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
from django.utils.safestring import mark_safe
from itertools import chain
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from pods.models import Channel, Theme, Pod, ContributorPods, TrackPods, DocPods, ChapterPods, Favorites, Type, Discipline, Mediacourses, EnrichPods, Notes
from djangoformsetjs.utils import formset_media_js
from modeltranslation.forms import TranslationModelForm

class ChannelForm(TranslationModelForm):
  def __init__(self, *args, **kwargs):
    super(ChannelForm, self).__init__(*args, **kwargs)
    for myField in self.fields:
        if self.fields[myField].required:
            self.fields[myField].widget.attrs['class'] = 'required'
            label_unicode = u'%s' %self.fields[myField].label
            self.fields[myField].label = mark_safe("%s <span class=\"special_class\">*</span>" %label_unicode)
        
  class Meta:
    model = Channel
    exclude = ('title','slug', 'owner', 'users' )

class ThemeForm(ModelForm):
  def __init__(self, *args, **kwargs):
    super(ThemeForm, self).__init__(*args, **kwargs)
    for myField in self.fields:
        self.fields[myField].widget.attrs['placeholder'] = self.fields[myField].label
        if self.fields[myField].required:
            self.fields[myField].widget.attrs['class'] = 'required'
            label_unicode = u'%s' %self.fields[myField].label
            self.fields[myField].label = mark_safe("%s <span class=\"special_class\">*</span>" %label_unicode)
  class Meta:
    model = Theme
    #exclude = ('title','slug', 'owner', 'users' )
    fields = ['title', 'description', 'headband']
    widgets = {
        'description': forms.Textarea(attrs={'rows':3, 'cols':15}),
    }

