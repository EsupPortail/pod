# -*- coding: utf-8 -*-
"""
Copyright (C) 2014 Nicolas Can
Ce programme est un logiciel libre : vous pouvez
le redistribuer et/ou le modifier sous les termes
de la licence GNU Public Licence telle que publiée
par la Free Software Foundation, soit dans la
version 3 de la licence, ou (selon votre choix)
toute version ultérieure.
Ce programme est distribué avec l'espoir
qu'il sera utile, mais SANS AUCUNE
GARANTIE : sans même les garanties
implicites de VALEUR MARCHANDE ou
D'APPLICABILITÉ À UN BUT PRÉCIS. Voir
la licence GNU General Public License
pour plus de détails.
Vous devriez avoir reçu une copie de la licence
GNU General Public Licence
avec ce programme. Si ce n'est pas le cas,
voir http://www.gnu.org/licenses/
"""
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from modeltranslation.admin import TranslationAdmin
from pods.models import *


# Ordering user by username !
User._meta.ordering = ["username"]

def url_to_edit_object(obj):
    url = reverse(
        'admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name), args=[obj.id])
    return format_html('<a href="{}">{}</a>', url, obj.__unicode__())

# Categories admin panel
class ChannelAdmin(TranslationAdmin):
    def get_owners(self, obj):
        owners = []
        for owner in obj.owners.all():
            url = url_to_edit_object(owner)
            owners.append(u'%s %s (%s)' % (
                owner.first_name, owner.last_name, url))
        return ', '.join(owners)

    get_owners.allow_tags = True
    get_owners.short_description = _('Owners')

    list_display = ('title', 'get_owners', 'visible',)
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('owners', 'users',)
    list_editable = ('visible', )
    ordering = ('title',)
admin.site.register(Channel, ChannelAdmin)

class ThemeAdmin(admin.ModelAdmin):
    list_display = ('title', 'channel')
    list_filter = ['channel']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('channel', 'title')
admin.site.register(Theme, ThemeAdmin)

class TypeAdmin(TranslationAdmin):
    prepopulated_fields = {'slug': ('title',)}
admin.site.register(Type, TypeAdmin)

class DisciplineAdmin(TranslationAdmin):
    prepopulated_fields = {'slug': ('title',)}
admin.site.register(Discipline, DisciplineAdmin)


# Pod admin panel
# Inlines
class EncodingPodsInline(admin.TabularInline):
    model = EncodingPods
    extra = 0

class ContributorPodsInline(admin.TabularInline):
    model = ContributorPods
    extra = 0

class TrackPodsInline(admin.TabularInline):
    model = TrackPods
    extra = 0

class DocPodsInline(admin.TabularInline):
    model = DocPods
    extra = 0

class OverlayPodsInLine(admin.TabularInline):
    model = OverlayPods
    extra = 0

class ChapterPodsInline(admin.TabularInline):
    model = ChapterPods
    extra = 0

class EnrichPodsInline(admin.TabularInline):
    model = EnrichPods
    extra = 0

class PlaylistAdmin(admin.ModelAdmin):
    def get_owner_by_name(self, obj):
        owner = obj.owner
        url = url_to_edit_object(owner)
        return u'%s %s (%s)' % (owner.first_name, owner.last_name, url)

    get_owner_by_name.allow_tags = True
    get_owner_by_name.short_description = _('Owner')

    list_display = ('id', 'title', 'owner', 'visible')
    list_display_links = ('title',)
    list_editable = ('visible',)
    search_fields = ['id', 'title', 'owner__username', 'owner__first_name', 'owner__last_name']

admin.site.register(Playlist, PlaylistAdmin)

class PlaylistVideoAdmin(admin.ModelAdmin):
    list_display = ('video', 'playlist', 'position')
    list_display_links = ('video',)

admin.site.register(PlaylistVideo, PlaylistVideoAdmin)


# Pod admin panel
# Main
# Have search function by owner
class PodAdmin(admin.ModelAdmin):

    def get_owner_by_name(self, obj):
        owner = obj.owner
        url = url_to_edit_object(owner)
        return u'%s %s (%s)' % (owner.first_name, owner.last_name, url)

    get_owner_by_name.allow_tags = True
    get_owner_by_name.short_description = _('Owner')

    list_display = ('id', 'title', 'get_owner_by_name', 'type', 'date_added', 'view_count', 'is_draft', 'is_restricted',
                    'is_password', 'duration_in_time', 'encoding_in_progress', 'encoding_status', 'admin_thumbnail')
    list_display_links = ('id', 'title')
    list_filter = ('date_added', 'channel', 'type', 'is_draft')
    list_editable = ('is_draft', 'is_restricted')
    search_fields = ['id', 'title', 'description', 'video',
                     'owner__username', 'owner__first_name', 'owner__last_name']
    list_per_page = 20
    #prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('discipline', 'channel', 'theme',)
    readonly_fields = ('duration', 'infoVideo',
                       'encoding_in_progress', 'encoding_status')
    inlines = [
        EncodingPodsInline,
        ContributorPodsInline,
        TrackPodsInline,
        DocPodsInline,
        OverlayPodsInLine,
        ChapterPodsInline,
        EnrichPodsInline
    ]

    def is_password(self, obj):
        return bool(obj.password)
    is_password.boolean = True
    is_password.short_description = _('Password')

    actions = ['encode_video']

    def encode_video(self, request, queryset):
        for item in queryset:
            item.encoding_in_progress = False
            item.to_encode = True
            item.save()
    encode_video.short_description = _('Encode selected')
admin.site.register(Pod, PodAdmin)


# Encoding admin panel
class EncodingPodsAdmin(admin.ModelAdmin):
    list_display = ('video', 'encodingType', 'encodingFile', 'encodingFormat')
    list_display_links = ('video',)
    list_filter = ('encodingFormat', 'encodingType__output_height')
    list_editable = ('encodingFormat', )
admin.site.register(EncodingPods, EncodingPodsAdmin)


# Notes admin panel
# Have search function by id
class NotesAdmin(admin.ModelAdmin):
    list_display = ('id', 'video', 'user')
    list_display_links = ('video',)
    search_fields = ['id']
admin.site.register(Notes, NotesAdmin)


# Basic admin panel
admin.site.register(ContributorPods)
admin.site.register(TrackPods)
admin.site.register(DocPods)
admin.site.register(OverlayPods)
admin.site.register(ChapterPods)
admin.site.register(EnrichPods)


# Recorder admin panel
# Mediacourses
class MediacoursesAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'mediapath', 'started', 'date_added')
    list_display_links = ('title',)
    list_filter = ('user',)
    #list_editable = ('status', 'slide' )
