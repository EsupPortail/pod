# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.forms.models import inlineformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from paginations import get_pagination
from pods.forms import ChannelForm, ThemeForm
from pods.models import Channel, Pod, Theme
from string import replace

import simplejson as json

H5P_ENABLED = getattr(settings, 'H5P_ENABLED', False)
if H5P_ENABLED:
    from h5pp.models import h5p_contents, h5p_libraries
    from h5pp.h5p.h5pmodule import getUserScore, h5pGetContentId

DEFAULT_PER_PAGE = 12
VIDEOS = Pod.objects.filter(is_draft=False, encodingpods__gt=0).distinct()

referer = ''

# CHANNELS

@login_required
def owner_channels_list(request):
    channels_list = request.user.owners_channels.all().annotate(
        video_count=Count("pod", distinct=True))
    per_page = request.COOKIES.get('perpage') if request.COOKIES.get(
        'perpage') and request.COOKIES.get('perpage').isdigit() else DEFAULT_PER_PAGE
    paginator = Paginator(channels_list, per_page)
    page = request.GET.get('page')

    channels = get_pagination(page, paginator)

    if request.is_ajax():
        some_data_to_dump = {
            'json_videols': render_to_string("channels/channels_list.html",
                                             {"channels": channels},
                                             context_instance=RequestContext(request)),
            'json_toolbar': render_to_string("maintoolbar.html",
                                             {"channels": channels})
        }
        data = json.dumps(some_data_to_dump)
        return HttpResponse(data, content_type='application/json')

    return render_to_response("channels/my_channels.html",
                              {"channels": channels, "video_count": VIDEOS.filter(
                                  channel__in=list(channels_list)).count()},
                              context_instance=RequestContext(request))


def channels(request):
    channels_list = Channel.objects.filter(
        visible=True, pod__is_draft=False, pod__encodingpods__gt=0
    ).distinct().annotate(video_count=Count("pod", distinct=True))

    per_page = request.COOKIES.get('perpage') if request.COOKIES.get(
        'perpage') and request.COOKIES.get('perpage').isdigit() else DEFAULT_PER_PAGE
    paginator = Paginator(channels_list, per_page)
    page = request.GET.get('page')

    channels = get_pagination(page, paginator)

    if request.is_ajax():
        some_data_to_dump = {
            'json_videols': render_to_string("channels/channels_list.html",
                                             {"channels": channels},
                                             context_instance=RequestContext(request)),
            'json_toolbar': render_to_string("maintoolbar.html",
                                             {"channels": channels})
        }
        data = json.dumps(some_data_to_dump)
        return HttpResponse(data, content_type='application/json')

    return render_to_response("channels/channels.html",
                              {"channels": channels, "video_count": VIDEOS.filter(
                                  channel__in=list(channels_list)).count()},
                              context_instance=RequestContext(request))


def channel(request, slug_c, slug_t=None):
    channel = get_object_or_404(Channel, slug=slug_c)
    theme = None

    videos_list = VIDEOS.filter(channel=channel)

    param = "channel=%s" % (slug_c,)

    if slug_t:
        theme = get_object_or_404(Theme, slug=slug_t)
        videos_list = videos_list.filter(theme=theme)
        param = "channel=%s&theme=%s" % (slug_c, slug_t.encode('utf8'))

    order_by = request.COOKIES.get('orderby') if request.COOKIES.get(
        'orderby') else "order_by_-date_added"
    videos_list = videos_list.order_by(
        "%s" % replace(order_by, "order_by_", ""))

    per_page = request.COOKIES.get('perpage') if request.COOKIES.get(
        'perpage') and request.COOKIES.get('perpage').isdigit() else DEFAULT_PER_PAGE
    paginator = Paginator(videos_list, per_page)
    page = request.GET.get('page')

    videos = get_pagination(page, paginator)

    interactive = None
    if H5P_ENABLED:
        if h5p_libraries.objects.filter(machine_name='H5P.InteractiveVideo').count() > 0:
            interactive = True

    if request.is_ajax():
        return render_to_response("videos/videos_list.html",
                                  {"videos": videos, "param": param},
                                  context_instance=RequestContext(request))

    if request.GET.get('is_iframe', None):
        return render_to_response("videos/videos_iframe.html",
                                  {"videos": videos, "param": param},
                                  context_instance=RequestContext(request))

    return render_to_response("channels/channel.html",
                              {"channel": channel, "theme": theme,
                               "param": param, "videos": videos, "interactive": interactive},
                              context_instance=RequestContext(request))


@csrf_protect
@login_required
def channel_edit(request, slug_c):
    # Add this to improve folder selection and view list
    if not request.session.get('filer_last_folder_id'):
        from filer.models import Folder
        folder = Folder.objects.get(
            owner=request.user, name=request.user.username)
        request.session['filer_last_folder_id'] = folder.id

    channel = get_object_or_404(Channel, slug=slug_c)
    if request.user not in channel.owners.all() and not request.user.is_superuser:
        messages.add_message(
            request, messages.ERROR, _(u'You cannot edit this channel.'))
        raise PermissionDenied

    if request.user.is_staff:
        ThemeInlineFormSet = inlineformset_factory(
            Channel, Theme, form=ThemeForm, extra=0)
    else:
        ThemeInlineFormSet = inlineformset_factory(
            Channel, Theme, form=ThemeForm, exclude=('headband',), extra=0)

    channel_form = ChannelForm(instance=channel, user=request.user)
    #formset = ThemeInlineFormSet(instance=channel)
    referer = request.META.get('HTTP_REFERER')

    if request.POST:
        channel_form = ChannelForm(
            request.POST, instance=channel, user=request.user)
        formset = ThemeInlineFormSet(request.POST, instance=channel)
        if channel_form.is_valid() and formset.is_valid():
            channel = channel_form.save()
            formset = formset.save()
            messages.add_message(
                request, messages.INFO, _(u'The changes have been saved.'))

            referer = request.POST.get("referer")
            # go back
            if request.POST.get("action2") and request.POST.get("referer"):
                return HttpResponseRedirect("%s" % request.POST.get("referer"))
            if request.POST.get("action3"):
                return HttpResponseRedirect(reverse('pods.views.channel', args=(channel.slug,)))
        else:
            messages.add_message(
                request, messages.ERROR, _(u'One or more errors have been found in the form.'))

    formset = ThemeInlineFormSet(instance=channel)   # MAJ...
    return render_to_response("channels/channel_edit.html",
                              {'form': channel_form, 'formset': formset,
                                  "referer": referer},
                              context_instance=RequestContext(request))