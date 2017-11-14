# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, date
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.utils import formats
from django.views.decorators.csrf import csrf_protect
from pods.forms import MediacoursesForm

# MEDIACOURSES

@csrf_protect
@login_required
@staff_member_required
def mediacourses(request):
    mediapath = request.GET.get('mediapath')
    if not mediapath and not request.user.is_superuser:
        messages.add_message(
            request, messages.ERROR, _(u'Mediapath should be indicated.'))
        raise PermissionDenied

    form = MediacoursesForm(request, initial={'mediapath': mediapath})
    if request.GET.get('course_title'):
        course_title = request.GET.get('course_title')
        form = MediacoursesForm(
            request, initial={'mediapath': mediapath, 'title': course_title})

    if request.method == 'POST':  # If the form has been submitted...
        # A form bound to the POST data
        form = MediacoursesForm(request, request.POST)
        if form.is_valid():  # All validation rules pass
            med = form.save(commit=False)
            if request.POST.get('user') and request.POST.get('user') != "":
                med.user = form.cleaned_data['user']
            else:
                med.user = request.user
            if request.POST.get('mediapath') and request.POST.get('mediapath') != "":
                med.mediapath = form.cleaned_data['mediapath']
            else:
                med.mediapath = mediapath
            med.save()
            message = _(
                'Your publication is saved. Adding it to your videos will be in a few minutes.')
            messages.add_message(request, messages.INFO, message)
            return HttpResponseRedirect(reverse('pods.views.owner_videos_list'))
        else:
            message = _('One or more errors have been found in the form.')
            messages.add_message(request, messages.ERROR, message)

    return render_to_response("mediacourses/mediacourses_add.html",
                              {"form": form},
                              context_instance=RequestContext(request))

def mediacourses_notify(request):  # post mediacourses notification
    # http://URL/mediacourses_notify/?recordingPlace=192_168_1_10&mediapath=file.zip&key=77fac92a3f06d50228116898187e50e5
    if request.GET.get("recordingPlace") and request.GET.get('mediapath') and request.GET.get('key'):
        m = hashlib.md5()
        m.update(request.GET.get("recordingPlace") + settings.RECORDER_SALT)
        if request.GET.get('key') != m.hexdigest():
            # messages.add_message(
            #    request, messages.ERROR, _(u'You cannot notify a mediacourse'))
            #raise PermissionDenied
            return HttpResponse("nok : key is not valid")

        recorder = get_object_or_404(
            Recorder, adress_ip=request.GET.get("recordingPlace").replace("_", "."))
        date_notify = datetime.now()
        formatted_date_notify = formats.date_format(
            date_notify, "SHORT_DATE_FORMAT")
        link_url = ''.join([request.build_absolute_uri(reverse('mediacourses')), "?mediapath=", request.GET.get(
            'mediapath'), "&course_title=%s" % _("Recording"), " %s" % formatted_date_notify.replace("/", "-")])

        text_msg = _("Hello, \n\na new mediacourse has just be added on the video website \"%(title_site)s\" from the recorder \"%(recorder)s\"."
                     "\nTo add it, just click on link below.\n\n%(link_url)s\nif you cannot click on link, just copy-paste it in your browser."
                     "\n\nRegards") % {'title_site': settings.TITLE_SITE, 'recorder': recorder.name, 'link_url': link_url}

        html_msg = _("Hello, <p>a new mediacourse has just be added on %(title_site)s from the recorder \"%(recorder)s\"."
                     "<br/>To add it, just click on link below.</p><a href=\"%(link_url)s\">%(link_url)s</a><br/><i>if you cannot click on link, just copy-paste it in your browser.</i>"
                     "<p><p>Regards</p>") % {'title_site': settings.TITLE_SITE, 'recorder': recorder.name, 'link_url': link_url}

        admin_emails = User.objects.filter(
            is_superuser=True).values_list('email', flat=True)
        subject = "[" + settings.TITLE_SITE + \
            "] %s" % _('New mediacourse added.')

        email_msg = EmailMultiAlternatives(
            subject, text_msg, settings.DEFAULT_FROM_EMAIL, admin_emails)

        email_msg.attach_alternative(html_msg, "text/html")
        email_msg.send(fail_silently=False)

        return HttpResponse("ok")
    else:
        return HttpResponse("nok : recordingPlace or mediapath or key are missing")