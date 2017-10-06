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
from pods.models import Channel, Type, Discipline, Theme
from django.contrib.auth.models import User
from django.db.models import Count, Prefetch
from django.conf import settings


MENUBAR_HIDE_INACTIVE_OWNERS = getattr(
    settings, 'MENUBAR_HIDE_INACTIVE_OWNERS', False)
MENUBAR_SHOW_STAFF_OWNERS_ONLY = getattr(
    settings, 'MENUBAR_SHOW_STAFF_OWNERS_ONLY', False)


def items_menu_header(request):
    owners_filter_args = {
        'pod__is_draft': False,
        'pod__encodingpods__gt': 0,
    }
    if MENUBAR_HIDE_INACTIVE_OWNERS:
        owners_filter_args['is_active'] = True
    if MENUBAR_SHOW_STAFF_OWNERS_ONLY:
        owners_filter_args['is_staff'] = True
    return {
        'CHANNELS': Channel.objects.filter(
            visible=True, pod__is_draft=False, pod__encodingpods__gt=0
        ).distinct().annotate(
            video_count=Count("pod", distinct=True)
        ).prefetch_related(
            Prefetch("themes", queryset=Theme.objects.filter(
                pod__is_draft=False, pod__encodingpods__gt=0
            ).distinct().annotate(
                video_count=Count("pod", distinct=True)
            ))),
        'TYPES': Type.objects.filter(
            pod__is_draft=False, pod__encodingpods__gt=0
        ).distinct().annotate(video_count=Count("pod", distinct=True)),
        'DISCIPLINES': Discipline.objects.filter(
            pod__is_draft=False, pod__encodingpods__gt=0
        ).distinct().annotate(video_count=Count("pod", distinct=True)),
        'OWNERS': User.objects.filter(**owners_filter_args).order_by(
            'last_name').distinct().annotate(video_count=Count(
                "pod", distinct=True)).prefetch_related("userprofile"),
        'H5P_ENABLED': settings.H5P_ENABLED
    }
