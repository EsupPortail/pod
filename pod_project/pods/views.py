# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import hashlib
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.http import HttpResponse
from django.http import StreamingHttpResponse
from django.template import RequestContext
from pods.forms import ChannelForm
from pods.forms import ThemeForm
from pods.forms import PodForm
from pods.forms import ContributorPodsForm
from pods.forms import DocPodsForm
from pods.forms import TrackPodsForm
from pods.forms import ChapterPodsForm
from pods.forms import VideoPasswordForm
from pods.forms import NotesForm
from pods.forms import MediacoursesForm
from pods.forms import EnrichPodsForm
from pods.models import *
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms.models import inlineformset_factory
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from string import replace
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from datetime import datetime
from django.utils import formats
from django.utils.http import urlquote
from django.core.mail import EmailMultiAlternatives

import simplejson as json
from haystack.query import SearchQuerySet

from django.core.servers.basehttp import FileWrapper

DEFAULT_PER_PAGE = 12

VIDEOS = Pod.objects.filter(is_draft=False, encodingpods__gt=0).distinct()


def get_pagination(page, paginator):
    try:
        page = int(page.encode('utf-8'))
    except:
        page = 0
    try:
        return paginator.page(page + 1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        return paginator.page(paginator.num_pages)

# CHANNELS


@login_required
def owner_channels_list(request):
    channels_list = request.user.owner_channels.all()
    per_page = request.COOKIES.get('perpage') if request.COOKIES.get(
        'perpage') and request.COOKIES.get('perpage').isdigit() else DEFAULT_PER_PAGE
    paginator = Paginator(channels_list, per_page)
    page = request.GET.get('page') #request.GET.get('page')

    channels = get_pagination(page, paginator)

    if request.is_ajax():
        return render_to_response("channels/channels_list.html",
                                  {"channels": channels},
                                  context_instance=RequestContext(request))

    return render_to_response("channels/my_channels.html",
                              {"channels": channels, "video_count": VIDEOS.filter(
                                  channel__in=list(channels_list)).count()},
                              context_instance=RequestContext(request))


def channels(request):
    channels_list = Channel.objects.filter(visible=True)
    #per_page = request.GET.get('per_page') if request.GET.get('per_page') and request.GET.get('per_page').isdigit() else DEFAULT_PER_PAGE
    per_page = request.COOKIES.get('perpage') if request.COOKIES.get(
        'perpage') and request.COOKIES.get('perpage').isdigit() else DEFAULT_PER_PAGE
    paginator = Paginator(channels_list, per_page)
    page = request.GET.get('page')

    channels = get_pagination(page, paginator)

    if request.is_ajax():
        return render_to_response("channels/channels_list.html",
                                  {"channels": channels},
                                  context_instance=RequestContext(request))

    return render_to_response("channels/channels.html",
                              {"channels": channels, "video_count": VIDEOS.filter(
                                  channel__in=list(channels_list)).count()},
                              context_instance=RequestContext(request))


def channel(request, slug_c, slug_t=None):
    channel = get_object_or_404(Channel, slug=slug_c)
    theme = None

    videos_list = VIDEOS.filter(channel=channel)

    if slug_t:
        theme = get_object_or_404(Theme, slug=slug_t)
        videos_list = videos_list.filter(theme=theme)

    order_by = request.COOKIES.get('orderby') if request.COOKIES.get(
        'orderby') else "order_by_-date_added"
    videos_list = videos_list.order_by(
        "%s" % replace(order_by, "order_by_", ""))

    #per_page = request.GET.get('per_page') if request.GET.get('per_page') and request.GET.get('per_page').isdigit() else DEFAULT_PER_PAGE
    per_page = request.COOKIES.get('perpage') if request.COOKIES.get(
        'perpage') and request.COOKIES.get('perpage').isdigit() else DEFAULT_PER_PAGE
    paginator = Paginator(videos_list, per_page)
    page = request.GET.get('page')

    videos = get_pagination(page, paginator)

    if request.is_ajax():
        return render_to_response("videos/videos_list.html",
                                  {"videos": videos},
                                  context_instance=RequestContext(request))

    return render_to_response("channels/channel.html",
                              {"channel": channel, "theme": theme,
                                  "videos": videos},
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
    if not request.user.is_superuser or channel.owner != request.user:
        # return HttpResponseForbidden("<h1>Vous n'avez pas accès à cette
        # ressource</h1>")
        messages.add_message(
            request, messages.ERROR, _(u'You cannot edit this channel'))
        raise PermissionDenied

    ThemeInlineFormSet = inlineformset_factory(
        Channel, Theme, form=ThemeForm, extra=0)

    channel_form = ChannelForm(instance=channel)
    #formset = ThemeInlineFormSet(instance=channel)
    referer = request.META.get('HTTP_REFERER')

    if request.POST:
        channel_form = ChannelForm(request.POST, instance=channel)
        formset = ThemeInlineFormSet(request.POST, instance=channel)
        if channel_form.is_valid() and formset.is_valid():
            channel = channel_form.save()
            formset = formset.save()
            messages.add_message(
                request, messages.INFO, _(u'The changes have been saved'))

            referer = request.POST.get("referer")
            # go back
            if request.POST.get("action2") and request.POST.get("referer"):
                return HttpResponseRedirect("%s" % request.POST.get("referer"))
            if request.POST.get("action3"):
                return HttpResponseRedirect(reverse('pods.views.channel', args=(channel.slug,)))
        else:
            messages.add_message(
                request, messages.ERROR, _(u'Error in the form'))

    formset = ThemeInlineFormSet(instance=channel)   # MAJ...
    return render_to_response("channels/channel_edit.html",
                              {'form': channel_form, 'formset': formset,
                                  "referer": referer},
                              context_instance=RequestContext(request))


def types(request):
    types_list = Type.objects.all()
    #per_page = request.GET.get('per_page') if request.GET.get('per_page') and request.GET.get('per_page').isdigit() else DEFAULT_PER_PAGE
    per_page = request.COOKIES.get('perpage') if request.COOKIES.get(
        'perpage') and request.COOKIES.get('perpage').isdigit() else DEFAULT_PER_PAGE
    paginator = Paginator(types_list, per_page)
    page = request.GET.get('page')

    types = get_pagination(page, paginator)

    if request.is_ajax():
        return render_to_response("types/types_list.html",
                                  {"types": types},
                                  context_instance=RequestContext(request))

    return render_to_response("types/types.html",
                              {"types": types, "video_count": VIDEOS.filter(
                                  type__in=list(types_list)).count()},
                              context_instance=RequestContext(request))


def owners(request):
    owners_list = User.objects.filter(pod__in=VIDEOS).order_by(
        'last_name').distinct()  # User.objects.all()
    owners_filter = request.GET.get(
        'owners_filter') if request.GET.get('owners_filter') else None
    if owners_filter:
        owners_list = owners_list.filter(
            last_name__iregex=r'^%s+' % owners_filter)
    #per_page = request.GET.get('per_page') if request.GET.get('per_page') and request.GET.get('per_page').isdigit() else DEFAULT_PER_PAGE
    per_page = request.COOKIES.get('perpage') if request.COOKIES.get(
        'perpage') and request.COOKIES.get('perpage').isdigit() else DEFAULT_PER_PAGE
    paginator = Paginator(owners_list, per_page)
    page = request.GET.get('page')

    owners = get_pagination(page, paginator)

    if request.is_ajax():
        return render_to_response("owners/owners_list.html",
                                  {"owners": owners},
                                  context_instance=RequestContext(request))

    return render_to_response("owners/owners.html",
                              {"owners": owners, "video_count": VIDEOS.filter(
                                  owner__in=list(owners_list)).count()},
                              context_instance=RequestContext(request))


def disciplines(request):
    disciplines_list = Discipline.objects.all()
    #per_page = request.GET.get('per_page') if request.GET.get('per_page') and request.GET.get('per_page').isdigit() else DEFAULT_PER_PAGE
    per_page = request.COOKIES.get('perpage') if request.COOKIES.get(
        'perpage') and request.COOKIES.get('perpage').isdigit() else DEFAULT_PER_PAGE
    paginator = Paginator(disciplines_list, per_page)
    page = request.GET.get('page')

    disciplines = get_pagination(page, paginator)

    if request.is_ajax():
        return render_to_response("disciplines/disciplines_list.html",
                                  {"disciplines": disciplines},
                                  context_instance=RequestContext(request))

    return render_to_response("disciplines/disciplines.html",
                              {"disciplines": disciplines, "video_count": VIDEOS.filter(
                                  discipline__in=list(disciplines_list)).count()},
                              context_instance=RequestContext(request))


def tags(request):
    return render_to_response("tags/tags.html",
                              {},
                              context_instance=RequestContext(request))


@login_required
def owner_videos_list(request):
    videos_list = request.user.pod_set.all()

    per_page = request.COOKIES.get('perpage') if request.COOKIES.get(
        'perpage') and request.COOKIES.get('perpage').isdigit() else DEFAULT_PER_PAGE

    order_by = request.COOKIES.get('orderby') if request.COOKIES.get(
        'orderby') else "order_by_-date_added"
    videos_list = videos_list.order_by(
        "%s" % replace(order_by, "order_by_", ""))

    paginator = Paginator(videos_list, per_page)
    page = request.GET.get('page')

    videos = get_pagination(page, paginator)

    if request.is_ajax():
        return render_to_response("videos/videos_list.html",
                                  {"videos": videos},
                                  context_instance=RequestContext(request))

    return render_to_response("videos/my_videos.html",
                              {"videos": videos},
                              context_instance=RequestContext(request))


@login_required
def favorites_videos_list(request):
    videos_list = Pod.objects.filter(
        id__in=request.user.favorites_set.all().values_list('video', flat=True))

    per_page = request.COOKIES.get('perpage') if request.COOKIES.get(
        'perpage') and request.COOKIES.get('perpage').isdigit() else DEFAULT_PER_PAGE

    order_by = request.COOKIES.get('orderby') if request.COOKIES.get(
        'orderby') else "order_by_-date_added"
    videos_list = videos_list.order_by(
        "%s" % replace(order_by, "order_by_", ""))

    paginator = Paginator(videos_list, per_page)
    page = request.GET.get('page')

    videos = get_pagination(page, paginator)

    if request.is_ajax():
        return render_to_response("videos/videos_list.html",
                                  {"videos": videos},
                                  context_instance=RequestContext(request))

    return render_to_response("favorites/my_favorites.html",
                              {"videos": videos},
                              context_instance=RequestContext(request))


def videos(request):
    videos_list = VIDEOS
    # type
    type = request.GET.getlist('type') if request.GET.getlist('type') else None
    if type:
        videos_list = videos_list.filter(type__slug__in=type)

    # discipline
    discipline = request.GET.getlist(
        'discipline') if request.GET.getlist('discipline') else None
    if discipline:
        videos_list = videos_list.filter(discipline__slug__in=discipline)
    # owner
    owner = request.GET.getlist(
        'owner') if request.GET.getlist('owner') else None
    list_owner = None
    if owner:
        videos_list = videos_list.filter(owner__username__in=owner)
        list_owner = User.objects.filter(username__in=owner)

    # tags
    tag = request.GET.getlist('tag') if request.GET.getlist('tag') else None
    if tag:
        videos_list = videos_list.filter(tags__slug__in=tag).distinct()
    #Food.objects.filter(tags__name__in=["delicious", "red"]).distinct()

    order_by = request.COOKIES.get('orderby') if request.COOKIES.get(
        'orderby') else "order_by_-date_added"
    videos_list = videos_list.order_by(
        "%s" % replace(order_by, "order_by_", ""))

    per_page = request.COOKIES.get('perpage') if request.COOKIES.get(
        'perpage') and request.COOKIES.get('perpage').isdigit() else DEFAULT_PER_PAGE

    paginator = Paginator(videos_list, per_page)
    page = request.GET.get('page')

    videos = get_pagination(page, paginator)

    if request.is_ajax():
        return render_to_response("videos/videos_list.html",
                                  {"videos": videos, "owners": list_owner},
                                  context_instance=RequestContext(request))

    return render_to_response("videos/videos.html",
                              {"videos": videos, "types": type, "owners": list_owner,
                                  "disciplines": discipline, "tags_slug": tag},
                              context_instance=RequestContext(request))


@csrf_protect
def video(request, slug, slug_c=None, slug_t=None):
    video = get_object_or_404(Pod, slug=slug)
    channel = None
    if slug_c:
        channel = get_object_or_404(Channel, slug=slug_c)
    theme = None
    if slug_t:
        theme = get_object_or_404(Theme, slug=slug_t)

    if video.is_draft:
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('account_login') + '?next=%s' % urlquote(request.get_full_path()))
        else:
            if request.user == video.owner or request.user.is_superuser:
                pass
            else:
                messages.add_message(
                    request, messages.ERROR, _(u'You cannot watch this video'))
                raise PermissionDenied

    if video.is_restricted:
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('account_login') + '?next=%s' % urlquote(request.get_full_path()))

    if request.POST:
        if request.POST.get("action") and request.POST.get("action") == "increase_view_count":
            if request.user.is_authenticated() and (request.user == video.owner or request.user.is_superuser):
                pass
            else:
                video.view_count += 1
                video.save()
            if request.is_ajax():
                return HttpResponse(_(u'The changes have been saved'))

    # Video url to share
    share_url = request.get_host() + request.get_full_path()
    if share_url.find('?') == -1:
        share_url += '?'
    else:
        share_url += '&'
    share_url += 'is_iframe=true&size=240'

    ####### VIDEO PASSWORD #########
    if video.password and not (request.user == video.owner or request.user.is_superuser):
        form = VideoPasswordForm()
        if not request.POST:
            return render_to_response(
                'videos/video.html',
                {'video': video, 'form': form, 'channel': channel,
                    'theme': theme, 'share_url': share_url},
                context_instance=RequestContext(request)
            )
        else:
            # A form bound to the POST data
            form = VideoPasswordForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data['password']
                if password == video.password:
                    if request.GET.get('action') and request.GET.get('action') == "download":
                        return download_video(video, request.GET)
                    else:
                        return render_to_response(
                            'videos/video.html',
                            {'video': video, 'channel': channel,
                                'theme': theme, 'share_url': share_url},
                            context_instance=RequestContext(request)
                        )
                else:
                    messages.add_message(
                        request, messages.ERROR, _(u'Incorrect password'))
                    return render_to_response(
                        'videos/video.html',
                        {'video': video, 'form': form, 'channel': channel,
                            'theme': theme, 'share_url': share_url},
                        context_instance=RequestContext(request)
                    )
            else:
                messages.add_message(
                    request, messages.ERROR, _(u'Error in the form'))
                return render_to_response(
                    'videos/video.html',
                    {'video': video, 'form': form, 'channel': channel,
                        'theme': theme, 'share_url': share_url},
                    context_instance=RequestContext(request)
                )

    if request.user.is_authenticated():
        note, created = Notes.objects.get_or_create(
            video=video, user=request.user)
        notes_form = NotesForm(instance=note)
        if request.GET.get('action') and request.GET.get('action') == "download":
            return download_video(video, request.GET)
        else:
            return render_to_response(
                'videos/video.html',
                {'video': video, 'channel': channel, 'theme': theme,
                    'notes_form': notes_form, 'share_url': share_url},
                context_instance=RequestContext(request)
            )
    if request.GET.get('action') and request.GET.get('action') == "download":
        return download_video(video, request.GET)
    else:
        return render_to_response(
            'videos/video.html',
            {'video': video, 'channel': channel,
                'theme': theme, 'share_url': share_url},
            context_instance=RequestContext(request)
        )


