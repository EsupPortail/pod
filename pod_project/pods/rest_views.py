from pods.models import Pod, Type, EncodingPods, ContributorPods, ChapterPods
from rest_framework import viewsets
from pods.serializers import PodSerializer, TypeSerializer, EncodingPodsSerializer, ContributorPodsSerializer, ChapterPodsSerializer
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

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
