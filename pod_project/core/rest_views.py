from django.contrib.auth.models import User, Group
from core.models import UserProfile
from rest_framework import viewsets
from core.serializers import UserProfileSerializer, UserSerializer, GroupSerializer


class UserProfileViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows userprofiles to be viewed or edited.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class UserViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