def download_video(video, get_request):
    format = "video/mp4" if "video" in video.get_mediatype() else "audio/mp3"
    resolution = get_request.get(
        'resolution') if get_request.get('resolution') else 240
    filename = EncodingPods.objects.get(
        video=video, encodingType__output_height=resolution, encodingFormat=format).encodingFile.path
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type=format)
    response['Content-Length'] = os.path.getsize(filename)
    response['Content-Disposition'] = 'attachment; filename="%s_%s.%s"' % (
        video.slug, resolution, format.split("/")[1])
    return response


@login_required
@csrf_protect
def video_add_favorite(request, slug):
    video = get_object_or_404(Pod, slug=slug)
    if request.POST:
        msg = _(u'The video has been added to your Favorites')
        favorite, create = Favorites.objects.get_or_create(
            user=request.user, video=video)
        if not create:
            favorite.delete()
            msg = _(u'The video has been removed to your Favorites')
        if request.is_ajax():
            return HttpResponse(msg)
        messages.add_message(request, messages.INFO, msg)
        return HttpResponseRedirect(reverse('pods.views.video', args=(video.slug,)))
    else:
        messages.add_message(
            request, messages.ERROR, _(u'You cannot view this page'))
        raise PermissionDenied


@login_required
@csrf_protect
def video_notes(request, slug):
    video = get_object_or_404(Pod, slug=slug)
    if request.POST:
        notes_form = NotesForm(request.POST)
        if notes_form.is_valid():
            note, created = Notes.objects.get_or_create(
                video=video, user=request.user)
            note.note = notes_form.cleaned_data["note"]
            note.save()
            messages.add_message(
                request, messages.INFO, _(u'The changes have been saved'))
            if request.is_ajax():
                return HttpResponse(_(u'The changes have been saved'))
            return HttpResponseRedirect(reverse('pods.views.video', args=(video.slug,)))
    else:
        messages.add_message(
            request, messages.ERROR, _(u'You cannot view this page'))
        raise PermissionDenied


