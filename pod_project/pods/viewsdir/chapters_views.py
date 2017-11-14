# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from pods.forms import ChapterPodsForm
from pods.models import ChapterPods, Pod

import simplejson as json

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
                              {'video': video, 'list_chapter': list_chapter,
                                  'interactive': interactive},
                              context_instance=RequestContext(request))