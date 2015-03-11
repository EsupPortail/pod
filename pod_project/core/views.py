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

from __future__ import unicode_literals

from django.shortcuts import render
from core.forms import FileBrowseForm, ProfileForm
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.template import RequestContext

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login

from django.utils.http import urlquote

from django.conf import settings
import sys

import logging
logger = logging.getLogger(__name__)

def file_browse(request):
    form = FileBrowseForm() # A empty, unbound form
    fic=None
    get_CKEditorFuncNum = None
    if request.GET.get('CKEditorFuncNum') :
        get_CKEditorFuncNum = "%s" %request.GET['CKEditorFuncNum']
    if request.method == 'POST':
        form = FileBrowseForm(request.POST)
        if form.is_valid():
            fic = form.cleaned_data['document']
    return render_to_response("fileBrowse.html",
                          {'form':form, 'fic':fic, 'get_CKEditorFuncNum':get_CKEditorFuncNum},
                          context_instance=RequestContext(request))
@csrf_protect
def core_login(request):
    #on determine la page ou renvoyer l'utilisateur
    next = request.GET['next'] if request.GET.get('next') else request.POST['next'] if request.POST.get('next') else request.META['HTTP_REFERER'] if request.META.get('HTTP_REFERER') else "/"
    
    if settings.USE_CAS and not request.GET.get("gateway") and not request.POST:
        if request.GET.get("is_iframe"):
            return HttpResponseRedirect(reverse('cas_login')+'?gateway=True&next=%s&is_iframe=true'%urlquote(next))
        else:
            return HttpResponseRedirect(reverse('cas_login')+'?gateway=True&next=%s'%urlquote(next))
        
    if request.user.is_authenticated == True:
        return HttpResponseRedirect(next) # Redirect to a success page.
        
    form = AuthenticationForm()
    #placeholder
    from django import forms
    form.fields['username'].widget=forms.TextInput(attrs={'placeholder':_('Login')})
    form.fields['password'].widget=forms.PasswordInput(attrs={'placeholder':_('Password')})
    
    if request.POST and request.POST['username'] and request.POST['password']:
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                try:
                    user.userprofile.auth_type="loc"
                    user.userprofile.save()
                except:
                    msg = u'\n*****Unexpected error link :%s - %s' %(sys.exc_info()[0], sys.exc_info()[1])
                    logger.error(msg)
                # Redirect to a success page.
                return HttpResponseRedirect(next)
            else:
                # Return a 'disabled account' error message
                msg = u'%s' %_(u'Your account is disabled, please contact the administrator of the platform')
                messages.add_message(request, messages.ERROR, msg)
        else:
            # Return an 'invalid login' error message.
            msg = u'%s' %_(u'Unable to connect, please check the information otherwise contact the platform administrator')
            messages.add_message(request, messages.ERROR, msg)
            
    return render_to_response("registration/login.html",
                          {'form':form, 'next':next, "USE_CAS": settings.USE_CAS},
                          context_instance=RequestContext(request))

def core_logout(request):
    logout(request)
    if settings.USE_CAS :
        return HttpResponseRedirect(reverse('cas_logout'))
    else:
        return HttpResponseRedirect("/")
                          
@csrf_protect
@login_required
def user_profile(request):
    try:
        profile_form = ProfileForm(instance=request.user.userprofile)
    except:
        profile_form = ProfileForm()
        
    if request.POST:
        try:
            profile_form = ProfileForm(request.POST,instance=request.user.userprofile)
        except:
            profile_form = ProfileForm(request.POST)
            
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.add_message(request, messages.INFO, _(u'Your profile is saved'))
        else:
            messages.add_message(request, messages.ERROR, _(u'Error in the form'))
        
          
    return render_to_response("userProfile.html",
                          {'form':profile_form, },
                          context_instance=RequestContext(request))
          