@csrf_protect
@login_required
def video_edit(request, slug=None):
    # Add this to improve folder selection and view list
    if not request.session.get('filer_last_folder_id'):
        from filer.models import Folder
        folder = Folder.objects.get(
            owner=request.user, name=request.user.username)
        request.session['filer_last_folder_id'] = folder.id

    video_form = PodForm(request)
    video = None
    if slug:
        video = get_object_or_404(Pod, slug=slug)
        if request.user != video.owner and not request.user.is_superuser:
            messages.add_message(
                request, messages.ERROR, _(u'You cannot edit this video'))
            raise PermissionDenied
        video_form = PodForm(request, instance=video)

    referer = request.META.get('HTTP_REFERER')

    if request.POST:
        if video:
            video_form = PodForm(
                request, request.POST, request.FILES, instance=video)
        else:
            video_form = PodForm(request, request.POST, request.FILES)

        if video_form.is_valid():
            vid = video_form.save(commit=False)
            if request.POST.get('owner') and request.POST.get('owner') != "":
                vid.owner = video_form.cleaned_data['owner']
            else:
                vid.owner = request.user
            if request.FILES:
                vid.to_encode = True
            vid.save()
            # Without this next line the tags won't be saved.
            video_form.save_m2m()
            messages.add_message(
                request, messages.INFO, _(u'The changes have been saved'))
            # Without this next line the tags does not appear in search engine
            vid.save()

            referer = request.POST.get("referer")
            # go back
            if request.POST.get("action2") and request.POST.get("referer"):
                return HttpResponseRedirect("%s" % request.POST.get("referer"))
            if request.POST.get("action3"):
                return HttpResponseRedirect(reverse('pods.views.video', args=(vid.slug,)))
            else:
                return HttpResponseRedirect(reverse('pods.views.video_edit', args=(vid.slug,)))
        else:
            messages.add_message(
                request, messages.ERROR, _(u'Error in the form'))

    video_ext_accept = replace(' | '.join(settings.VIDEO_EXT_ACCEPT), ".", "")

    return render_to_response("videos/video_edit.html",
                              {'form': video_form, "referer": referer,
                                  "video_ext_accept": video_ext_accept},
                              context_instance=RequestContext(request))


