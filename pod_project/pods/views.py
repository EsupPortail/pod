# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import hashlib
from string import find
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
from pods.forms import SearchForm
from pods.models import *
from pods.utils_rssfeed import MySelectFeed
from django.contrib import messages

# Replaced to allow JSON serialization of localized messages.
from django.utils.translation import ugettext as _
# from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms.models import inlineformset_factory
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.exceptions import SuspiciousOperation
from string import replace
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from datetime import datetime, date
from django.utils import formats
from django.utils.http import urlquote
from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Count
import simplejson as json

from django.core.servers.basehttp import FileWrapper

DEFAULT_PER_PAGE = 12
VIDEOS = Pod.objects.filter(is_draft=False, encodingpods__gt=0).distinct()
ES_URL = getattr(settings, 'ES_URL', ['http://127.0.0.1:9200/'])

referer = ''


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
    channels_list = request.user.owners_channels.all().annotate(video_count=Count("pod", distinct=True))
    per_page = request.COOKIES.get('perpage') if request.COOKIES.get(
        'perpage') and request.COOKIES.get('perpage').isdigit() else DEFAULT_PER_PAGE
    paginator = Paginator(channels_list, per_page)
    page = request.GET.get('page')  # request.GET.get('page')

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
    channels_list = Channel.objects.filter(
        visible=True, pod__is_draft=False, pod__encodingpods__gt=0
    ).distinct().annotate(video_count=Count("pod", distinct=True))
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

    param = "channel=%s" % (slug_c,)

    if slug_t:
        theme = get_object_or_404(Theme, slug=slug_t)
        videos_list = videos_list.filter(theme=theme)
	param = "channel=%s&theme=%s" % (slug_c, slug_t.encode('utf8'))

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
    RSS = settings.RSS_ENABLED
    ATOM_HD = settings.ATOM_HD_ENABLED
    ATOM_SD = settings.ATOM_SD_ENABLED
    #ATOM_AUDIO = settings.ATOM_AUDIO_ENABLED

    interactive = None
    if settings.H5P_ENABLED:
        from h5pp.models import h5p_libraries
        if h5p_libraries.objects.filter(machine_name='H5P.InteractiveVideo').count() > 0:
            interactive = True

    if request.is_ajax():
        return render_to_response("videos/videos_list.html",
                                  {"videos": videos, "param": param, "RSS": RSS, "ATOM_HD": ATOM_HD, "ATOM_SD": ATOM_SD},
                                  context_instance=RequestContext(request))

    if request.GET.get('is_iframe', None):
        return render_to_response("videos/videos_iframe.html",
                                  {"videos": videos, "param": param, "RSS": RSS, "ATOM_HD": ATOM_HD, "ATOM_SD": ATOM_SD},
                                  context_instance=RequestContext(request))

    return render_to_response("channels/channel.html",
                              {"channel": channel, "theme": theme,
				   "param": param, "videos": videos, "RSS": RSS, "ATOM_HD": ATOM_HD, "ATOM_SD": ATOM_SD, "interactive": interactive}, 
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


def types(request):
    types_list = Type.objects.filter(
        pod__is_draft=False, pod__encodingpods__gt=0
    ).distinct().annotate(video_count=Count("pod", distinct=True))
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
    owners_list = User.objects.filter(
        pod__is_draft=False, pod__encodingpods__gt=0
    ).order_by(
        'last_name').distinct().annotate(video_count=Count("pod", distinct=True)).prefetch_related("userprofile")
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
    disciplines_list = Discipline.objects.filter(
        pod__is_draft=False, pod__encodingpods__gt=0
    ).distinct().annotate(video_count=Count("pod", distinct=True))
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

    interactive = None
    if settings.H5P_ENABLED:
        from h5pp.models import h5p_libraries
        if h5p_libraries.objects.filter(machine_name='H5P.InteractiveVideo').count() > 0:
            interactive = True

    if request.is_ajax():
        return render_to_response("videos/videos_list.html",
                                  {"videos": videos},
                                  context_instance=RequestContext(request))

    return render_to_response("videos/my_videos.html",
                              {"videos": videos, "interactive": interactive},
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
    is_iframe = request.GET.get('is_iframe', None)

    param = None

    # type
    type = request.GET.getlist(
        'type') if request.GET.getlist('type') else None
    utype = []
    if type:
        for t in type:
	    utype.append(t.encode('utf8'))
        videos_list = videos_list.filter(type__slug__in=type)
	param = "type=%s" % (utype,)

    # discipline
    udiscipline = []
    discipline = request.GET.getlist(
        'discipline') if request.GET.getlist('discipline') else None
    if discipline:
        videos_list = videos_list.filter(discipline__slug__in=discipline)
	for d in discipline:
	    udiscipline.append(d.encode('utf8'))
	if param:
	    param = param + " discipline=%s" % (udiscipline,)
	    #param = param + " discipline=%s" % (discipline.encode('utf8'),)
	else:
	    param = "discipline=%s" % (udiscipline,)

    # owner
    owner = request.GET.getlist(
        'owner') if request.GET.getlist('owner') else None
    list_owner = None
    if owner:
        uowner = []
        for o in owner:
	    uowner.append(o.encode('utf8'))
        videos_list = videos_list.filter(owner__username__in=owner)
        if not is_iframe:
            list_owner = User.objects.filter(username__in=owner)
	if param:
	    param = param + " owner=%s" % (uowner,)
	else:
	    param = "owner=%s" % (uowner,)
    # tags
    tag = request.GET.getlist(
        'tag') if request.GET.getlist('tag') else None
    if tag:
        utag = []
	for g in tag:
	    utag.append(g.encode('utf8'))
        videos_list = videos_list.filter(tags__slug__in=tag).distinct()
	if param:
	    param = param + " tag=%s" % (utag,)
	else:
	    param = "tag=%s" % (utag,)
    # Food.objects.filter(tags__name__in=["delicious", "red"]).distinct()

    order_by = request.COOKIES.get('orderby') if request.COOKIES.get(
        'orderby') else "order_by_-date_added"
    videos_list = videos_list.order_by(
        "%s" % replace(order_by, "order_by_", ""))

    per_page = request.COOKIES.get('perpage') if request.COOKIES.get(
        'perpage') and request.COOKIES.get(
        'perpage').isdigit() else DEFAULT_PER_PAGE

    paginator = Paginator(videos_list, per_page)
    page = request.GET.get('page')

    videos = get_pagination(page, paginator)

    RSS = settings.RSS_ENABLED
    ATOM_HD = settings.ATOM_HD_ENABLED
    ATOM_SD = settings.ATOM_SD_ENABLED
    #ATOM_AUDIO = settings.ATOM_AUDIO_ENABLED
  
    interactive = None
    if settings.H5P_ENABLED:
        from h5pp.models import h5p_libraries
        if h5p_libraries.objects.filter(machine_name='H5P.InteractiveVideo').count() > 0:
            interactive = True
            
    if request.is_ajax():
        some_data_to_dump = {
	    'json_toolbar': render_to_string('maintoolbar.html',
	        {'videos': videos, 'param': param, 'RSS': RSS, 'ATOM_HD': ATOM_HD, 'ATOM_SD': ATOM_SD}),
	    'json_videols': render_to_string('videos/videos_list.html',
	        {'videos': videos, 'types': type, 'owners': list_owner, 'disciplines': discipline, 'param': param, 'csrf_token': request.COOKIES['csrftoken']})
	}
        data = json.dumps(some_data_to_dump)
	return HttpResponse(data, content_type='application/json')
        #return render_to_response("videos/videos_list.html",
        #                          {"videos": videos, "param": param, "owners": list_owner},
        #                          context_instance=RequestContext(request))

    if is_iframe:
        return render_to_response("videos/videos_iframe.html",
                                  {"videos": videos},
                                  context_instance=RequestContext(request))

    return render_to_response("videos/videos.html",
                              {"videos": videos, "types": type, "owners": list_owner,
                                  "disciplines": discipline, "tags_slug": tag, "param": param, "RSS": RSS, "ATOM_HD": ATOM_HD, "ATOM_SD": ATOM_SD, "interactive": interactive},
                              context_instance=RequestContext(request))


@csrf_protect
def video(request, slug, slug_c=None, slug_t=None):
    try:
        id = int(slug[:find(slug, "-")])
    except ValueError:
        raise SuspiciousOperation('Invalid video id')
    video = get_object_or_404(Pod, id=id)
    show_report = getattr(settings, 'SHOW_REPORT', False)
    param = None
    channel = None
    if slug_c:
        channel = get_object_or_404(Channel, slug=slug_c)
	param = "slug_c=%s" % (str(slug_c),)
    theme = None
    if slug_t:
        theme = get_object_or_404(Theme, slug=slug_t)

	param = param + "slug_t=%s" % (str(slug_t),)

    interactive = None
    if settings.H5P_ENABLED:
        from h5pp.models import h5p_contents, h5p_libraries
        from h5pp.h5p.h5pmodule import getUserScore, h5pGetContentId
        if h5p_libraries.objects.filter(machine_name='H5P.InteractiveVideo').count() > 0:
            score = None
            h5p = None
            if h5p_contents.objects.filter(title=video.title).count() > 0:
                h5p = h5p_contents.objects.get(title=video.title)
                if request.user == video.owner or request.user.is_superuser:
                    score = getUserScore(h5p.content_id)
                else:
                    score = getUserScore(h5p.content_id, request.user)
                    if score != None:
                        score = score[0]
            interactive = {'h5p': h5p, 'score': score}

    if video.is_draft:
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('account_login') + '?next=%s' % urlquote(request.get_full_path()))
        else:
            if request.user == video.owner or request.user.is_superuser:
                pass
            else:
                messages.add_message(
                    request, messages.ERROR, _(u'You cannot watch this video.'))
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
                return HttpResponse(_(u'The changes have been saved.'))

    ####### VIDEO PASSWORD #########
    if video.password and not (request.user == video.owner or request.user.is_superuser):
        form = VideoPasswordForm()
        if not request.POST:
            return render_to_response(
                'videos/video.html',
                {'video': video, 'form': form, 'channel': channel,
                    'theme': theme, 'interactive': interactive, 'show_report': show_report},
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
                                'theme': theme, 'interactive': interactive, 'show_report': show_report},
                            context_instance=RequestContext(request)
                        )
                else:
                    messages.add_message(
                        request, messages.ERROR, _(u'Incorrect password'))
                    return render_to_response(
                        'videos/video.html',
                        {'video': video, 'form': form, 'channel': channel,
                            'theme': theme, 'interactive': interactive, 'show_report': show_report},
                        context_instance=RequestContext(request)
                    )
            else:
                messages.add_message(
                    request, messages.ERROR, _(u'One or more errors have been found in the form.'))
                return render_to_response(
                    'videos/video.html',
                    {'video': video, 'form': form, 'channel': channel,
                        'theme': theme, 'interactive': interactive, 'show_report': show_report},
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
                {'video': video, 'channel': channel, 'param': param, 'theme': theme, 'interactive': interactive,
                    'notes_form': notes_form, 'show_report': show_report},
                context_instance=RequestContext(request)
            )
    if request.GET.get('action') and request.GET.get('action') == "download":
        return download_video(video, request.GET)
    else:
        return render_to_response(
            'videos/video.html',
            {'video': video, 'channel': channel, 'param': param,
                'theme': theme, 'interactive': interactive, 'show_report': show_report},
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
        msg = _(u'The video has been added to your favorites.')
        favorite, create = Favorites.objects.get_or_create(
            user=request.user, video=video)
        if not create:
            favorite.delete()
            msg = _(u'The video has been removed from your favorites.')
        if request.is_ajax():
            some_data_to_dump = {'msg': "%s" % msg}
            data = json.dumps(some_data_to_dump)
            return HttpResponse(data, content_type='application/json')
        messages.add_message(request, messages.INFO, msg)
        return HttpResponseRedirect(reverse('pods.views.video', args=(video.slug,)))
    else:
        messages.add_message(
            request, messages.ERROR, _(u'You cannot acces this page.'))
        raise PermissionDenied


@login_required
@csrf_protect
def video_add_report(request, slug):
    video = get_object_or_404(Pod, slug=slug)
    if request.POST and request.POST.get('comment'):
        report = ReportVideo.objects.create(
            user=request.user, video=video, comment='%s' % request.POST['comment'])

        subject = _(u'Video report confirmation')

        msg = _("\nYou just report the video: \"%(title)s\" with this comment: \n\"%(comment)s\".\n"
                "\nAn email has just been sent to us and your request recorded."
                "\nBest regards."
                "\nThe Pod team.") % {'title': video.title, 'comment': '%s' % request.POST['comment']}

        msg_html = _("<p>You just report the video: \"%(title)s\" with this comment:<br/> \"%(comment)s\".</p>"
                     "<p>An email has just been sent to us and your request recorded.</p>"
                     "<p>Best regards</p>"
                     "<p>The Pod team</p>") % {'title': video.title, 'comment': '%s' % request.POST['comment'].replace("\n", "<br/>")}

        email_msg = EmailMultiAlternatives(
            "[" + settings.TITLE_SITE + "]  %s" % subject, msg, settings.DEFAULT_FROM_EMAIL, ['%s' % request.user.email])
        email_msg.attach_alternative(msg_html, "text/html")
        email_msg.send(fail_silently=False)

        subject = _(u'A video has just been reported.')

        msg = _(u'The video intitled "%(video_title)s" has just been reported by %(user_firstname)s %(user_lastname)s <%(user_email)s>.\n'
                'here is the comment posted: \n'
                '%(comment)s\n'
                'here is some more information about the video:\n'
                'Description: %(description)s.\n'
                'url: %(url)s.\n'
                'Video posted by: %(owner_firstname)s %(owner_lastname)s <%(owner_email)s>.\n'
                'Video added on: %(video_date_added)s.\n') % {
                    'video_title': video.title, 'user_firstname': request.user.first_name, 'user_lastname': request.user.last_name,
                    'user_email': request.user.email, 'comment': request.POST['comment'], 'description': video.description,
                    'url': ''.join(['http://', get_current_site(request).domain, video.get_absolute_url()]),
                    'owner_firstname': video.owner.first_name, 'owner_lastname': video.owner.last_name, 'owner_email': video.owner.email,
                    'video_date_added': video.date_added}

        msg_html = _(u'<p>The video intitled "%(video_title)s" has just been reported by %(user_firstname)s %(user_lastname)s &lt;<a href=\"mailto:%(user_email)s\">%(user_email)s</a>&gt;.</p>'
                     '<p>here is the comment posted: <br/>'
                     '%(comment)s</p>'
                     '<p>here is some more information about the video:<br/>'
                     'Description: %(description)s<br/>'
                     'url: <a href=\"%(url)s\">%(url)s</a><br/>'
                     'Video posted by: %(owner_firstname)s %(owner_lastname)s &lt;<a href=\"mailto:%(owner_email)s\">%(owner_email)s&gt;</a>.<br/>'
                     'Video added on: %(video_date_added)s.</p>') % {
            'video_title': video.title, 'user_firstname': request.user.first_name, 'user_lastname': request.user.last_name,
            'user_email': request.user.email, 'comment': request.POST['comment'].replace("\n", "<br/>"), 'description': video.description,
            'url': ''.join(['http://', get_current_site(request).domain, video.get_absolute_url()]),
            'owner_firstname': video.owner.first_name, 'owner_lastname': video.owner.last_name, 'owner_email': video.owner.email,
            'video_date_added': video.date_added}

        email_msg = EmailMultiAlternatives(
            "[" + settings.TITLE_SITE + "]  %s" % subject, msg, settings.DEFAULT_FROM_EMAIL, settings.REPORT_VIDEO_MAIL_TO)
        email_msg.attach_alternative(msg_html, "text/html")
        email_msg.send(fail_silently=False)

        if request.is_ajax():
            msg = _(u'This video has been reported.')
            some_data_to_dump = {'msg': "%s" % msg}
            data = json.dumps(some_data_to_dump)
            return HttpResponse(data, content_type='application/json')

        messages.add_message(request, messages.INFO, msg)
        return HttpResponseRedirect(reverse('pods.views.video', args=(video.slug,)))
    else:
        messages.add_message(
            request, messages.ERROR, _(u'You cannot acces this page.'))
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
                request, messages.INFO, _(u'The changes have been saved.'))
            if request.is_ajax():
                return HttpResponse(_(u'The changes have been saved.'))
            return HttpResponseRedirect(reverse('pods.views.video', args=(video.slug,)))
    else:
        messages.add_message(
            request, messages.ERROR, _(u'You cannot acces this page.'))
        raise PermissionDenied