class NotesForm(ModelForm):
  def __init__(self, *args, **kwargs):
    super(NotesForm, self).__init__(*args, **kwargs)
    for myField in self.fields:
        self.fields[myField].widget.attrs['placeholder'] = self.fields[myField].label
        if self.fields[myField].required:
            self.fields[myField].widget.attrs['class'] = 'required'
            label_unicode = u'%s' %self.fields[myField].label
            self.fields[myField].label = "" #mark_safe("%s <span class=\"special_class\">*</span>" %label_unicode)
  class Meta:
    model = Notes
    #exclude = ('title','slug', 'owner', 'users' )
    fields = ['note']
    widgets = {
        'note': forms.Textarea(attrs={'rows':5, 'cols':15, 'class':"form-control"}),
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
                raise ValidationError(_("Filetype not allowed! Filetypes allowed: ") + ', '.join(self.ext_whitelist))
        return data
    
class PodForm(ModelForm):
    date_evt = DateField(required=False, label=_(u'Date of the event'), widget=widgets.AdminDateWidget)
    video = ExtFileField(ext_whitelist=settings.VIDEO_EXT_ACCEPT, label=_(u'File'),)
    def __init__(self, request, *args, **kwargs):
        super(PodForm, self).__init__(*args, **kwargs)

        try :
            if not self.instance.owner.is_staff :
                del self.fields['thumbnail']
            if self.instance.encoding_in_progress:
                del self.fields['video']
        except:
        
            del self.fields['thumbnail']
            
        if not request.user.is_superuser:
            del self.fields['date_added']
            del self.fields['owner']
            user_channels = request.user.owner_channels.all() | request.user.users_channels.all()
            if user_channels:
                self.fields["channel"].queryset = user_channels
                list_theme = Theme.objects.filter(channel=user_channels).order_by('channel','title')
                self.fields["theme"].queryset = list_theme
            else:
                del self.fields['channel']
                del self.fields['theme']
            
        
        for myField in self.fields:
            self.fields[myField].widget.attrs['placeholder'] = self.fields[myField].label
            if self.fields[myField].required:
                self.fields[myField].widget.attrs['class'] = 'required'
                label_unicode = u'%s' %self.fields[myField].label
                self.fields[myField].label = mark_safe("%s <span class=\"special_class\">*</span>" %label_unicode)
        
        
    class Meta:
        model = Pod


class ContributorPodsForm(ModelForm):
    class Media(object):
        js = formset_media_js + (
            # Other form media here
        )
    def __init__(self, *args, **kwargs):
      super(ContributorPodsForm, self).__init__(*args, **kwargs)
      for myField in self.fields:
          self.fields[myField].widget.attrs['placeholder'] = self.fields[myField].label
          if self.fields[myField].required:
              self.fields[myField].widget.attrs['class'] = 'required'
              label_unicode = u'%s' %self.fields[myField].label
              self.fields[myField].label = mark_safe("%s <span class=\"special_class\">*</span>" %label_unicode)
    class Meta:
      model = ContributorPods

class TrackPodsForm(ModelForm):
    class Media(object):
        js = formset_media_js + (
            # Other form media here
        )
    def __init__(self, *args, **kwargs):
      super(TrackPodsForm, self).__init__(*args, **kwargs)
      for myField in self.fields:
          self.fields[myField].widget.attrs['placeholder'] = self.fields[myField].label
          if self.fields[myField].required:
              self.fields[myField].widget.attrs['class'] = 'required'
              label_unicode = u'%s' %self.fields[myField].label
              self.fields[myField].label = mark_safe("%s <span class=\"special_class\">*</span>" %label_unicode)
    class Meta:
      model = TrackPods

class DocPodsForm(ModelForm):
    class Media(object):
        js = formset_media_js + (
            # Other form media here
        )
    def __init__(self, *args, **kwargs):
      super(DocPodsForm, self).__init__(*args, **kwargs)
      for myField in self.fields:
          self.fields[myField].widget.attrs['placeholder'] = self.fields[myField].label
          if self.fields[myField].required:
              self.fields[myField].widget.attrs['class'] = 'required'
              label_unicode = u'%s' %self.fields[myField].label
              self.fields[myField].label = mark_safe("%s <span class=\"special_class\">*</span>" %label_unicode)
    class Meta:
      model = DocPods

    
class ChapterPodsForm(ModelForm):
    class Media(object):
        js = formset_media_js + (
            # Other form media here
        )
        #min="1" max="5"
    def __init__(self, *args, **kwargs):
      super(ChapterPodsForm, self).__init__(*args, **kwargs)
      for myField in self.fields:
          try:
            self.fields[myField].widget.attrs['min'] = 0
            self.fields[myField].widget.attrs['max'] = self.instance.video.duration
          except:
            self.fields[myField].widget.attrs['min'] = 0
            self.fields[myField].widget.attrs['max'] = 360000
            
          self.fields[myField].widget.attrs['placeholder'] = self.fields[myField].label
          if self.fields[myField].required:
              self.fields[myField].widget.attrs['class'] = 'required'
              label_unicode = u'%s' %self.fields[myField].label
              self.fields[myField].label = mark_safe("%s <span class=\"special_class\">*</span>" %label_unicode)
    class Meta:
      model = ChapterPods   

    
class EnrichPodsForm(ModelForm):
    class Media(object):
        js = formset_media_js + (
            # Other form media here
        )
        #min="1" max="5"
    def __init__(self, *args, **kwargs):
      super(EnrichPodsForm, self).__init__(*args, **kwargs)
      for myField in self.fields:
          try:
            self.fields[myField].widget.attrs['min'] = 0
            self.fields[myField].widget.attrs['max'] = self.instance.video.duration
          except:
            self.fields[myField].widget.attrs['min'] = 0
            self.fields[myField].widget.attrs['max'] = 360000
            
          self.fields[myField].widget.attrs['placeholder'] = self.fields[myField].label
          if self.fields[myField].required:
              self.fields[myField].widget.attrs['class'] = 'required'
              label_unicode = u'%s' %self.fields[myField].label
              self.fields[myField].label = mark_safe("%s <span class=\"special_class\">*</span>" %label_unicode)
    class Meta:
      model = EnrichPods
      exclude = ('video',)   
    
class VideoPasswordForm(Form):
    password = CharField(label=_(u'Password'), widget=PasswordInput())
    
    def __init__(self, *args, **kwargs):
      super(VideoPasswordForm, self).__init__(*args, **kwargs)
      for myField in self.fields:
          self.fields[myField].widget.attrs['placeholder'] = self.fields[myField].label
          if self.fields[myField].required:
              self.fields[myField].widget.attrs['class'] = 'required'
              label_unicode = u'%s' %self.fields[myField].label
              self.fields[myField].label = mark_safe("%s <span class=\"special_class\">*</span>" %label_unicode)


from haystack.forms import SearchForm, FacetedSearchForm
from haystack.query import SearchQuerySet
import time, datetime

class DateRangeSearchForm(FacetedSearchForm):
    start_date = forms.DateField(required=False, label=u'Date de début', widget=widgets.AdminDateWidget)
    end_date = forms.DateField(required=False, label=u'Date de fin', widget=widgets.AdminDateWidget)
    
    #type=forms.ModelMultipleChoiceField(required=False, queryset=Type.objects.all())
    #discipline=forms.ModelMultipleChoiceField(required=False, queryset=Discipline.objects.all())
    #channel=forms.ModelMultipleChoiceField(required=False, queryset=Channel.objects.all())
    def search(self):
        # First, store the SearchQuerySet received from other processing.
        sqs = super(DateRangeSearchForm, self).search()

        if not self.is_valid():
            return self.no_query_found()
        
        if self.cleaned_data['start_date']:    
                sqs = sqs.filter(date_added__gte=self.cleaned_data['start_date'])
    
        # Check to see if an end_date was chosen.
        if self.cleaned_data['end_date']:
            timestring = "%s 23:59:59" %self.cleaned_data['end_date']
            time_format = "%Y-%m-%d %H:%M:%S"
            midnight = datetime.datetime.fromtimestamp(time.mktime(time.strptime(timestring, time_format)))
            #print "END DATE : %s" %midnight
            sqs = sqs.filter(date_added__lte=midnight)
            
        return sqs
            
    """
    def search(self):
        # First, store the SearchQuerySet received from other processing.
        #sqs = super(DateRangeSearchForm, self).search()
        sqs = SearchQuerySet().facet('owner').facet('type').facet('tags').facet('discipline').facet('channel')
        if self.is_valid():
            
            sqs = sqs.filter(text_ngram=self.cleaned_data['q'])
            #sqs = sqs.autocomplete(text=self.cleaned_data['q']) 
            if not sqs:
                sqs = super(DateRangeSearchForm, self).search()

            # Check to see if a start_date was chosen.
            if self.cleaned_data['start_date']:    
                sqs = sqs.filter(date_added__gte=self.cleaned_data['start_date'])
    
            # Check to see if an end_date was chosen.
            if self.cleaned_data['end_date']:
                timestring = "%s 23:59:59" %self.cleaned_data['end_date']
                time_format = "%Y-%m-%d %H:%M:%S"
                midnight = datetime.datetime.fromtimestamp(time.mktime(time.strptime(timestring, time_format)))
                #print "END DATE : %s" %midnight
                sqs = sqs.filter(date_added__lte=midnight)
            
            if self.cleaned_data['type']:
                listid=[]
                for type in self.cleaned_data['type']:
                    listid.append(type.id)
                sqs = sqs.filter(type__in=listid)
            
            if self.cleaned_data['discipline']:
                listid=[]
                for disc in self.cleaned_data['discipline']:
                    listid.append(disc.id)
                sqs = sqs.filter(discipline__in=listid)
            
            if self.cleaned_data['channel']:
                listid=[]
                for channel in self.cleaned_data['channel']:
                    listid.append(channel.id)
                sqs = sqs.filter(channel__in=listid)

        return sqs
    """
    

#class formMediacours(forms.Form):
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
            self.fields[myField].widget.attrs['placeholder'] = self.fields[myField].label
            if self.fields[myField].required:
                self.fields[myField].widget.attrs['class'] = 'required'
                label_unicode = u'%s' %self.fields[myField].label
                self.fields[myField].label = mark_safe("%s <span class=\"special_class\">*</span>" %label_unicode)
        
    class Meta:
        model = Mediacourses
        exclude = ('started','error')