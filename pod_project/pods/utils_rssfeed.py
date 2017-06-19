from django.contrib.syndication.views import Feed
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Max, Min
from string import replace
from datetime import date, datetime
from HTMLParser import HTMLParser
from models import *

unescape = HTMLParser().unescape

VIDEOS = Pod.objects.filter(is_draft=False, encodingpods__gt=0).distinct()


class MySelectFeed(Feed):
    title = "Test de la fonction RSS"
    link = "/rss/"
    description = "Test feed RSS."

    def get_object(self, request, qparam):

        VIDEOS = Pod.objects.filter(
            is_draft=False, encodingpods__gt=0).distinct()
        filtres = ""

        # Filtres
        if qparam:
            filtres = qparam.replace("'] ", "']&")

        return filtres

    def items(self, obj):

        VIDEOS = Pod.objects.filter(
            is_draft=False, encodingpods__gt=0).distinct()

        if obj:
            obj = obj.encode('utf8')
            param = obj.split("&")

            for p in param:
                k, v = p.split('=')

                if k == 'channel':
                    channel = get_object_or_404(Channel, slug=v)
                    VIDEOS = VIDEOS.filter(channel=channel)
                    self.title = channel.title
                    self.description = unescape(
                        channel.description.replace("<p>", ""))
                    self.description = self.description.replace("</p>", "")

                else:
                    v = (((v.replace('\'', '')).replace(
                        '[', '')).replace(']', '')).replace(', ', ',')
                    lv = v.split(',')
                    if k == 'theme':
                        theme = get_object_or_404(Theme, slug=v)
                        VIDEOS = VIDEOS.filter(theme=theme)
                    if k == 'type':
                        VIDEOS = VIDEOS.filter(type__slug__in=lv)
                    if k == 'discipline':
                        VIDEOS = VIDEOS.filter(discipline__slug__in=lv)
                    if k == 'owner':
                        VIDEOS = VIDEOS.filter(owner__username__in=lv)
                    if k == 'tag':
                        v = v.encode('utf8')
                        VIDEOS = VIDEOS.filter(tags__slug__in=lv)

        return VIDEOS


class MySelectPodVideoHd(Feed):
    title = "Test de la fonction RSS"
    link = "/rss/"
    description = "Test feed RSS."

    def get_object(self, request, qparam):

        VIDEOS = Pod.objects.filter(
            is_draft=False, encodingpods__gt=0).distinct()
        filtres = ""

        # Filtres
        if qparam:
            filtres = qparam.replace("'] ", "']&")

        return filtres

    def items(self, obj):

        VIDEOS = Pod.objects.filter(
            is_draft=False, encodingpods__gt=0).distinct()

        if obj:
            obj = obj.encode('utf8')
            param = obj.split("&")

            for p in param:
                k, v = p.split('=')

                if k == 'channel':
                    channel = get_object_or_404(Channel, slug=v)
                    VIDEOS = VIDEOS.filter(channel=channel)
                    self.title = channel.title
                    self.description = unescape(
                        channel.description.replace("<p>", ""))
                    self.description = self.description.replace("</p>", "")

                else:
                    v = (((v.replace('\'', '')).replace(
                        '[', '')).replace(']', '')).replace(', ', ',')
                    lv = v.split(',')
                    if k == 'theme':
                        theme = get_object_or_404(Theme, slug=v)
                        VIDEOS = VIDEOS.filter(theme=theme)
                    if k == 'type':
                        VIDEOS = VIDEOS.filter(type__slug__in=lv)
                    if k == 'discipline':
                        VIDEOS = VIDEOS.filter(discipline__slug__in=lv)
                    if k == 'owner':
                        VIDEOS = VIDEOS.filter(owner__username__in=lv)
                    if k == 'tag':
                        v = v.encode('utf8')
                        VIDEOS = VIDEOS.filter(tags__slug__in=lv)

        return VIDEOS

    def item_title(self, item):
        return item.owner.get_full_name() + ' | ' + item.title

    def item_description(self, item):
        description = item.description + 'dur&eacute;e : ' + item.duration_in_time()

        return description

    def item_link(self, item):
        link = reverse('pods.views.video', args=(item.slug,))
        ENCODINGS = EncodingPods.objects.filter(
            video=Pod.objects.get(slug=item.slug), encodingFormat="video/mp4")
        resolmax = ENCODINGS.aggregate(Max('encodingType__output_height'))[
            'encodingType__output_height__max']
        link = link + "?action=download&resolution=" + str(resolmax)

        return link

    def item_pubdate(self, item):
        return datetime.strptime(item.date_added.strftime('%Y-%m-%d'), '%Y-%m-%d')


class MySelectPodVideoSd(Feed):
    title = "Test de la fonction RSS"
    link = "/rss/"
    description = "Test feed RSS."

    def get_object(self, request, qparam):

        VIDEOS = Pod.objects.filter(
            is_draft=False, encodingpods__gt=0).distinct()
        filtres = ""

        # Filtres
        if qparam:
            filtres = qparam.replace("'] ", "']&")

        return filtres

    def items(self, obj):

        VIDEOS = Pod.objects.filter(
            is_draft=False, encodingpods__gt=0).distinct()

        if obj:
            obj = obj.encode('utf8')
            param = obj.split("&")

            for p in param:
                k, v = p.split('=')

                if k == 'channel':
                    channel = get_object_or_404(Channel, slug=v)
                    VIDEOS = VIDEOS.filter(channel=channel)
                    self.title = channel.title
                    self.description = unescape(
                        channel.description.replace("<p>", ""))
                    self.description = self.description.replace("</p>", "")

                else:
                    v = (((v.replace('\'', '')).replace(
                        '[', '')).replace(']', '')).replace(', ', ',')
                    lv = v.split(',')
                    if k == 'theme':
                        theme = get_object_or_404(Theme, slug=v)
                        VIDEOS = VIDEOS.filter(theme=theme)
                    if k == 'type':
                        VIDEOS = VIDEOS.filter(type__slug__in=lv)
                    if k == 'discipline':
                        VIDEOS = VIDEOS.filter(discipline__slug__in=lv)
                    if k == 'owner':
                        VIDEOS = VIDEOS.filter(owner__username__in=lv)
                    if k == 'tag':
                        v = v.encode('utf8')
                        VIDEOS = VIDEOS.filter(tags__slug__in=lv)

        return VIDEOS

    def item_title(self, item):
        return item.owner.get_full_name() + ' | ' + item.title

    def item_description(self, item):
        description = item.description + 'dur&eacute;e : ' + item.duration_in_time()

        return description

    def item_link(self, item):
        link = reverse('pods.views.video', args=(item.slug,))
        ENCODINGS = EncodingPods.objects.filter(
            video=Pod.objects.get(slug=item.slug), encodingFormat="video/mp4")
        resolmin = ENCODINGS.aggregate(Min('encodingType__output_height'))[
            'encodingType__output_height__min']
        link = link + "?action=download&resolution=" + str(resolmin)

        return link

    def item_pubdate(self, item):
        return datetime.strptime(item.date_added.strftime('%Y-%m-%d'), '%Y-%m-%d')