@csrf_protect
@login_required
def video_edit(request, slug=None):

    global referer

    # Add this to improve folder selection and view list
    if not request.session.get('filer_last_folder_id'):
        from filer.models import Folder
        folder = Folder.objects.get(
            owner=request.user, name=request.user.username)
        request.session['filer_last_folder_id'] = folder.id

    if not request.POST:
        referer = request.META.get('HTTP_REFERER', '/')

    if slug:
        video = get_object_or_404(Pod, slug=slug)
        if request.user != video.owner and not request.user.is_superuser:
            messages.add_message(
                request, messages.ERROR, _(u'You cannot edit this video.'))
            raise PermissionDenied
        video_form = PodForm(request, instance=video)
    else:
        if not request.user.is_superuser and settings.MAX_DAILY_USER_UPLOADS and Pod.objects.filter(
                owner_id=request.user.id,
                date_added=date.today()).count() >= settings.MAX_DAILY_USER_UPLOADS:
            return render_to_response("videos/video_edit.html", {"referer": referer},
                                      context_instance=RequestContext(request))
        else:
            video = None
            video_form = PodForm(request)

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
                request, messages.INFO, _(u'The changes have been saved.'))
            # Without this next line the tags does not appear in search engine
            vid.save()

            # go back
            action = request.POST.get("user_choice")

            if action == "1":
                urlToLoad = reverse('pods.views.video_edit', args=(vid.slug,))
            elif action == "2":
                urlToLoad = "%s" % referer
            else:
                urlToLoad = reverse('pods.views.video', args=(vid.slug,))

            if request.is_ajax():
                response_data = {}
                response_data['success'] = True
                response_data['url'] = "%s" % urlToLoad
                return HttpResponse(json.dumps(response_data), content_type='application/json')
            else:
                return HttpResponseRedirect(urlToLoad)

        else:
            if request.is_ajax():
                response_data = {}
                response_data['success'] = False
                response_data['message'] = _(
                    u'One or more errors have been found in the form.')
                return HttpResponse(json.dumps(response_data), content_type='application/json')
            else:
                messages.add_message(
                    request, messages.ERROR, _(u'One or more errors have been found in the form.'))

    video_ext_accept = replace('|'.join(settings.VIDEO_EXT_ACCEPT), ".", "")
    video_ext_accept_text = replace(
        ', '.join(settings.VIDEO_EXT_ACCEPT), ".", "").upper()

    interactive = None
    if settings.H5P_ENABLED:
        from h5pp.models import h5p_libraries
        if h5p_libraries.objects.filter(machine_name='H5P.InteractiveVideo').count() > 0:
            interactive = True

    return render_to_response("videos/video_edit.html",
                              {'form': video_form, "referer": referer,
                                  "video_ext_accept": video_ext_accept,
                                  "video_ext_accept_text": video_ext_accept_text,
                                  "interactive": interactive},
                              context_instance=RequestContext(request))