@csrf_protect
@login_required
#@staff_member_required
def video_completion(request, slug):
    # Add this to improve folder selection and view list
    if not request.session.get('filer_last_folder_id'):
        from filer.models import Folder
        folder = Folder.objects.get(
            owner=request.user, name=request.user.username)
        request.session['filer_last_folder_id'] = folder.id

    video = get_object_or_404(Pod, slug=slug)
    if request.user != video.owner and not request.user.is_superuser:
        messages.add_message(
            request, messages.ERROR, _(u'You cannot complete this video'))
        raise PermissionDenied

    ContributorInlineFormSet = inlineformset_factory(
        Pod, ContributorPods, form=ContributorPodsForm, extra=0, can_delete=True)
    TrackInlineFormSet = inlineformset_factory(
        Pod, TrackPods, form=TrackPodsForm, extra=0, can_delete=True)
    DocInlineFormSet = inlineformset_factory(
        Pod, DocPods, form=DocPodsForm, extra=0, can_delete=True)

    if request.method == "POST":
        if request.user.is_staff:
            contributorformset = ContributorInlineFormSet(
                request.POST, instance=video, prefix='contributor_form')
            trackformset = TrackInlineFormSet(
                request.POST, instance=video, prefix='track_form')
            docformset = DocInlineFormSet(
                request.POST, instance=video, prefix='doc_form')

            if contributorformset.is_valid() and trackformset.is_valid() and docformset.is_valid():
                contributorformset.save()
                trackformset.save()
                docformset.save()
                # MAJ...
                contributorformset = ContributorInlineFormSet(
                    instance=video, prefix='contributor_form')
                trackformset = TrackInlineFormSet(
                    instance=video, prefix='track_form')
                docformset = DocInlineFormSet(
                    instance=video, prefix='doc_form')
                #...
                messages.add_message(
                    request, messages.INFO, _(u'The changes have been saved'))
                referer = request.POST.get("referer")
                # go back
                if request.POST.get("action2") and request.POST.get("referer"):
                    return HttpResponseRedirect("%s" % request.POST.get("referer"))
                if request.POST.get("action3"):
                    return HttpResponseRedirect(reverse('pods.views.video', args=(video.slug,)))
                # else:
                # return
                # HttpResponseRedirect(reverse('pods.views.video_completion',
                # args=(video.slug,)))
            else:
                messages.add_message(
                    request, messages.ERROR, _(u'Error in the form'))
        else:
            contributorformset = ContributorInlineFormSet(
                request.POST, instance=video, prefix='contributor_form')

            if contributorformset.is_valid():
                contributorformset.save()
                # MAJ...
                contributorformset = ContributorInlineFormSet(
                    instance=video, prefix='contributor_form')
                #...
                messages.add_message(
                    request, messages.INFO, _(u'The changes have been saved'))
                referer = request.POST.get("referer")
                # go back
                if request.POST.get("action2") and request.POST.get("referer"):
                    return HttpResponseRedirect("%s" % request.POST.get("referer"))
                if request.POST.get("action3"):
                    return HttpResponseRedirect(reverse('pods.views.video', args=(video.slug,)))
                # else:
                # return
                # HttpResponseRedirect(reverse('pods.views.video_completion',
                # args=(video.slug,)))
            else:
                messages.add_message(
                    request, messages.ERROR, _(u'Error in the form'))
    else:
        contributorformset = ContributorInlineFormSet(
            instance=video, prefix='contributor_form')
        trackformset = TrackInlineFormSet(instance=video, prefix='track_form')
        docformset = DocInlineFormSet(instance=video, prefix='doc_form')

    if request.user.is_staff:
        return render_to_response("videos/video_completion_formset.html",
                                  {'contributorformset': contributorformset,
                                      'trackformset': trackformset, 'docformset': docformset},
                                  context_instance=RequestContext(request))
    else:
        return render_to_response("videos/video_completion_formset.html",
                                  {'contributorformset': contributorformset},
                                  context_instance=RequestContext(request))


