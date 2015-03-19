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
from django.contrib.flatpages.admin import FlatpageForm, FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from ckeditor.widgets import CKEditorWidget
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from core.models import UserProfile, PagesMenuBas, EncodingType


class PageForm(FlatpageForm):

    class Meta:
        model = FlatPage
        widgets = {
            'content_fr': CKEditorWidget(config_name='complete'),
            'content_en': CKEditorWidget(config_name='complete'),
        }

from modeltranslation.admin import TranslationAdmin


class CustomFlatPageAdmin(TranslationAdmin):
    list_display = ('title', 'url', )
    form = PageForm

# unregister the default FlatPage admin and register CustomFlatPageAdmin.
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, CustomFlatPageAdmin)


admin.site.register(PagesMenuBas)

# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profiles'

# Define a new User admin


class UserAdmin(UserAdmin):
    inlines = (UserProfileInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class EncodingTypeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'bitrate_audio', 'bitrate_video', 'output_height', 'mediatype')
admin.site.register(EncodingType, EncodingTypeAdmin)