@csrf_protect
#@staff_member_required
def video_completion(request, slug):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('account_login') + '?next=%s' % urlquote(request.get_full_path()))
    video = get_object_or_404(Pod, slug=slug)

    # Add this to improve folder selection and view list
    if not request.session.get('filer_last_folder_id'):
        from filer.models import Folder
        folder = Folder.objects.get(
            owner=request.user, name=request.user.username)
        request.session['filer_last_folder_id'] = folder.id

    if request.user != video.owner and not request.user.is_superuser:
        messages.add_message(
            request, messages.ERROR, _(u'You cannot complement this video.'))
        raise PermissionDenied
    else:
        if request.user.is_staff:
            list_contributor = video.contributorpods_set.all()
            list_subtitle = video.trackpods_set.all()
            list_download = video.docpods_set.all()
        else:
            list_contributor = video.contributorpods_set.all()

    interactive = None
    if settings.H5P_ENABLED:
        from h5pp.models import h5p_libraries
        if h5p_libraries.objects.filter(machine_name='H5P.InteractiveVideo').count() > 0:
            interactive = True

    if request.user.is_staff:
        return render_to_response("videos/video_completion.html",
                                  {'video': video,
                                      'list_contributor': list_contributor,
                                      'list_subtitle': list_subtitle,
                                      'list_download': list_download,
                                      'interactive': interactive},
                                  context_instance=RequestContext(request))
    else:
        return render_to_response("videos/video_completion.html",
                                  {'video': video,
                                      'list_contributor': list_contributor,
                                      'interactive': interactive},
                                  context_instance=RequestContext(request))