@csrf_protect
@login_required
def video_chapter(request, slug):
    video = get_object_or_404(Pod, slug=slug)
    if request.user != video.owner and not request.user.is_superuser:
        messages.add_message(
            request, messages.ERROR, _(u'You cannot chapter this video'))
        raise PermissionDenied

    ChapterInlineFormSet = inlineformset_factory(
        Pod, ChapterPods, form=ChapterPodsForm, extra=0, can_delete=True)

    if request.method == "POST":
        chapterformset = ChapterInlineFormSet(
            request.POST, instance=video, prefix='chapter_form')

        if chapterformset.is_valid():
            chapterformset.save()

            # MAJ...
            chapterformset = ChapterInlineFormSet(
                instance=video, prefix='chapter_form')
            #...
            messages.add_message(
                request, messages.INFO, _(u'The changes have been saved'))

        else:
            messages.add_message(
                request, messages.ERROR, _(u'Error in the form'))
    else:
        chapterformset = ChapterInlineFormSet(
            instance=video, prefix='chapter_form')

    return render_to_response("videos/video_chapterpods_formset.html",
                              {'chapterformset': chapterformset},
                              context_instance=RequestContext(request))


@csrf_protect
@login_required
@staff_member_required
def video_enrich(request, slug):
    video = get_object_or_404(Pod, slug=slug)
    # Add this to improve folder selection and view list
    if not request.session.get('filer_last_folder_id'):
        from filer.models import Folder
        folder = Folder.objects.get(
            owner=request.user, name=request.user.username)
        request.session['filer_last_folder_id'] = folder.id

    if request.user != video.owner and not request.user.is_superuser:
        messages.add_message(
            request, messages.ERROR, _(u'You cannot enrich this video'))
        raise PermissionDenied

    EnrichInlineFormSet = inlineformset_factory(
        Pod, EnrichPods, form=EnrichPodsForm, extra=0, can_delete=True)

    if request.method == "POST":
        enrichformset = EnrichInlineFormSet(
            request.POST, instance=video, prefix='enrich_form')

        if enrichformset.is_valid():
            enrichformset.save()

            # MAJ...
            enrichformset = EnrichInlineFormSet(
                instance=video, prefix='enrich_form')
            #...
            messages.add_message(
                request, messages.INFO, _(u'The changes have been saved'))

        else:
            messages.add_message(
                request, messages.ERROR, _(u'Error in the form'))
    else:
        enrichformset = EnrichInlineFormSet(
            instance=video, prefix='enrich_form')

    return render_to_response("videos/video_enrichpods_formset.html",
                              {'enrichformset': enrichformset},
                              context_instance=RequestContext(request))


