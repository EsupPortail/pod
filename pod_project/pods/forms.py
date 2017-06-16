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
import os
from django import forms
from django.forms import ModelForm, DateField, ValidationError, FileField, CharField, Form, PasswordInput
from django.contrib.admin import widgets
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from itertools import chain
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from pods.models import Channel, Theme, Pod, ContributorPods, TrackPods, DocPods, ChapterPods, Favorites, Type, Discipline, Mediacourses, EnrichPods, Notes
from modeltranslation.forms import TranslationModelForm
from django.forms.widgets import HiddenInput

ALLOW_VISIBILITY_SETTING_TO_CHANNEL_OWNERS = getattr(
    settings, 'ALLOW_VISIBILITY_SETTING_TO_CHANNEL_OWNERS', True)

SHOW_IS_360_IN_FORM_UPLOAD = getattr(
    settings, 'SHOW_IS_360_IN_FORM_UPLOAD', False)


class ChannelForm(TranslationModelForm):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ChannelForm, self).__init__(*args, **kwargs)
        try:
            if not user.is_staff:
                del self.fields['headband']
                del self.fields['users']
            else:
                self.fields['users'].queryset = User.objects.exclude(
                    id=user.id)
                self.fields['users'].label_from_instance = lambda obj: "%s %s (%s)" % (
                    obj.first_name, obj.last_name, obj.username)
        except:
            del self.fields['headband']
            del self.fields['users']
        for myField in self.fields:
            if self.fields[myField].required:
                self.fields[myField].widget.attrs['class'] = 'required'
                label_unicode = u'%s' % self.fields[myField].label
                self.fields[myField].label = mark_safe(
                    "%s <span class=\"special_class\">*</span>" % label_unicode)

    class Meta:
        model = Channel
        if ALLOW_VISIBILITY_SETTING_TO_CHANNEL_OWNERS:
            exclude = ('title', 'slug', 'owners')
        else:
            exclude = ('title', 'slug', 'owners', 'visible')


class ThemeForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ThemeForm, self).__init__(*args, **kwargs)
        for myField in self.fields:
            self.fields[myField].widget.attrs[
                'placeholder'] = self.fields[myField].label
            if self.fields[myField].required:
                self.fields[myField].widget.attrs['class'] = 'required'
                label_unicode = u'%s' % self.fields[myField].label
                self.fields[myField].label = mark_safe(
                    "%s <span class=\"special_class\">*</span>" % label_unicode)

    class Meta:
        model = Theme
        #exclude = ('title','slug', 'owner', 'users' )
        fields = ['title', 'description', 'headband']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'cols': 15}),
        }


class NotesForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(NotesForm, self).__init__(*args, **kwargs)
        for myField in self.fields:
            self.fields[myField].widget.attrs[
                'placeholder'] = self.fields[myField].label
            if self.fields[myField].required:
                self.fields[myField].widget.attrs['class'] = 'required'
                label_unicode = u'%s' % self.fields[myField].label
                # mark_safe("%s <span class=\"special_class\">*</span>" %label_unicode)
                self.fields[myField].label = ""

    class Meta:
        model = Notes
        #exclude = ('title','slug', 'owner', 'users' )
        fields = ['note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 5, 'cols': 15, 'class': "form-control"}),
        }