@csrf_protect
#@staff_member_required
def video_completion_contributor(request, slug):
    if not request.user.is_authenticated():
        raise PermissionDenied

    video = get_object_or_404(Pod, slug=slug)

    if request.user != video.owner and not request.user.is_superuser:
        messages.add_message(
            request, messages.ERROR, _(u'You cannot complement this video.'))
        raise PermissionDenied

    list_contributor = video.contributorpods_set.all()
    list_subtitle = video.trackpods_set.all()
    list_download = video.docpods_set.all()

    if request.POST:  # Contributor CRUD Action
        # new
        if request.POST.get("action") and request.POST['action'] == 'new':
            form_contributor = ContributorPodsForm(initial={"video": video})
            if request.is_ajax():  # if ajax
                return render_to_response("videos/completion/contributor/form_contributor.html",
                                          {'form_contributor': form_contributor,
                                              'video': video},
                                          context_instance=RequestContext(request))
            else:
                return render_to_response("videos/video_completion.html",
                                          {
                                              'video': video,
                                              'list_contributor': list_contributor,
                                              'list_subtitle': list_subtitle,
                                              'list_download': list_download,
                                              'form_contributor': form_contributor
                                          },
                                          context_instance=RequestContext(request))
        # save
        if request.POST.get("action") and request.POST['action'] == 'save':
            form_contributor = None
            if request.POST.get("contributor_id") and request.POST.get("contributor_id") != "None":
                contributor = get_object_or_404(
                    ContributorPods, id=request.POST.get("contributor_id"))
                form_contributor = ContributorPodsForm(
                    request.POST, instance=contributor)
            else:
                form_contributor = ContributorPodsForm(request.POST)

            if form_contributor.is_valid():  # All validation rules pass
                form_contributor.save()
                list_contributor = video.contributorpods_set.all()
                if request.is_ajax():
                    some_data_to_dump = {
                        'list_data': render_to_string('videos/completion/contributor/list_contributor.html', {'list_contributor': list_contributor, 'video': video}, context_instance=RequestContext(request)),
                    }
                    data = json.dumps(some_data_to_dump)
                    return HttpResponse(data, content_type='application/json')
                else:
                    return render_to_response("videos/video_completion.html",
                                              {
                                                  'video': video,
                                                  'list_contributor': list_contributor,
                                                  'list_subtitle': list_subtitle,
                                                  'list_download': list_download
                                              },
                                              context_instance=RequestContext(request))
            else:
                if request.is_ajax():
                    some_data_to_dump = {
                        'errors': "%s" % _('Please correct errors'),
                        'form': render_to_string('videos/completion/contributor/form_contributor.html', {'video': video, 'form_contributor': form_contributor}, context_instance=RequestContext(request))
                    }
                    data = json.dumps(some_data_to_dump)
                    return HttpResponse(data, content_type='application/json')
                else:
                    return render_to_response("videos/video_completion.html",
                                              {
                                                  'video': video,
                                                  'list_contributor': list_contributor,
                                                  'list_subtitle': list_subtitle,
                                                  'list_download': list_download,
                                                  'form_contributor': form_contributor
                                              },
                                              context_instance=RequestContext(request))
        # modify
        if request.POST.get("action") and request.POST['action'] == 'modify':
            contributor = get_object_or_404(
                ContributorPods, id=request.POST['id'])
            form_contributor = ContributorPodsForm(instance=contributor)
            if request.is_ajax():
                return render_to_response("videos/completion/contributor/form_contributor.html",
                                          {'form_contributor': form_contributor,
                                              'video': video},
                                          context_instance=RequestContext(request))
            else:
                return render_to_response("videos/video_completion.html",
                                          {
                                              'video': video,
                                              'list_contributor': list_contributor,
                                              'list_subtitle': list_subtitle,
                                              'list_download': list_download,
                                              'form_contributor': form_contributor
                                          },
                                          context_instance=RequestContext(request))
        # delete
        if request.POST.get("action") and request.POST['action'] == 'delete':
            contributor = get_object_or_404(
                ContributorPods, id=request.POST['id'])
            contributor_delete = contributor.delete()
            list_contributor = video.contributorpods_set.all()
            if request.is_ajax():
                some_data_to_dump = {
                    'list_data': render_to_string('videos/completion/contributor/list_contributor.html',
                                                  {'list_contributor': list_contributor, 'video': video}, context_instance=RequestContext(request))
                }
                data = json.dumps(some_data_to_dump)
                return HttpResponse(data, content_type='application/json')
            else:
                return render_to_response("videos/video_completion.html",
                                          {
                                              'video': video,
                                              'list_contributor': list_contributor,
                                              'list_subtitle': list_subtitle,
                                              'list_download': list_download
                                          },
                                          context_instance=RequestContext(request))

    return render_to_response("videos/video_completion.html",
                              {'video': video,
                                  'list_contributor': list_contributor,
                                  'list_subtitle': list_subtitle,
                                  'list_download': list_download},
                              context_instance=RequestContext(request))


