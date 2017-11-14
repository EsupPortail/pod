# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from paginations import get_pagination
from pods.models import Type, Pod

DEFAULT_PER_PAGE = 12
VIDEOS = Pod.objects.filter(is_draft=False, encodingpods__gt=0).distinct()

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
