# -*- coding: utf-8 -*-

from pods.models import Pod, Type, EncodingPods, ContributorPods, ChapterPods
from rest_framework import viewsets
from pods.serializers import PodSerializer, TypeSerializer, EncodingPodsSerializer, ContributorPodsSerializer, ChapterPodsSerializer
from pods.views import VIDEOS
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import renderers

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

class ContributorPodsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows video to be viewed or edited.
    """
    queryset = ContributorPods.objects.all()
    serializer_class = ContributorPodsSerializer

class EncodingPodsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows video to be viewed or edited.
    """
    queryset = EncodingPods.objects.all()
    serializer_class = EncodingPodsSerializer

class ChapterPodsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows video to be viewed or edited.
    """
    queryset = ChapterPods.objects.all()
    serializer_class = ChapterPodsSerializer
    
class EncodePodView(APIView):
        
    def post(self, request, *args, **kwargs):
        id = request.data.get('id')
        instance = get_object_or_404(Pod, pk=id)
        instance.encoding_in_progress=False
        instance.to_encode=True
        instance.save()
        output_serializer = PodSerializer(instance, context={'request': request})
        return Response(output_serializer.data)
        #{"username":"root"}

class XmlTextRenderer(renderers.BaseRenderer):
    media_type = 'text/xml'
    format = 'xml'
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        return data.encode(self.charset)

from django.template.loader import render_to_string

class DublinCoreView(APIView):
    """
    """
    renderer_classes = (XmlTextRenderer, )

    def get(self, request, format=None):
        xmlcontent="<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
        xmlcontent+="<!DOCTYPE rdf:RDF PUBLIC \"-//DUBLIN CORE//DCMES DTD 2002/07/31//EN\" \n"
        xmlcontent+="\"http://dublincore.org/documents/2002/07/31/dcmes-xml/dcmes-xml-dtd.dtd\">\n"
        xmlcontent+="<rdf:RDF xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\" xmlns:dc =\"http://purl.org/dc/elements/1.1/\">\n"
        for video in VIDEOS:
            rendered = render_to_string('videos/dublincore.html', {'video': video, "xml":True})
            xmlcontent+=rendered
        xmlcontent+="</rdf:RDF>"
        return Response(xmlcontent)