@csrf_protect
#@staff_member_required
def video_completion_subtitle(request, slug):
    if not request.user.is_authenticated() or not request.user.is_staff:
        raise PermissionDenied

    video = get_object_or_404(Pod, slug=slug)

    if request.user != video.owner and not request.user.is_superuser:
        messages.add_message(
            request, messages.ERROR, _(u'You cannot complement this video.'))
        raise PermissionDenied

    list_contributor = video.contributorpods_set.all()
    list_subtitle = video.trackpods_set.all()
    list_download = video.docpods_set.all()

    if request.POST:  # Subtitle CRUD Action
        # new
        if request.POST.get("action") and request.POST['action'] == 'new':
            form_subtitle = TrackPodsForm(initial={"video": video})
            if request.is_ajax():  # if ajax
                return render_to_response("videos/completion/subtitle/form_subtitle.html",
                                          {'form_subtitle': form_subtitle,
                                              'video': video},
                                          context_instance=RequestContext(request))
            else:
                return render_to_response("videos/video_completion.html",
                                          {
                                              'video': video,
                                              'list_contributor': list_contributor,
                                              'list_subtitle': list_subtitle,
                                              'list_download': list_download,
                                              'form_subtitle': form_subtitle
                                          },
                                          context_instance=RequestContext(request))
        # save
        if request.POST.get("action") and request.POST['action'] == 'save':
            form_subtitle = None
            if request.POST.get("subtitle_id") and request.POST.get("subtitle_id") != "None":
                subtitle = get_object_or_404(
                    TrackPods, id=request.POST.get("subtitle_id"))
                form_subtitle = TrackPodsForm(request.POST, instance=subtitle)
            else:
                form_subtitle = TrackPodsForm(request.POST)

            if form_subtitle.is_valid():  # All validation rules pass
                form_subtitle.save()
                list_subtitle = video.trackpods_set.all()
                if request.is_ajax():
                    some_data_to_dump = {
                        'list_data': render_to_string('videos/completion/subtitle/list_subtitle.html', {'list_subtitle': list_subtitle, 'video': video}, context_instance=RequestContext(request)),
                    }
                    data = json.dumps(some_data_to_dump)
                    return HttpResponse(data, content_type='application/json')
                else:
                    return render_to_response("videos/video_completion.html",
                                              {
                                                  'video': video,
                                                  'list_contributor': list_contributor,
                                                  'list_subtitle': list_subtitle,
                                                  'list_download': list_download
                                              },
                                              context_instance=RequestContext(request))
            else:
                if request.is_ajax():
                    some_data_to_dump = {
                        'errors': "%s" % _('Please correct errors'),
                        'form': render_to_string('videos/completion/subtitle/form_subtitle.html', {'video': video, 'form_subtitle': form_subtitle}, context_instance=RequestContext(request))
                    }
                    data = json.dumps(some_data_to_dump)
                    return HttpResponse(data, content_type='application/json')
                else:
                    return render_to_response("videos/video_completion.html",
                                              {
                                                  'video': video,
                                                  'list_contributor': list_contributor,
                                                  'list_subtitle': list_subtitle,
                                                  'list_download': list_download,
                                                  'form_subtitle': form_subtitle
                                              },
                                              context_instance=RequestContext(request))
        # modify
        if request.POST.get("action") and request.POST['action'] == 'modify':
            subtitle = get_object_or_404(TrackPods, id=request.POST['id'])
            form_subtitle = TrackPodsForm(instance=subtitle)
            if request.is_ajax():
                return render_to_response("videos/completion/subtitle/form_subtitle.html",
                                          {'form_subtitle': form_subtitle,
                                              'video': video},
                                          context_instance=RequestContext(request))
            else:
                return render_to_response("videos/video_completion.html",
                                          {
                                              'video': video,
                                              'list_contributor': list_contributor,
                                              'list_subtitle': list_subtitle,
                                              'list_download': list_download,
                                              'form_subtitle': form_subtitle
                                          },
                                          context_instance=RequestContext(request))
        # delete
        if request.POST.get("action") and request.POST['action'] == 'delete':
            subtitle = get_object_or_404(TrackPods, id=request.POST['id'])
            subtitle_delete = subtitle.delete()
            list_subtitle = video.trackpods_set.all()
            if request.is_ajax():
                some_data_to_dump = {
                    'list_data': render_to_string('videos/completion/subtitle/list_subtitle.html', {'list_subtitle': list_subtitle, 'video': video}, context_instance=RequestContext(request))
                }
                data = json.dumps(some_data_to_dump)
                return HttpResponse(data, content_type='application/json')
            else:
                return render_to_response("videos/video_completion.html",
                                          {
                                              'video': video,
                                              'list_contributor': list_contributor,
                                              'list_subtitle': list_subtitle,
                                              'list_download': list_download
                                          },
                                          context_instance=RequestContext(request))

    return render_to_response("videos/video_completion.html",
                              {
                                  'video': video,
                                  'list_contributor': list_contributor,
                                  'list_subtitle': list_subtitle,
                                  'list_download': list_download
                              },
                              context_instance=RequestContext(request))


