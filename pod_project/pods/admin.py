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
from pods.models import *
from django import forms
from django.utils.translation import ugettext as _
from django.contrib.admin import widgets

from django.contrib.auth.models import User
#Ordering user by username !   
User._meta.ordering=["username"]

from modeltranslation.admin import TranslationAdmin

class ChannelAdmin(TranslationAdmin):
    list_display = ('title','visible',)
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('users',)
    list_editable = ('visible', )
admin.site.register(Channel, ChannelAdmin)

class ThemeAdmin(admin.ModelAdmin):
    list_display = ('title', 'channel')
    list_filter = ['channel']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('channel','title')
admin.site.register(Theme, ThemeAdmin)

class TypeAdmin(TranslationAdmin):
    prepopulated_fields = {'slug': ('title',)}
admin.site.register(Type, TypeAdmin)

class DisciplineAdmin(TranslationAdmin):
    prepopulated_fields = {'slug': ('title',)}
admin.site.register(Discipline, DisciplineAdmin)

class EncodingPodsInline(admin.TabularInline):
    model = EncodingPods
class ContributorPodsInline(admin.TabularInline):
    model = ContributorPods
class TrackPodsInline(admin.TabularInline):
    model = TrackPods
class DocPodsInline(admin.TabularInline):
    model = DocPods
class ChapterPodsInline(admin.TabularInline):
    model = ChapterPods
class EnrichPodsInline(admin.TabularInline):
    model = EnrichPods


class PodAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'owner', 'type', 'date_added', 'view_count', 'is_draft', 'duration_in_time', 'encoding_in_progress', 'encoding_status', 'admin_thumbnail')
    list_display_links = ('id', 'title')
    list_filter = ('date_added', 'channel', 'type', 'is_draft')
    list_editable = ('is_draft', )
    search_fields = ['id', 'title', 'description', 'video', 'owner__username', 'owner__first_name', 'owner__last_name']
    list_per_page = 20
    #prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('discipline','channel','theme',)
    readonly_fields=('duration', 'infoVideo', 'encoding_in_progress', 'encoding_status')
    inlines = [
        EncodingPodsInline,
        ContributorPodsInline,
        TrackPodsInline,
        DocPodsInline,
        ChapterPodsInline,
        EnrichPodsInline
    ]
    actions = ['encode_video']
    def encode_video(self, request, queryset):
        for item in queryset:
            item.encoding_in_progress=False
            item.to_encode=True
            item.save()
    encode_video.short_description = "encode"
    
    
admin.site.register(Pod, PodAdmin)

class EncodingPodsAdmin(admin.ModelAdmin):
    list_display = ('video', 'encodingType', 'encodingFile', 'encodingFormat')
    list_display_links = ('video',)
    list_filter = ('encodingFormat', 'encodingType__output_height')
    list_editable = ('encodingFormat', )

admin.site.register(EncodingPods, EncodingPodsAdmin)

admin.site.register(ContributorPods)
admin.site.register(TrackPods)
admin.site.register(DocPods)
admin.site.register(ChapterPods)
admin.site.register(EnrichPods)
admin.site.register(Notes)

#recorder
admin.site.register(Mediacourses)
admin.site.register(Building)
admin.site.register(Recorder)


#Report Video
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'video', 'comment', 'answer', 'date_added', 'get_iframe_url_to_video')
    list_filter = ('date_added',)
    list_display_links = ('id','user','video')
admin.site.register(ReportVideo, ReportAdmin)

#AdditionRequestVideo
class Contact_usAdmin(admin.ModelAdmin):
    list_display = ('id','subject', 'comment', 'answer', 'date_added')
    list_filter = ('date_added',)
    list_display_links = ('id',)
admin.site.register(Contact_us, Contact_usAdmin)
