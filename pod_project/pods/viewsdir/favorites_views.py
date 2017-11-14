# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from paginations import get_pagination
from pods.models import Favorites, Pod

import simplejson as json

H5P_ENABLED = getattr(settings, 'H5P_ENABLED', False)
if H5P_ENABLED:
    from h5pp.models import h5p_contents, h5p_libraries
    from h5pp.h5p.h5pmodule import getUserScore, h5pGetContentId

DEFAULT_PER_PAGE = 12
VIDEOS = Pod.objects.filter(is_draft=False, encodingpods__gt=0).distinct()

# FAVORITES

@login_required
def favorites_videos_list(request):
    videos_list = Pod.objects.filter(
        id__in=request.user.favorites_set.all().values_list('video', flat=True))

    per_page = request.COOKIES.get('perpage') if request.COOKIES.get(
        'perpage') and request.COOKIES.get('perpage').isdigit() else DEFAULT_PER_PAGE

    order_by = request.COOKIES.get('orderby') if request.COOKIES.get(
        'orderby') else "order_by_-date_added"
    if order_by == 'order_by_date_added':
        videos_list = videos_list.order_by('date_added', 'id')
    elif order_by == 'order_by_-date_added':
        videos_list = videos_list.order_by('-date_added', '-id')
    else:
        videos_list = videos_list.order_by(
            "%s" % replace(order_by, "order_by_", ""))

    paginator = Paginator(videos_list, per_page)
    page = request.GET.get('page')

    videos = get_pagination(page, paginator)

    interactive = None
    if H5P_ENABLED:
        if h5p_libraries.objects.filter(machine_name='H5P.InteractiveVideo').count() > 0:
            interactive = True

    if request.is_ajax():
        return render_to_response("videos/videos_list.html",
                                  {"videos": videos},
                                  context_instance=RequestContext(request))

    return render_to_response("favorites/my_favorites.html",
                              {"videos": videos, "interactive": interactive},
                              context_instance=RequestContext(request))

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