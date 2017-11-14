# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from pods.forms import EnrichPodsForm
from pods.models import EnrichPods, Pod

import simplejson as json

H5P_ENABLED = getattr(settings, 'H5P_ENABLED', False)
if H5P_ENABLED:
    from h5pp.models import h5p_contents, h5p_libraries
    from h5pp.h5p.h5pmodule import getUserScore, h5pGetContentId


# ENRICHMENT

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

# INTERACTIVE

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

    h5p = None
    version = h5p_libraries.objects.get(machine_name='H5P.InteractiveVideo')
    if video.is_interactive():
        h5p = h5p_contents.objects.get(title=video.title)
    interactive = {'h5p': h5p, 'version': version}

    if request.user == video.owner or request.user.is_superuser:
        return render_to_response('videos/video_interactive.html',
                                  {'video': video, 'channel': channel,
                                      'theme': theme, 'interactive': interactive},
                                  context_instance=RequestContext(request))
    else:
        messages.add_message(
            request, messages.ERROR, _(u'You cannot edit this video.'))
        raise PermissionDenied