admin.site.register(Mediacourses, MediacoursesAdmin)


# Basic admin panel
admin.site.register(Building)


# Recorder admin panel
# Main
class RecorderAdmin(admin.ModelAdmin):
    list_display = ('name', 'adress_ip', 'building',
                    'status', 'slide', 'is_restricted')
    list_display_links = ('name',)
    list_filter = ('building',)
    list_editable = ('status', 'slide', 'is_restricted')
admin.site.register(Recorder, RecorderAdmin)


# Report Video admin panel
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'video', 'comment', 'answer',
                    'date_added', 'get_iframe_url_to_video')
    list_filter = ('date_added',)
    list_display_links = ('id', 'user', 'video')
admin.site.register(ReportVideo, ReportAdmin)


# RSS Feed admin panel
class RssfeedAdmin(admin.ModelAdmin):
    def get_owner_by_name(self, obj):
        owner = obj.owner
        url = url_to_edit_object(owner)
        return u'%s %s (%s)' % (owner.first_name, owner.last_name, url)

    get_owner_by_name.allow_tags = True
    get_owner_by_name.short_description = _('Owner')

    list_display = ('title', 'type_rss', 'year', 'get_owner_by_name', 'is_up')
    list_filter = ('date_update', 'year', 'type_rss', 'is_up')
    list_editable = ('year', 'is_up')
    search_fields = ['title', 'description', 'link_rss',
                     'owner__username', 'owner__first_name', 'owner__last_name']
    list_per_page = 20
admin.site.register(Rssfeed, RssfeedAdmin)