@csrf_protect
#@staff_member_required
def video_completion_download(request, slug):
    if not request.user.is_authenticated() or not request.user.is_staff:
        raise PermissionDenied
    video = get_object_or_404(Pod, slug=slug)

    if request.user != video.owner and not request.user.is_superuser:
        messages.add_message(
            request, messages.ERROR, _(u'You cannot complement this video.'))
        raise PermissionDenied

    list_contributor = video.contributorpods_set.all()
    list_subtitle = video.trackpods_set.all()
    list_download = video.docpods_set.all()

    if request.POST:  # Download CRUD Action
        # new
        if request.POST.get("action") and request.POST['action'] == 'new':
            form_download = DocPodsForm(initial={"video": video})
            if request.is_ajax():  # if ajax
                return render_to_response("videos/completion/download/form_download.html",
                                          {
                                              'form_download': form_download,
                                              'video': video
                                          },
                                          context_instance=RequestContext(request))
            else:
                return render_to_response("videos/video_completion.html",
                                          {
                                              'video': video,
                                              'list_contributor': list_contributor,
                                              'list_subtitle': list_subtitle,
                                              'list_download': list_download,
                                              'form_download': form_download
                                          },
                                          context_instance=RequestContext(request))
        # save
        if request.POST.get("action") and request.POST['action'] == 'save':
            form_download = None
            if request.POST.get("download_id") and request.POST.get("download_id") != "None":
                download = get_object_or_404(
                    DocPods, id=request.POST.get("download_id"))
                form_download = DocPodsForm(request.POST, instance=download)
            else:
                form_download = DocPodsForm(request.POST)

            if form_download.is_valid():  # All validation rules pass
                form_download.save()
                list_download = video.docpods_set.all()
                if request.is_ajax():
                    some_data_to_dump = {
                        'list_data': render_to_string('videos/completion/download/list_download.html', {'list_download': list_download, 'video': video}, context_instance=RequestContext(request))
                    }
                    data = json.dumps(some_data_to_dump)
                    return HttpResponse(data, content_type='application/json')
                else:
                    return render_to_response("videos/video_completion.html",
                                              {
                                                  'video': video,
                                                  'list_contributor': list_contributor,
                                                  'list_subtitle': list_subtitle,
                                                  'list_download': list_download
                                              },
                                              context_instance=RequestContext(request))
            else:
                if request.is_ajax():
                    some_data_to_dump = {
                        'errors': "%s" % _('Please correct errors'),
                        'form': render_to_string('videos/completion/download/form_download.html', {'video': video, 'form_download': form_download}, context_instance=RequestContext(request))
                    }
                    data = json.dumps(some_data_to_dump)
                    return HttpResponse(data, content_type='application/json')
                else:
                    return render_to_response("videos/video_completion.html",
                                              {
                                                  'video': video,
                                                  'list_contributor': list_contributor,
                                                  'list_subtitle': list_subtitle,
                                                  'list_download': list_download,
                                                  'form_download': form_download
                                              },
                                              context_instance=RequestContext(request))
        # modify
        if request.POST.get("action") and request.POST['action'] == 'modify':
            download = get_object_or_404(DocPods, id=request.POST['id'])
            form_download = DocPodsForm(instance=download)
            if request.is_ajax():
                return render_to_response("videos/completion/download/form_download.html",
                                          {'form_download': form_download,
                                              'video': video},
                                          context_instance=RequestContext(request))
            else:
                return render_to_response("videos/video_completion.html",
                                          {
                                              'video': video,
                                              'list_contributor': list_contributor,
                                              'list_subtitle': list_subtitle,
                                              'list_download': list_download,
                                              'form_download': form_download
                                          },
                                          context_instance=RequestContext(request))
        # delete
        if request.POST.get("action") and request.POST['action'] == 'delete':
            download = get_object_or_404(DocPods, id=request.POST['id'])
            download_delete = download.delete()
            list_download = video.docpods_set.all()
            if request.is_ajax():
                some_data_to_dump = {
                    'list_data': render_to_string('videos/completion/download/list_download.html', {'list_download': list_download, 'video': video}, context_instance=RequestContext(request))
                }
                data = json.dumps(some_data_to_dump)
                return HttpResponse(data, content_type='application/json')
            else:
                return render_to_response("videos/video_completion.html",
                                          {
                                              'video': video,
                                              'list_contributor': list_contributor,
                                              'list_subtitle': list_subtitle,
                                              'list_download': list_download
                                          },
                                          context_instance=RequestContext(request))

    return render_to_response("videos/video_completion.html",
                              {'video': video,
                                  'list_contributor': list_contributor,
                                  'list_subtitle': list_subtitle,
                                  'list_download': list_download},
                              context_instance=RequestContext(request))


