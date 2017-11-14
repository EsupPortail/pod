# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, date
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify
from django.utils.translation import get_language
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from filer.models import Folder
from paginations import get_pagination
from pods.forms import NotesForm, PodForm, VideoPasswordForm
from pods.models import EncodingPods, Notes, Pod, ReportVideo
from string import find, replace

import simplejson as json

H5P_ENABLED = getattr(settings, 'H5P_ENABLED', False)
if H5P_ENABLED:
    from h5pp.models import h5p_contents, h5p_libraries
    from h5pp.h5p.h5pmodule import getUserScore, h5pGetContentId
USE_PRIVATE_VIDEO = getattr(settings, 'USE_PRIVATE_VIDEO', False)
if USE_PRIVATE_VIDEO:
    from core.models import get_media_guard

DEFAULT_PER_PAGE = 12
VIDEOS = Pod.objects.filter(is_draft=False, encodingpods__gt=0).distinct()

referer = ''

# VIDEOS
## Main views

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
    if order_by == 'order_by_date_added':
        videos_list = videos_list.order_by('date_added', 'id')
    elif order_by == 'order_by_-date_added':
        # Already defined in model, so…
        pass
    else:
        videos_list = videos_list.order_by(
            "%s" % replace(order_by, "order_by_", ""))

    per_page = request.COOKIES.get('perpage') if request.COOKIES.get(
        'perpage') and request.COOKIES.get(
        'perpage').isdigit() else DEFAULT_PER_PAGE

    paginator = Paginator(videos_list, per_page)
    page = request.GET.get('page')

    videos = get_pagination(page, paginator)

    interactive = None
    if settings.H5P_ENABLED:
        if h5p_libraries.objects.filter(machine_name='H5P.InteractiveVideo').count() > 0:
            interactive = True

    if request.is_ajax():
        some_data_to_dump = {
            'json_toolbar': render_to_string('maintoolbar.html',
                                             {'videos': videos, 'param': param}),
            'json_videols': render_to_string('videos/videos_list.html',
                                             {'videos': videos, 'types': type, 'owners': list_owner,
                                                 'disciplines': discipline, 'param': param},
                                             context_instance=RequestContext(request))
        }
        data = json.dumps(some_data_to_dump)
        return HttpResponse(data, content_type='application/json')

    if is_iframe:
        return render_to_response("videos/videos_iframe.html",
                                  {"videos": videos},
                                  context_instance=RequestContext(request))

    return render_to_response("videos/videos.html",
                              {"videos": videos, "types": type, "owners": list_owner,
                                  "disciplines": discipline, "tags_slug": tag, "param": param, "interactive": interactive},
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
    if H5P_ENABLED:
        if h5p_libraries.objects.filter(machine_name='H5P.InteractiveVideo').count() > 0:
            score = None
            h5p = None
            if video.is_interactive():
                h5p = h5p_contents.objects.get(slug=slugify(video.title))
                if request.GET.get('is_iframe') and request.GET.get('interactive'):
                    if request.GET['interactive'] == 'true':
                        return HttpResponseRedirect('/h5p/embed/?contentId=%d' % h5p.content_id)
                if request.user == video.owner or request.user.is_superuser:
                    score = getUserScore(h5p.content_id)
                else:
                    score = getUserScore(h5p.content_id, request.user)
                    if score != None:
                        score = score[0]
            interactive = {'h5p': h5p, 'score': score}

    hash_id = None

    if video.is_draft:
        if USE_PRIVATE_VIDEO:
            hash_id = get_media_guard(video.owner.username, video.id)

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
                    'theme': theme, 'interactive': interactive, 'show_report': show_report, 'hash_id': hash_id},
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
                                'theme': theme, 'interactive': interactive, 'show_report': show_report, 'hash_id': hash_id},
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
                    'notes_form': notes_form, 'show_report': show_report, 'hash_id': hash_id},
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

## Private videos

