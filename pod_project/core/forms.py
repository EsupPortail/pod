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

from django.forms import ModelForm
from core.models import FileBrowse, UserProfile, ContactUs
from captcha.fields import CaptchaField

class FileBrowseForm(ModelForm):
    class Meta:
        model = FileBrowse
        fields = '__all__'

class ProfileForm(ModelForm):
  def __init__(self, *args, **kwargs):
    super(ProfileForm, self).__init__(*args, **kwargs)
    try :
        if not self.instance.user.is_staff and not self.instance.user.is_superuser:
            del self.fields['image']
    except:
        del self.fields['image']
    for myField in self.fields:
        self.fields[myField].widget.attrs['placeholder'] = self.fields[myField].label
        if self.fields[myField].required:
            self.fields[myField].widget.attrs['class'] = 'required'
            label_unicode = u'%s' %self.fields[myField].label
            self.fields[myField].label = mark_safe("%s <span class=\"special_class\">*</span>" %label_unicode)
        
  class Meta:
    model = UserProfile
    exclude = ('user','auth_type', 'commentaire', 'affiliation' )

class ContactUsModelForm(ModelForm):
    captcha = CaptchaField()
    class Meta:
        model = ContactUs