@csrf_protect
@login_required
def video_delete(request, slug):
    video = get_object_or_404(Pod, slug=slug)
    if request.user != video.owner and not request.user.is_superuser:
        messages.add_message(
            request, messages.ERROR, _(u'You can\'t delete this video'))
        raise PermissionDenied
    """
    from django.contrib.admin.util import NestedObjects

    collector = NestedObjects(using='default') # or specific database
    collector.collect([video])
    to_delete = collector.nested()
    print "to_delete : %s" %to_delete
    print "--------"
    for obj in to_delete:
        print obj
    """
    if request.method == "POST":
        video.delete()
        messages.add_message(
            request, messages.INFO, _(u'The video has been deleted'))
        return HttpResponseRedirect(reverse('pods.views.videos'))

    return render_to_response("videos/video_delete.html",
                              {"video": video},
                              context_instance=RequestContext(request))


def get_video_encoding(request, slug, csrftoken, size, type, ext):
    # csrf = request.COOKIES.get(
    #    'csrftoken') if request.COOKIES.get('csrftoken') else None
    # print csrf
    # print csrftoken
    video = get_object_or_404(Pod, slug=slug)
    if video.is_draft:
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('account_login') + '?next=%s' % urlquote(request.get_full_path()))
        else:
            if request.user == video.owner or request.user.is_superuser:
                pass
            else:
                messages.add_message(
                    request, messages.ERROR, _(u'You cannot watch this video'))
                raise PermissionDenied
    if video.is_restricted:
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('account_login') + '?next=%s' % urlquote(request.get_full_path()))
    encodingpods = get_object_or_404(EncodingPods,
                                     encodingFormat="%s/%s" % (type, ext), video=video, encodingType__output_height=size)
    """
    #TODO
    import re
    referer = request.META.get('HTTP_REFERER')
    user_agent = request.META.get('HTTP_USER_AGENT')
    MOBILE_AGENT_RE=re.compile(r".*(iphone|mobile|androidtouch)",re.IGNORECASE)
    print "user_agent : %s" %user_agent
    print "user agent match : %s" %MOBILE_AGENT_RE.match(user_agent)
    print "REFERER : %s" %referer
    print "CSRF_COOKIE : %s - encodingpods : %s" %(request.META['CSRF_COOKIE'], encodingpods)
    print "SESSION : %s" %request.session.items()
    print "SESSION : %s" %request.session.session_key

    Viewed.log_view(request, video_id)
    video = Video.objects.get(pk=video_id)
    filename = video.uploaded_video.name.split('/')[-1]
    response = StreamingHttpResponse(video.uploaded_video, content_type='video/mp4')
    response['Content-length'] = video.uploaded_video.file.size
    return response

    response = StreamingHttpResponse(encodingpods.encodingFile, content_type='%s' %encodingpods.encodingFormat)
    response['Content-length'] = encodingpods.encodingFile.size #video.uploaded_video.file.size
    return response

    # print encodingpods.encodingFile.url

    #END TODO
    """
    return HttpResponseRedirect("%s%s" % (settings.FMS_ROOT_URL, encodingpods.encodingFile.url))


