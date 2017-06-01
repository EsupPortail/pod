# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Nicolas Can
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

from pods.views import VIDEOS
from pods.models import Pod
from pods.models import Type
from pods.models import EncodingPods
from pods.models import ContributorPods
from pods.models import ChapterPods

from pods.serializers import PodSerializer
from pods.serializers import TypeSerializer
from pods.serializers import EncodingPodsSerializer
from pods.serializers import ContributorPodsSerializer
from pods.serializers import ChapterPodsSerializer

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import renderers
from rest_framework import filters
from django.template.loader import render_to_string


class TypeViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows type to be viewed or edited.
    """
    queryset = Type.objects.all()
    serializer_class = TypeSerializer


class PodViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows video to be viewed or edited.
    """
    queryset = Pod.objects.all().order_by('-date_added')
    serializer_class = PodSerializer
    filter_fields = ('owner', 'type', 'date_added')


class ContributorPodsViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows contributor to be viewed or edited.
    """
    queryset = ContributorPods.objects.all()
    serializer_class = ContributorPodsSerializer


class EncodingPodsViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows encoding to be viewed or edited.
    """
    queryset = EncodingPods.objects.all()
    serializer_class = EncodingPodsSerializer


class ChapterPodsViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows chapter to be viewed or edited.
    """
    queryset = ChapterPods.objects.all()
    serializer_class = ChapterPodsSerializer


class EncodePodView(APIView):

    def post(self, request, *args, **kwargs):
        id = request.data.get('id')
        instance = get_object_or_404(Pod, pk=id)
        instance.encoding_in_progress = False
        instance.to_encode = True
        instance.save()
        output_serializer = PodSerializer(
            instance, context={'request': request})
        return Response(output_serializer.data)
        #{"username":"root"}


class XmlTextRenderer(renderers.BaseRenderer):
    media_type = 'text/xml'
    format = 'xml'
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        if type(data) is dict:
            data_str = ""
            for k, v in data.iteritems():
                data_str += str(k + ': ' + v).encode(self.charset)
            return data_str
        else:
            return data.encode(self.charset)


class DublinCoreView(APIView):

    renderer_classes = (XmlTextRenderer, )

    def get(self, request, format=None):
        list_videos = VIDEOS
        if request.GET:
            list_videos = VIDEOS.filter(**request.GET.dict())
        xmlcontent = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
        xmlcontent += "<!DOCTYPE rdf:RDF PUBLIC \"-//DUBLIN CORE//DCMES DTD 2002/07/31//EN\" \n"
        xmlcontent += "\"http://dublincore.org/documents/2002/07/31/dcmes-xml/dcmes-xml-dtd.dtd\">\n"
        xmlcontent += "<rdf:RDF xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\" xmlns:dc =\"http://purl.org/dc/elements/1.1/\">\n"
        for video in list_videos:
            rendered = render_to_string(
                'videos/dublincore.html', {'video': video, "xml": True})
            xmlcontent += rendered
        xmlcontent += "</rdf:RDF>"
        return Response(xmlcontent)