@csrf_protect
@login_required
def video_chapter(request, slug):
    video = get_object_or_404(Pod, slug=slug)
    # Add this to improve folder selection and view list
    if not request.session.get('filer_last_folder_id'):
        from filer.models import Folder
        folder = Folder.objects.get(
            owner=request.user, name=request.user.username)
        request.session['filer_last_folder_id'] = folder.id

    if request.user != video.owner and not request.user.is_superuser:
        messages.add_message(
            request, messages.ERROR, _(u'You cannot chapter this video.'))
        raise PermissionDenied

    interactive = None
    if settings.H5P_ENABLED:
        from h5pp.models import h5p_libraries
        if h5p_libraries.objects.filter(machine_name='H5P.InteractiveVideo').count() > 0:
            interactive = True

    # get all chapter video
    list_chapter = video.chapterpods_set.all()
    if request.POST:  # some data sent
        if request.POST.get("action") and request.POST['action'] == 'new':
            form_chapter = ChapterPodsForm(initial={"video": video})
            if request.is_ajax():  # if ajax
                return render_to_response("videos/chapter/form_chapter.html",
                                          {'form_chapter': form_chapter,
                                              'video': video},
                                          context_instance=RequestContext(request))
            else:
                return render_to_response("videos/video_chapter.html",
                                          {'video': video, 'list_chapter': list_chapter,
                                              'form_chapter': form_chapter},
                                          context_instance=RequestContext(request))
        # save
        if request.POST.get("action") and request.POST['action'] == 'save':
            form_chapter = None
            if request.POST.get("chapter_id") != "None":
                chapter = get_object_or_404(
                    ChapterPods, id=request.POST.get("chapter_id"))
                form_chapter = ChapterPodsForm(request.POST, instance=chapter)
            else:
                form_chapter = ChapterPodsForm(request.POST)

            if form_chapter.is_valid():  # All validation rules pass
                form_chapter.save()
                list_chapter = video.chapterpods_set.all()
                if request.is_ajax():
                    some_data_to_dump = {
                        'list_chapter': render_to_string('videos/chapter/list_chapter.html', {'list_chapter': list_chapter, 'video': video}),
                        'player': render_to_string('videos/video_player.html', {'video': video, "csrf_token": request.COOKIES['csrftoken']})
                    }
                    data = json.dumps(some_data_to_dump)
                    return HttpResponse(data, content_type='application/json')
                else:
                    return render_to_response("videos/video_chapter.html",
                                              {'video': video,
                                                  'list_chapter': list_chapter},
                                              context_instance=RequestContext(request))
            else:
                if request.is_ajax():
                    some_data_to_dump = {
                        'errors': "%s" % _('Please correct errors.'),
                        'form': render_to_string('videos/chapter/form_chapter.html', {'video': video, 'form_chapter': form_chapter})
                    }
                    data = json.dumps(some_data_to_dump)
                    return HttpResponse(data, content_type='application/json')
                else:
                    return render_to_response("videos/video_chapter.html",
                                              {'video': video, 'list_chapter': list_chapter,
                                                  'form_chapter': form_chapter},
                                              context_instance=RequestContext(request))
        # end save
        # modify
        if request.POST.get("action") and request.POST['action'] == 'modify':
            chapter = get_object_or_404(ChapterPods, id=request.POST['id'])
            form_chapter = ChapterPodsForm(instance=chapter)
            if request.is_ajax():
                return render_to_response("videos/chapter/form_chapter.html",
                                          {'form_chapter': form_chapter,
                                              'video': video},
                                          context_instance=RequestContext(request))
            else:
                return render_to_response("videos/video_chapter.html",
                                          {'video': video, 'list_chapter': list_chapter,
                                              'form_chapter': form_chapter},
                                          context_instance=RequestContext(request))
        # end modify
        # delete
        if request.POST.get("action") and request.POST['action'] == 'delete':
            chapter = get_object_or_404(ChapterPods, id=request.POST['id'])
            chapter_delete = chapter.delete()
            list_chapter = video.chapterpods_set.all()
            if request.is_ajax():
                some_data_to_dump = {
                    'list_chapter': render_to_string('videos/chapter/list_chapter.html', {'list_chapter': list_chapter, 'video': video}),
                    'player': render_to_string('videos/video_player.html', {'video': video, "csrf_token": request.COOKIES['csrftoken']})
                }
                data = json.dumps(some_data_to_dump)
                return HttpResponse(data, content_type='application/json')
            else:
                return render_to_response("videos/video_chapter.html",
                                          {'video': video,
                                              'list_chapter': list_chapter},
                                          context_instance=RequestContext(request))
        # end delete
        # cancel
        if request.POST.get("action") and request.POST['action'] == 'cancel':
            return render_to_response("videos/video_chapter.html",
                                      {'video': video,
                                          'list_chapter': list_chapter},
                                      context_instance=RequestContext(request))
        # end cancel

    return render_to_response("videos/video_chapter.html",
                              {'video': video, 'list_chapter': list_chapter, 'interactive': interactive},
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
            request, messages.ERROR, _(u'You cannot enrich this video.'))
        raise PermissionDenied

    interactive = None
    if settings.H5P_ENABLED:
        from h5pp.models import h5p_libraries
        if h5p_libraries.objects.filter(machine_name='H5P.InteractiveVideo').count() > 0:
            interactive = True

    # get all video enrich
    list_enrichment = video.enrichpods_set.all()
    if request.POST:  # some data sent
        if request.POST.get("action") and request.POST['action'] == 'new':
            form_enrich = EnrichPodsForm(
                initial={"video": video, "start": 0, "end": 1})
            if request.is_ajax():  # if ajax
                return render_to_response("videos/enrich/form_enrich.html",
                                          {'form_enrich': form_enrich,
                                              'video': video},
                                          context_instance=RequestContext(request))
            else:
                return render_to_response("videos/video_enrich.html",
                                          {'video': video, 'list_enrichment':
                                              list_enrichment, 'form_enrich': form_enrich},
                                          context_instance=RequestContext(request))
        # save
        if request.POST.get("action") and request.POST['action'] == 'save':
            form_enrich = None
            if request.POST.get("enrich_id") != "None":
                enrich = get_object_or_404(
                    EnrichPods, id=request.POST.get("enrich_id"))
                form_enrich = EnrichPodsForm(request.POST, instance=enrich)
            else:
                form_enrich = EnrichPodsForm(request.POST)

            if form_enrich.is_valid():  # All validation rules pass
                form_enrich.save()
                list_enrichment = video.enrichpods_set.all()
                if request.is_ajax():
                    some_data_to_dump = {
                        'list_enrich': render_to_string('videos/enrich/list_enrich.html', {'list_enrichment': list_enrichment, 'video': video}),
                        'player': render_to_string('videos/video_player.html', {'video': video, "csrf_token": request.COOKIES['csrftoken']})
                    }
                    data = json.dumps(some_data_to_dump)
                    return HttpResponse(data, content_type='application/json')
                else:
                    return render_to_response("videos/video_enrich.html",
                                              {'video': video,
                                                  'list_enrichment': list_enrichment},
                                              context_instance=RequestContext(request))
            else:
                if request.is_ajax():
                    some_data_to_dump = {
                        'errors': "%s" % _('Please correct errors.'),
                        'form': render_to_string('videos/enrich/form_enrich.html', {'video': video, 'form_enrich': form_enrich})
                    }
                    data = json.dumps(some_data_to_dump)
                    return HttpResponse(data, content_type='application/json')
                else:
                    return render_to_response("videos/video_enrich.html",
                                              {'video': video, 'list_enrichment':
                                                  list_enrichment, 'form_enrich': form_enrich},
                                              context_instance=RequestContext(request))
        # end save
        # modify
        if request.POST.get("action") and request.POST['action'] == 'modify':
            enrich = get_object_or_404(EnrichPods, id=request.POST['id'])
            form_enrich = EnrichPodsForm(instance=enrich)
            if request.is_ajax():
                return render_to_response("videos/enrich/form_enrich.html",
                                          {'form_enrich': form_enrich,
                                              'video': video},
                                          context_instance=RequestContext(request))
            else:
                return render_to_response("videos/video_enrich.html",
                                          {'video': video, 'list_enrichment':
                                              list_enrichment, 'form_enrich': form_enrich},
                                          context_instance=RequestContext(request))
        # end modify
        # delete
        if request.POST.get("action") and request.POST['action'] == 'delete':
            enrich = get_object_or_404(EnrichPods, id=request.POST['id'])
            enrich_delete = enrich.delete()
            list_enrichment = EnrichPods.objects.filter(video=video)
            if request.is_ajax():
                some_data_to_dump = {
                    'list_enrich': render_to_string('videos/enrich/list_enrich.html', {'list_enrichment': list_enrichment, 'video': video}),
                    'player': render_to_string('videos/video_player.html', {'video': video,  "csrf_token": request.COOKIES['csrftoken']})
                }
                data = json.dumps(some_data_to_dump)
                return HttpResponse(data, content_type='application/json')
            else:
                return render_to_response("videos/video_enrich.html",
                                          {'video': video,
                                              'list_enrichment': list_enrichment},
                                          context_instance=RequestContext(request))
        # end delete
        # cancel
        if request.POST.get("action") and request.POST['action'] == 'cancel':
            return render_to_response("videos/video_enrich.html",
                                      {'video': video,
                                          'list_enrichment': list_enrichment},
                                      context_instance=RequestContext(request))
        # end cancel

    return render_to_response("videos/video_enrich.html",
                              {'video': video,
                                  'list_enrichment': list_enrichment,
                                  'interactive': interactive},
                              context_instance=RequestContext(request))

@csrf_protect
@login_required
@staff_member_required
def video_interactive(request, slug):
  video = get_object_or_404(Pod, slug=slug)
  # Add this to improve folder selection and view list
  if not request.session.get('filer_last_folder_id'):
    from filer.models import Folder
    folder = Folder.objects.get(
      owner=request.user, name=request.user.username)
    request.session['filer_last_folder_id'] = folder.id

  if request.user != video.owner and not request.user.is_superuser:
    messages.add_message(
      request, messages.ERROR, _(u'You cannot add interactivity to this video.'))
    raise PermissionDenied
  
  if 'h5pp' in settings.INSTALLED_APPS:
    from h5pp.models import h5p_contents
    interactive = h5p_contents.objects.filter(slug=slug).values()
    if len(interactive) > 0:
      return render_to_response('videos/video_interactive.html',
				{'video': video,
				'contentId': interactive[0]['content_id'],
				'slug': slug},
				context_instance=RequestContext(request))
    
    return render_to_response('videos/video_interactive.html',
			      {'video': video,
			      'slug': slug},
			      context_instance=RequestContext(request))

  else:
    messages.add_message(
      request, messages.ERROR, _(u'Interactive video is not available in this server.'))
    raise PermissionDenied