def autocomplete(request):
    sqs = SearchQuerySet().autocomplete(
        title_auto=request.GET.get('q', ''))[:5]
    suggestions = [entry.object.title for entry in sqs]
    # Make sure you return a JSON object, not a bare list.
    # Otherwise, you could be vulnerable to an XSS attack.
    the_data = json.dumps({
        'results': suggestions
    })
    return HttpResponse(the_data, content_type='application/json')


# RECORDER
@csrf_protect
@login_required
@staff_member_required
def mediacourses(request):
    mediapath = request.GET.get('mediapath')
    print "mediapath : %s" % mediapath
    if not mediapath and not request.user.is_superuser:
        messages.add_message(
            request, messages.ERROR, _(u'Mediapath should be indicated'))
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
            message = _('Error in the form')
            messages.add_message(request, messages.ERROR, message)

    return render_to_response("mediacourses/mediacourses_add.html",
                              {"form": form},
                              context_instance=RequestContext(request))


def lives(request):  # affichage des directs
    buildings = Building.objects.all()
    return render_to_response("mediacourses/lives.html",
                              {'buildings': buildings},
                              context_instance=RequestContext(request))


def live(request, pk):  # affichage des directs
    recorder = get_object_or_404(Recorder, pk=pk)
    if recorder.is_restricted and not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('account_login') + '?next=%s' % request.get_full_path())

    c = RequestContext(request, {'recorder': recorder})
    return render_to_response('mediacourses/live.html', c)


