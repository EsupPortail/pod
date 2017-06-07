# -*- coding: utf-8 -*-
"""
Copyright (C) 2014 Nicolas Can
Ce programme est un logiciel libre : vous pouvez
le redistribuer et/ou le modifier sous les termes
de la licence GNU Public Licence telle que publiée
par la Free Software Foundation, soit dans la
version 3 de la licence, ou (selon votre choix)
toute version ultérieure.
Ce programme est distribué avec l'espoir
qu'il sera utile, mais SANS AUCUNE
GARANTIE : sans même les garanties
implicites de VALEUR MARCHANDE ou
D'APPLICABILITÉ À UN BUT PRÉCIS. Voir
la licence GNU General Public License
pour plus de détails.
Vous devriez avoir reçu une copie de la licence
GNU General Public Licence
avec ce programme. Si ce n'est pas le cas,
voir http://www.gnu.org/licenses/
"""
from __future__ import unicode_literals

from django.template import Library
from django.template.loader import get_template
from django.template.context import Context
from django.utils.html import escapejs, format_html
from django.utils.safestring import mark_safe
from django.utils.http import urlencode
from django.core.urlresolvers import reverse
from django.conf import settings
import random
import datetime
from django.utils.translation import ugettext_lazy as _
from django.db.models import Count, Case, When, IntegerField, Prefetch
from pods.models import Pod

register = Library()

DOT = '.'
PAGE_VAR = 'page'
HOMEPAGE_SHOWS_PASSWORDED = getattr(settings, 'HOMEPAGE_SHOWS_PASSWORDED', True)
HOMEPAGE_SHOWS_RESTRICTED = getattr(settings, 'HOMEPAGE_SHOWS_RESTRICTED', True)
HOMEPAGE_NBR_CONTENTS_SHOWN = getattr(settings, 'HOMEPAGE_NBR_CONTENTS_SHOWN', 12)


@register.simple_tag(takes_context=True)
def paginator_number(context, cl, i, params, index):
    """
    Generates an individual page index link in a paginated list.
    """
    if i == DOT:
        return '<li class="disabled"><span class="current">... </span></li> '
    elif i == cl.number - 1:
        return format_html('<li class="active"><span class="current">{0}</span> </li>', i + 1)
    else:
        if index == 0:
            query_string = get_query_string(params, {PAGE_VAR: i + 1})
        else:
            query_string = get_query_string(params, {PAGE_VAR: i})
        return format_html('<li><a href="{0}"{1}>{2}</a> </li>',
                           query_string,
                           mark_safe(
                               ' class="end"' if i == cl.paginator.num_pages - 1 else ''),
                           i + 1)


@register.simple_tag()
def dict(params, new_key, new_value):
    old_params = params.copy()
    return get_query_string(old_params, {"%s" % new_key: "%s" % new_value})


@register.simple_tag()
def randomchoices():
    a = ("horizontal", "vertical")
    return random.choice(a)


@register.filter_function
def only_video(queryset):
    #args = [x.strip() for x in args.split(',')]
    return queryset.values_list('video', flat=True)


@register.simple_tag()
def get_query_string(params, new_params=None, remove=None):
    if new_params is None:
        new_params = {}
    if remove is None:
        remove = []
    p = params  # self.params.copy()

    for r in remove:
        for k in list(p):
            if k.startswith(r):
                del p[k]

    for k, v in new_params.items():
        if v is None:
            if k in p:
                del p[k]
        else:
            p[k] = v
    return '?%s' % p.urlencode()  # urlencode(sorted(p.items()))


@register.inclusion_tag('pagination.html', takes_context=True)
def pagination(context, cl, index=1):
    """
    Generates the series of links to the pages in a paginated list.
    """
    try:
        paginator = cl.paginator
        page_num = cl.number - index

        ON_EACH_SIDE = 3
        ON_ENDS = 2

        # If there are 10 or fewer pages, display links to every page.
        # Otherwise, do some fancy
        if paginator.num_pages <= 10:
            page_range = range(paginator.num_pages)
        else:
            # Insert "smart" pagination links, so that there are always ON_ENDS
            # links at either end of the list of pages, and there are always
            # ON_EACH_SIDE links at either end of the "current page" link.
            page_range = []
            if page_num > (ON_EACH_SIDE + ON_ENDS):
                page_range.extend(range(0, ON_ENDS))
                page_range.append(DOT)
                page_range.extend(
                    range(page_num - ON_EACH_SIDE, page_num + index))
            else:
                page_range.extend(range(0, page_num + index))
            if page_num < (paginator.num_pages - ON_EACH_SIDE - ON_ENDS - 1):
                page_range.extend(
                    range(page_num + index, page_num + ON_EACH_SIDE + index))
                page_range.append(DOT)
                page_range.extend(
                    range(paginator.num_pages - ON_ENDS, paginator.num_pages))
            else:
                page_range.extend(range(page_num + index, paginator.num_pages))

        return {
            'cl': cl,
            'page_range': page_range,
            'params': context['request'].GET.copy(),
            '1': 1,
            'index': index
        }
    except:
        return {}


@register.simple_tag()
def user_menu(filter, queryset_user):
    html = ""
    for user in queryset_user.filter(last_name__iregex=r'^%s+' % filter):
        html += "<li class=\"subItem\"><a href=\"%s%s\">%s %s (%s)</a></li>" % (reverse(
            'videos'), "?owner=%s" % user.username, user.last_name, user.first_name, user.video_count)
    return html


@register.simple_tag()
def video_count(obj):
    return obj.pod_set.filter(is_draft=False, encodingpods__gt=0).distinct().count()


@register.simple_tag()
def get_label_lang(lang):
    for tab in settings.ALL_LANG_CHOICES:
        if tab[0] == lang:
            return tab[1]
    return lang


@register.simple_tag()
def get_label_cursus(cursus):
    for tab in settings.CURSUS_CODES:
        if tab[0] == cursus:
            return tab[1]
    return cursus


@register.inclusion_tag("videos/videos_list.html")
def get_last_videos():
    filter_args = {'encodingpods__gt': 0, 'is_draft': False}
    if not HOMEPAGE_SHOWS_PASSWORDED:
        filter_args['password'] = ""
    if not HOMEPAGE_SHOWS_RESTRICTED:
        filter_args['is_restricted'] = False
    return {
        'videos': Pod.objects.filter(**filter_args).exclude(
            channel__visible=0).order_by(
            '-date_added', '-id').distinct()[:HOMEPAGE_NBR_CONTENTS_SHOWN],
        'DEFAULT_IMG': settings.DEFAULT_IMG
    }


@register.simple_tag()
def is_new(video):
    diff = datetime.datetime.now().date() - video.date_added
    if diff.total_seconds() < 604800:
        return '<span class="label label-danger">%s !</span>' % _('New')
    return ""


@register.simple_tag()
def is_new_date(date_added):
    if date_added == "":
        return ""
    date_added = datetime.datetime.strptime(date_added, "%Y-%m-%dT%H:%M:%S")
    diff = datetime.datetime.now().date() - date_added.date()
    if diff.total_seconds() < 604800:
        return '<span class="label label-danger">%s !</span>' % _('New')
    return ""


@register.filter(name='get')
def get(d, k):
    return d.get(k, None)