class ExtFileField(FileField):

    """
    Find : https://djangosnippets.org/snippets/977/
    Same as forms.FileField, but you can specify a file extension whitelist.

    >>> from django.core.files.uploadedfile import SimpleUploadedFile
    >>>
    >>> t = ExtFileField(ext_whitelist=(".pdf", ".txt"))
    >>>
    >>> t.clean(SimpleUploadedFile('filename.pdf', 'Some File Content'))
    >>> t.clean(SimpleUploadedFile('filename.txt', 'Some File Content'))
    >>>
    >>> t.clean(SimpleUploadedFile('filename.exe', 'Some File Content'))
    Traceback (most recent call last):
    ...
    ValidationError: [u'Not allowed filetype!']
    """

    def __init__(self, *args, **kwargs):
        ext_whitelist = kwargs.pop("ext_whitelist")
        self.ext_whitelist = [i.lower() for i in ext_whitelist]

        super(ExtFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(ExtFileField, self).clean(*args, **kwargs)
        if data:
            filename = data.name
            ext = os.path.splitext(filename)[1]
            ext = ext.lower()
            if ext not in self.ext_whitelist:
                raise ValidationError(
                    _("Filetype not allowed! Filetypes allowed: ") + ', '.join(self.ext_whitelist))
        return data


class PodForm(ModelForm):
    date_evt = DateField(
        required=False, label=_(u'Date of the event'), widget=widgets.AdminDateWidget)
    video = ExtFileField(
        ext_whitelist=settings.VIDEO_EXT_ACCEPT, label=_(u'File'),)

    def __init__(self, request, *args, **kwargs):
        super(PodForm, self).__init__(*args, **kwargs)

        try:
            if not self.instance.owner.is_staff:
                del self.fields['thumbnail']
            if self.instance.encoding_in_progress:
                del self.fields['video']
        except:

            del self.fields['thumbnail']

        if not request.user.is_superuser:
            del self.fields['date_added']
            del self.fields['owner']
            user_channels = (request.user.owners_channels.all(
            ) | request.user.users_channels.all()).distinct()
            if user_channels:
                self.fields["channel"].queryset = user_channels
                list_theme = Theme.objects.filter(
                    channel=user_channels).order_by('channel', 'title')
                self.fields["theme"].queryset = list_theme
            else:
                del self.fields['channel']
                del self.fields['theme']

        for myField in self.fields:
            self.fields[myField].widget.attrs[
                'placeholder'] = self.fields[myField].label
            if self.fields[myField].required:
                self.fields[myField].widget.attrs['class'] = 'required'
                label_unicode = u'%s' % self.fields[myField].label
                self.fields[myField].label = mark_safe(
                    "%s <span class=\"special_class\">*</span>" % label_unicode)

    class Meta:
        model = Pod
        if SHOW_IS_360_IN_FORM_UPLOAD:
            fields = '__all__'
        else:
            exclude = ('is_360', )


class ContributorPodsForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ContributorPodsForm, self).__init__(*args, **kwargs)
        for myField in self.fields:
            self.fields['video'].widget = HiddenInput()
            self.fields[myField].widget.attrs[
                'placeholder'] = self.fields[myField].label
            if self.fields[myField].required:
                self.fields[myField].widget.attrs['class'] = 'required'
                label_unicode = u'%s' % self.fields[myField].label
                self.fields[myField].label = mark_safe(
                    "%s <span class=\"special_class\">*</span>" % label_unicode)

    class Meta:
        model = ContributorPods
        fields = '__all__'


class TrackPodsForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(TrackPodsForm, self).__init__(*args, **kwargs)
        for myField in self.fields:
            self.fields['video'].widget = HiddenInput()
            self.fields[myField].widget.attrs[
                'placeholder'] = self.fields[myField].label
            if self.fields[myField].required or myField == 'src':
                self.fields[myField].widget.attrs['class'] = 'required'
                label_unicode = u'%s' % self.fields[myField].label
                self.fields[myField].label = mark_safe(
                    "%s <span class=\"special_class\">*</span> : " % label_unicode)

    class Meta:
        model = TrackPods
        fields = '__all__'


class DocPodsForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(DocPodsForm, self).__init__(*args, **kwargs)
        for myField in self.fields:
            self.fields['video'].widget = HiddenInput()
            self.fields[myField].widget.attrs[
                'placeholder'] = self.fields[myField].label
            if self.fields[myField].required:
                self.fields[myField].widget.attrs['class'] = 'required'
                label_unicode = u'%s' % self.fields[myField].label
                self.fields[myField].label = mark_safe(
                    "%s <span class=\"special_class\">*</span>" % label_unicode)

    class Meta:
        model = DocPods
        fields = '__all__'


class ChapterPodsForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ChapterPodsForm, self).__init__(*args, **kwargs)
        self.fields['video'].widget = HiddenInput()
        self.fields['time'].widget.attrs['min'] = 0

        try:
            self.fields['time'].widget.attrs[
                'max'] = self.instance.video.duration - 1
        except:
            self.fields['time'].widget.attrs['max'] = 36000
        for myField in self.fields:
            self.fields[myField].widget.attrs[
                'placeholder'] = self.fields[myField].label
            if self.fields[myField].required:
                self.fields[myField].widget.attrs['class'] = 'required'
                label_unicode = u'%s' % self.fields[myField].label
                self.fields[myField].label = mark_safe(
                    "%s <span class=\"special_class\">*</span>" % label_unicode)

    class Meta:
        model = ChapterPods
        fields = '__all__'


class EnrichPodsForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(EnrichPodsForm, self).__init__(*args, **kwargs)
        self.fields['video'].widget = HiddenInput()
        self.fields['start'].widget.attrs['min'] = 0
        self.fields['end'].widget.attrs['min'] = 1
        try:
            self.fields['start'].widget.attrs[
                'max'] = self.instance.video.duration
            self.fields['end'].widget.attrs[
                'max'] = self.instance.video.duration
        except:
            self.fields['start'].widget.attrs['max'] = 36000
            self.fields['end'].widget.attrs['max'] = 36000

        for myField in self.fields:
            self.fields[myField].widget.attrs[
                'placeholder'] = self.fields[myField].label
            if self.fields[myField].required or myField == "type":
                self.fields[myField].widget.attrs['class'] = 'required'
                label_unicode = u'%s' % self.fields[myField].label
                self.fields[myField].label = mark_safe(
                    "%s <span class=\"special_class\">*</span>" % label_unicode)

    class Meta:
        model = EnrichPods
        fields = '__all__'


class VideoPasswordForm(Form):
    password = CharField(label=_(u'Password'), widget=PasswordInput())

    def __init__(self, *args, **kwargs):
        super(VideoPasswordForm, self).__init__(*args, **kwargs)
        for myField in self.fields:
            self.fields[myField].widget.attrs[
                'placeholder'] = self.fields[myField].label
            if self.fields[myField].required:
                self.fields[myField].widget.attrs['class'] = 'required'
                label_unicode = u'%s' % self.fields[myField].label
                self.fields[myField].label = mark_safe(
                    "%s <span class=\"special_class\">*</span>" % label_unicode)


class SearchForm(Form):
    q = forms.CharField(required=False, label=_('Search'),
                        widget=forms.TextInput(attrs={'type': 'search'}))
    start_date = forms.DateField(
        required=False, label=u'Start date', widget=widgets.AdminDateWidget)
    end_date = forms.DateField(
        required=False, label=u'End date', widget=widgets.AdminDateWidget)

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)

        for myField in self.fields:
            self.fields[myField].widget.attrs[
                'placeholder'] = self.fields[myField].label
            if self.fields[myField].required:
                self.fields[myField].widget.attrs['class'] = 'required'
                label_unicode = u'%s' % self.fields[myField].label
                self.fields[myField].label = mark_safe(
                    "%s <span class=\"special_class\">*</span>" % label_unicode)
# class formMediacours(forms.Form):
#    titre = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'size':'35', 'class':'required'}), required=True, label=(u'Titre '))
#    mediapath = forms.CharField(required=False, widget=forms.HiddenInput())


class MediacoursesForm(ModelForm):
    #mediapath = forms.CharField(required=True, widget=forms.HiddenInput())

    def __init__(self, request, *args, **kwargs):
        super(MediacoursesForm, self).__init__(*args, **kwargs)

        if not request.user.is_superuser:
            #del self.fields['date_added']
            del self.fields['user']
            del self.fields['mediapath']

        for myField in self.fields:
            self.fields[myField].widget.attrs[
                'placeholder'] = self.fields[myField].label
            if self.fields[myField].required:
                self.fields[myField].widget.attrs['class'] = 'required'
                label_unicode = u'%s' % self.fields[myField].label
                self.fields[myField].label = mark_safe(
                    "%s <span class=\"special_class\">*</span>" % label_unicode)

    class Meta:
        model = Mediacourses
        exclude = ('started', 'error')
