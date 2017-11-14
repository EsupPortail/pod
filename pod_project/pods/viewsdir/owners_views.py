# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _
from paginations import get_pagination
from pods.models import Pod

H5P_ENABLED = getattr(settings, 'H5P_ENABLED', False)
if H5P_ENABLED:
    from h5pp.models import h5p_contents, h5p_libraries
    from h5pp.h5p.h5pmodule import getUserScore, h5pGetContentId

DEFAULT_PER_PAGE = 12
VIDEOS = Pod.objects.filter(is_draft=False, encodingpods__gt=0).distinct()

# OWNERS

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

@login_required
def owner_videos_list(request):
    videos_list = request.user.pod_set.all()

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

    return render_to_response("videos/my_videos.html",
                              {"videos": videos, "interactive": interactive},
                              context_instance=RequestContext(request))