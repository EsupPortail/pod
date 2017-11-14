# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from pods.forms import ContributorPodsForm, DocPodsForm, OverlayPodsForm, TrackPodsForm
from pods.models import ContributorPods, DocPods, OverlayPods, Pod, TrackPods

import simplejson as json

H5P_ENABLED = getattr(settings, 'H5P_ENABLED', False)
if H5P_ENABLED:
    from h5pp.models import h5p_contents, h5p_libraries
    from h5pp.h5p.h5pmodule import getUserScore, h5pGetContentId


# COMPLETION

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
            list_overlay = video.overlaypods_set.all()
        else:
            list_contributor = video.contributorpods_set.all()

    interactive = None
    if H5P_ENABLED:
        if h5p_libraries.objects.filter(machine_name='H5P.InteractiveVideo').count() > 0:
            interactive = True

    if request.user.is_staff:
        return render_to_response("videos/video_completion.html",
                                  {'video': video,
                                      'list_contributor': list_contributor,
                                      'list_subtitle': list_subtitle,
                                      'list_download': list_download,
                                      'list_overlay': list_overlay,
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
#@staff_member_required
def video_completion_overlay(request, slug):
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
    list_overlay = video.overlaypods_set.all()

    if request.POST:
        # New overlay
        if request.POST.get("action") and request.POST['action'] == 'new':
            form_overlay = OverlayPodsForm(initial={"video": video})
            if request.is_ajax():
                return render_to_response("videos/completion/overlay/form_overlay.html",
                                          {
                                              'form_overlay': form_overlay,
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
                                              'list_overlay': list_overlay,
                                              'form_overlay': form_overlay
                                          },
                                          context_instance=RequestContext(request))
        # Save overlay
        if request.POST.get("action") and request.POST['action'] == 'save':
            form_overlay = None
            if request.POST.get("overlay_id") and request.POST.get("overlay_id") != "None":
                overlay = get_object_or_404(
                    OverlayPods, id=request.POST.get("overlay_id"))
                form_overlay = OverlayPodsForm(request.POST, instance=overlay)
            else:
                form_overlay = OverlayPodsForm(request.POST)

            if form_overlay.is_valid():
                form_overlay.save()
                list_overlay = video.overlaypods_set.all()
                if request.is_ajax():
                    some_data_to_dump = {
                        'list_data': render_to_string('videos/completion/overlay/list_overlay.html', {'list_overlay': list_overlay, 'video': video}, context_instance=RequestContext(request))
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
                                                  'list_overlay': list_overlay
                                              },
                                              context_instance=RequestContext(request))
            else:
                if request.is_ajax():
                    some_data_to_dump = {
                        'errors': "%s" % _('Please correct errors'),
                        'form': render_to_string('videos/completion/overlay/form_overlay.html', {'video': video, 'form_overlay': form_overlay}, context_instance=RequestContext(request))
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
                                                  'list_overlay': list_overlay,
                                                  'form_overlay': form_overlay
                                              },
                                              context_instance=RequestContext(request))
        # Modify overlay
        if request.POST.get("action") and request.POST['action'] == 'modify':
            overlay = get_object_or_404(OverlayPods, id=request.POST['id'])
            form_overlay = OverlayPodsForm(instance=overlay)
            if request.is_ajax():
                return render_to_response("videos/completion/overlay/form_overlay.html",
                                          {'form_overlay': form_overlay,
                                           'video': video},
                                          context_instance=RequestContext(request))
            else:
                return render_to_response("videos/video_completion.html",
                                          {
                                              'video': video,
                                              'list_contributor': list_contributor,
                                              'list_subtitle': list_subtitle,
                                              'list_download': list_download,
                                              'list_overlay': list_overlay,
                                              'form_overlay': form_overlay
                                          },
                                          context_instance=RequestContext(request))

        # Delete overlay
        if request.POST.get("action") and request.POST['action'] == 'delete':
            overlay = get_object_or_404(OverlayPods, id=request.POST['id'])
            overlay_delete = overlay.delete()
            list_overlay = video.overlaypods_set.all()
            if request.is_ajax():
                some_data_to_dump = {
                    'list_data': render_to_string('videos/completion/overlay/list_overlay.html', {'list_overlay': list_overlay, 'video': video}, context_instance=RequestContext(request))
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
                                              'list_overlay': list_overlay
                                          },
                                          context_instance=RequestContext(request))
    return render_to_response("videos/video_completion.html",
                              {'video': video,
                               'list_contributor': list_contributor,
                               'list_subtitle': list_subtitle,
                               'list_download': list_download,
                               'list_overlay': list_overlay},
                              context_instance=RequestContext(request))