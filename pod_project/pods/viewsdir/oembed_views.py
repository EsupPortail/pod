# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

# OEMBED

def video_oembed(request):
    format = request.GET.get('format')
    if format and format !="json":
        HttpResponse.status_code = '501'
        return HttpResponse(_(u'You are not authorized to view this resource'))
    url = request.GET.get('url')
    if not(url):
        HttpResponse.status_code = '404'
        return HttpResponse(_(u'The requested address was not found on this server.'))
    is_video = False
    video_position = url.find("/video/")
    is_video_private = False
    video_priv_position = url.find("/video_priv/")
    if video_position>0:
        is_video = True
    if video_priv_position>0:
        is_video_private = True
    if is_video:
        start = url.find('/video/') + 7
        end = url.find('/', start)
        slug = url[int(start):int(end)]
        try:
            id = int(slug[:find(slug, "-")])
        except ValueError:
            raise SuspiciousOperation('Invalid video id')
        video = get_object_or_404(Pod, id=id)
        if video.is_draft:
            HttpResponse.status_code = '401'
            return HttpResponse(_(u'You are not authorized to view this resource'))
        if video.is_restricted:
            HttpResponse.status_code = '401'
            return HttpResponse(_(u'You are not authorized to view this resource'))
    if is_video_private:
        start = url.find('/video_priv/') + 12
        stop1 = url.find('/', start)
        id = int(url[int(start):int(stop1)])
        stop2 = url.find('/', stop1+1)
        slug = url[int(stop1+1):int(stop2)]
        video = get_object_or_404(Pod, id=id)
        hash_id = get_media_guard(video.owner.username, video.id)
        if hash_id != slug:
            HttpResponse.status_code = '401'
            return HttpResponse("nok : key is not valid")

    if video.get_mediatype()[0] == 'audio':
        type = 'rich'
        thumbnail_url =  settings.STATIC_URL  + settings.DEFAULT_IMG
        thumbnail_width = 256
        thumbnail_height = 144
    else :
        type = video.get_mediatype()[0]
        thumbnail_url = video.thumbnail.url
        thumbnail_width = video.thumbnail.width
        thumbnail_height = video.thumbnail.height

    height = 360
    width = 640
    if request.GET.get('maxheight'):
        height = min(360,int(request.GET.get('maxheight')))
    if request.GET.get('maxwidth'):
        width = min(640,int(request.GET.get('maxwidth')))

    if is_video_private:
        code_integration = '<iframe src="//' + request.META.get('HTTP_HOST') + '/video_priv/' + str(id) + '/' + slug + '/' + '?is_iframe=true" width="' + str(width) + '" height="' + str(height) + '" style="padding: 0; margin: 0; border:0" allowfullscreen ></iframe>'
    else:
        code_integration = '<iframe src="//' + request.META.get('HTTP_HOST') + '/video/' + slug + '?is_iframe=true" width="' + str(width) + '" height="' + str(height) + '" style="padding: 0; margin: 0; border:0" allowfullscreen ></iframe>'
    protocole="http://"
    if request.is_secure():
        protocole="https://"
    some_data_to_dump = {
        'version' : "1.0",
        'provider_name' : settings.TITLE_SITE,
        "provider_url" : protocole + request.META.get('HTTP_HOST') + '/',
        "type" : type,
        "title" : video.title,
        "author_url" :  protocole + request.META.get('HTTP_HOST') + "/videos/?owner=" + video.owner.username,
        "author_name" : video.owner.first_name + " " + video.owner.last_name,
        "width" : width,
        "height" : height,
        "html" : code_integration,
        "thumbnail_url" : protocole + request.META.get('HTTP_HOST') + thumbnail_url,
        "thumbnail_width" : thumbnail_width,
        "thumbnail_height"  : thumbnail_height,
    }
    data = json.dumps(some_data_to_dump)
    return HttpResponse(data, content_type='application/json')