@csrf_protect
def video_priv(request, id, slug, slug_c=None, slug_t=None):
    try:
        v_id = id
        h_id = slug
    except ValueError:
        raise SuspiciousOperation('Invalid video id')
    video = get_object_or_404(Pod, id=v_id)
    show_report = getattr(settings, 'SHOW_REPORT', False)
    channel = None
    if slug_c:
        channel = get_object_or_404(Channel, slug=slug_c)
    theme = None
    if slug_t:
        theme = get_object_or_404(Theme, slug=slug_t)

    interactive = None
    if H5P_ENABLED:
        if h5p_libraries.objects.filter(machine_name='H5P.InteractiveVideo').count() > 0:
            score = None
            h5p = None
            if video.is_interactive():
                h5p = h5p_contents.objects.get(title=video.title)
                if request.GET.get('is_iframe') and request.GET.get('interactive'):
                    if request.GET['interactive'] == 'true':
                        return HttpResponseRedirect('/h5p/embed/?contentId=%d' % h5p.content_id)
                if request.user == video.owner or request.user.is_superuser:
                    score = getUserScore(h5p.content_id)
                else:
                    score = getUserScore(h5p.content_id, request.user)
                    if score != None:
                        score = score[0]
            interactive = {'h5p': h5p, 'score': score}

    hash_id = get_media_guard(video.owner.username, video.id)
    if hash_id != slug:
        return HttpResponse("nok : key is not valid")

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
                    'theme': theme, 'show_report': show_report, 'interactive': interactive, 'hash_id': hash_id},
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
                                'theme': theme, 'show_report': show_report, 'interactive': interactive, 'hash_id': hash_id},
                            context_instance=RequestContext(request)
                        )
                else:
                    messages.add_message(
                        request, messages.ERROR, _(u'Incorrect password'))
                    return render_to_response(
                        'videos/video.html',
                        {'video': video, 'form': form, 'channel': channel,
                            'theme': theme, 'show_report': show_report},
                        context_instance=RequestContext(request)
                    )
            else:
                messages.add_message(
                    request, messages.ERROR, _(u'One or more errors have been found in the form.'))
                return render_to_response(
                    'videos/video.html',
                    {'video': video, 'form': form, 'channel': channel,
                        'theme': theme, 'show_report': show_report},
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
                    'notes_form': notes_form, 'show_report': show_report, 'interactive': interactive, 'hash_id': hash_id},
                context_instance=RequestContext(request)
            )
    if request.GET.get('action') and request.GET.get('action') == "download":
        return download_video(video, request.GET)
    else:
        return render_to_response(
            'videos/video.html',
            {'video': video, 'channel': channel,
                'theme': theme, 'show_report': show_report, 'interactive': interactive},
            context_instance=RequestContext(request)
        )

## Videos edition

@csrf_protect
@login_required
def video_edit(request, slug=None):

    global referer

    # Add this to improve folder selection and view list
    if not request.session.get('filer_last_folder_id'):
        folder = Folder.objects.get(
            owner=request.user, name=request.user.username)
        request.session['filer_last_folder_id'] = folder.id

    if not request.POST:
        referer = request.META.get('HTTP_REFERER', '/')

    interactive = False
    h5p = None
    if slug:
        # If the edited video is interactive
        if H5P_ENABLED and h5p_libraries.objects.filter(machine_name='H5P.InteractiveVideo').count() > 0:
            interactive = True
            video = get_object_or_404(Pod, slug=slug)
            if video.is_interactive():
                h5p = h5p_contents.objects.get(slug=slugify(video.title))


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
                if settings.EMAIL_ON_ENCODING_COMPLETION and request.user.email:
                    vid.set_encoding_user_email_data(
                        request.user.email,
                        get_language(),
                        "%s://%s" % (
                            request.scheme,
                            request.get_host()
                        )
                    )
                vid.to_encode = True

            # Optional : Update interactive
            if H5P_ENABLED and h5p:
                h5p.title = vid.title
                h5p.slug = slugify(vid.title)
                h5p.save()

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

    return render_to_response("videos/video_edit.html",
                              {'form': video_form, "referer": referer,
                                  "video_ext_accept": video_ext_accept,
                                  "video_ext_accept_text": video_ext_accept_text,
                                  "interactive": interactive},
                              context_instance=RequestContext(request))


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

## VIDEOS OPTIONS

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

## VIDEOS ENCODING

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

def get_video_encoding_private(request, slug, csrftoken, size, type, ext):
    video = get_object_or_404(Pod, slug=slug)
    if video.is_restricted:
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('account_login') + '?next=%s' % urlquote(request.get_full_path()))
    encodingpods = get_object_or_404(EncodingPods,
                                     encodingFormat="%s/%s" % (type, ext), video=video, encodingType__output_height=size)
    return HttpResponseRedirect("%s%s" % (settings.FMS_ROOT_URL, encodingpods.encodingFile.url))