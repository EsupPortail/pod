from django.contrib.auth.models import User, Group
from core.models import UserProfile
from rest_framework import viewsets
from core.serializers import UserProfileSerializer, UserOutputSerializer, UserInputSerializer, GroupSerializer
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response


class UserProfileViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows userprofiles to be viewed or edited.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class GetUserView(APIView):

    def get(self, request, *args, **kwargs):
        input_serializer = UserInputSerializer(data=request.query_params)
        input_serializer.is_valid(raise_exception=True)
        instance = get_object_or_404(User, username=input_serializer.data['username'])
        output_serializer = UserOutputSerializer(instance, context={'request': request})
        return Response(output_serializer.data)
        
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        instance = get_object_or_404(User, username=username)
        output_serializer = UserOutputSerializer(instance, context={'request': request})
        return Response(output_serializer.data)
        #{"username":"root"}

class UserViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserOutputSerializer


class GroupViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    
    
