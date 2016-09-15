from pods.models import Pod
from rest_framework import viewsets
from pods.serializers import PodSerializer


class PodViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Pod.objects.all().order_by('-date_added')
    serializer_class = PodSerializer