@csrf_protect
@login_required
def video_interactive(request, slug, slug_c=None, slug_t=None):
    video = get_object_or_404(Pod, slug=slug)
    channel = None
    if slug_c:
        channel = get_object_or_404(Channel, slug=slug_c)
    theme = None
    if slug_t:
        theme = get_object_or_404(Theme, slug=slug_t)
    interactive = None

    from h5pp.models import h5p_contents, h5p_libraries
    h5p = None
    version = h5p_libraries.objects.get(machine_name='H5P.InteractiveVideo')
    if h5p_contents.objects.filter(title=video.title).count() > 0:
        h5p = h5p_contents.objects.get(title=video.title)
    interactive = {'h5p': h5p, 'version': version}
        
    if request.user.is_authenticated and (request.user == video.owner or request.user.is_superuser):    
        return render_to_response('videos/video_interactive.html',
                                      {'video': video, 'channel': channel, 'theme': theme, 'interactive': interactive},
                                      context_instance=RequestContext(request))
    else:
        messages.add_message(
                request, messages.ERROR, _(u'You cannot watch this video.'))
        raise PermissionDenied

@csrf_protect
@login_required
def video_delete(request, slug):
    video = get_object_or_404(Pod, slug=slug)
    if request.user != video.owner and not request.user.is_superuser:
        messages.add_message(
            request, messages.ERROR, _(u'You cannot delete this video.'))
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
            request, messages.INFO, _(u'The video has been deleted.'))
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
                    request, messages.ERROR, _(u'You cannot watch this video.'))
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
    suggestions = [entry.object.title for entry in res]
    # Make sure you return a JSON object, not a bare list.
    # Otherwise, you could be vulnerable to an XSS attack.
    the_data = json.dumps({})
    return HttpResponse(the_data, content_type='application/json')


def search_videos(request):
    es = Elasticsearch(ES_URL)
    aggsAttrs = ['owner_full_name', 'type.title',
                 'disciplines.title', 'tags.name', 'channels.title']

    # SEARCH FORM
    search_word = ""
    start_date = None
    end_date = None
    searchForm = SearchForm(request.GET)
    if searchForm.is_valid():
        search_word = searchForm.cleaned_data['q']
        start_date = searchForm.cleaned_data['start_date']
        end_date = searchForm.cleaned_data['end_date']

    # request parameters
    selected_facets = request.GET.getlist(
        'selected_facets') if request.GET.getlist('selected_facets') else []
    page = request.GET.get('page') if request.GET.get('page') else 0
    size = request.COOKIES.get('perpage') if request.COOKIES.get(
        'perpage') and request.COOKIES.get('perpage').isdigit() else DEFAULT_PER_PAGE
    #page = request.GET.get('page')
    try:
        page = int(page.encode('utf-8'))
    except:
        page = 0
    try:
        size = int(size.encode('utf-8'))
    except:
        size = DEFAULT_PER_PAGE

    search_from = page * size

    # Filter query
    filter_search = {}
    filter_query = ""
    for facet in selected_facets:
        filter_query += " %s AND" % facet
    else:
        filter_query = filter_query[:-3]

    if filter_query != "":
        filter_search["query"] = {
            "query_string": {
                "query": "%s" % filter_query
            }
        }
    # filter date range
    if start_date or end_date:
        filter_search["range"] = {"date_added": {}}
        if start_date:
            filter_search["range"]["date_added"][
                "gte"] = "%04d-%02d-%02d" % (start_date.year, start_date.month, start_date.day)
        if end_date:
            filter_search["range"]["date_added"][
                "lte"] = "%04d-%02d-%02d" % (end_date.year, end_date.month, end_date.day)

    # Query
    query = {"match_all": {}}
    if search_word != "":
        query = {
            "multi_match": {
                "query":    "%s" % search_word,
                "fields": ["_id", "title^1.1", "owner^0.9", "owner_full_name^0.9", "description^0.6", "tags.name^1",
                           "contributors^0.6", "chapters.title^0.5", "enrichments.title^0.5", "type.title^0.6", "disciplines.title^0.6", "channels.title^0.6"
                           ]
            }
        }

    # bodysearch
    bodysearch = {
        "from": search_from,
        "size": size,
        "query": {},
        "aggs": {},
        "highlight": {
            "pre_tags": ["<strong>"],
            "post_tags": ["</strong>"],
            "fields": {"title": {}}
        }
    }

    bodysearch["query"] = {
        "function_score": {
            "query": {},
            "functions": [
                {
                    "gauss": {
                        "date_added": {
                            "scale": "10d",
                            "offset": "5d",
                            "decay": 0.5
                        }
                    }
                }
            ]
        }
    }

    if filter_search != {}:
        bodysearch["query"]["function_score"]["query"] = {"filtered": {}}
        bodysearch["query"]["function_score"][
            "query"]["filtered"]["query"] = query
        bodysearch["query"]["function_score"]["query"][
            "filtered"]["filter"] = filter_search
    else:
        bodysearch["query"]["function_score"]["query"] = query

    #bodysearch["query"] = query

    for attr in aggsAttrs:
        bodysearch["aggs"][attr.replace(".", "_")] = {
            "terms": {"field": attr + ".raw", "size": 5, "order": {"_count": "asc"}}}

    # add cursus and main_lang 'cursus', 'main_lang',
    bodysearch["aggs"]['cursus'] = {
        "terms": {"field": "cursus", "size": 5, "order": {"_count": "asc"}}}
    bodysearch["aggs"]['main_lang'] = {
        "terms": {"field": "main_lang", "size": 5, "order": {"_count": "asc"}}}

    #print json.dumps(bodysearch, indent=4)

    result = es.search(index="pod", body=bodysearch)

    # Pagination mayby better idea ?
    objects = []
    for i in range(0, result["hits"]["total"]):
        objects.append(i)
    paginator = Paginator(objects, size)
    try:
        search_pagination = paginator.page(page + 1)
    except:
        search_pagination = paginator.page(paginator.num_pages)

    return render_to_response("search/search_video.html",
                              {"result": result, "page": page,
                                  "search_pagination": search_pagination, "form": searchForm},
                              context_instance=RequestContext(request))

####### RECORDER #######


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