def liveState(request):  # affichage des directs
    if request.GET.get("recordingPlace") and request.GET.get("status"):
        recorder = get_object_or_404(
            Recorder, adress_ip=request.GET.get("recordingPlace").replace("_", "."))
        if request.GET.get("status") == "begin":
            recorder.status = 1
        else:
            recorder.status = 0
        recorder.save()
    return HttpResponse("ok")


def mediacourses_notify(request):  # post mediacourses notification
    # http://URL/mediacourses_notify/?recordingPlace=192_168_1_10&mediapath=file.zip&key=77fac92a3f06d50228116898187e50e5
    if request.GET.get("recordingPlace") and request.GET.get('mediapath') and request.GET.get('key'):
        m = hashlib.md5()
        m.update(request.GET.get("recordingPlace") + settings.RECORDER_SALT)
        if request.GET.get('key') != m.hexdigest():
            # messages.add_message(
            #    request, messages.ERROR, _(u'You cannot notify a mediacourse'))
            #raise PermissionDenied
            return HttpResponse("nok")

        recorder = get_object_or_404(
            Recorder, adress_ip=request.GET.get("recordingPlace").replace("_", "."))
        date_notify = datetime.now()
        formatted_date_notify = formats.date_format(
            date_notify, "SHORT_DATE_FORMAT")
        link_url = ''.join([request.build_absolute_uri(reverse('mediacourses')), "?mediapath=", request.GET.get(
            'mediapath'), "&course_title=%s" % _("recording"), " %s" % formatted_date_notify.replace("/", "-")])

        text_msg = _("Hello, \n\na new mediacourse has just be added on the video website \"%(title_site)s\" from the recorder \"%(recorder)s\"."
                     "\nTo add it, just click on link below.\n\n%(link_url)s\nif you cannot click on link, just copy-paste it in your browser."
                     "\n\nRegards") % {'title_site': settings.TITLE_SITE, 'recorder': recorder.name, 'link_url': link_url}

        html_msg = _("Hello, <p>a new mediacourse has just be added on %(title_site)s from the recorder \"%(recorder)s\"."
                     "<br/>To add it, just click on link below.</p><a href=\"%(link_url)s\">%(link_url)s</a><br/><i>if you cannot click on link, just copy-paste it in your browser.</i>"
                     "<p><p>Regards</p>") % {'title_site': settings.TITLE_SITE, 'recorder': recorder.name, 'link_url': link_url}

        admin_emails = User.objects.filter(
            is_superuser=True).values_list('email', flat=True)
        subject = "[" + settings.TITLE_SITE + \
            "] %s" % _('New mediacourse added')

        email_msg = EmailMultiAlternatives(
            subject, text_msg, settings.DEFAULT_FROM_EMAIL, admin_emails)

        email_msg.attach_alternative(html_msg, "text/html")
        email_msg.send(fail_silently=False)

        return HttpResponse("ok")
    else:
        return HttpResponse("nok")


def liveSlide(request):  # affichage des slides en direct
    c = RequestContext(request, {'filename': request.GET.get("ip")})
    return render_to_response('mediacourses/liveSlide.html', c)
    """
    if request.GET.get("ip"):
        filename = "/audiovideocours/ftp/live/%s.jpg" %request.GET.get("ip").replace(".", "_") #Select your file here. 
        if not os.path.isfile(filename):
            return HttpResponse("pas de fichier")
        wrapper = FileWrapper(file(filename))
        mt = mimetypes.guess_type(filename)[0]
        response = HttpResponse(wrapper, content_type=mt)
        response['Content-Length'] = os.path.getsize(filename)
        return response
    else:
        return HttpResponse("pas de fichier")
    """
