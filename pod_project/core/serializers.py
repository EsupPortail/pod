# -*- coding: utf-8 -*-
from django.contrib.auth.models import User, Group
from core.models import UserProfile
from rest_framework import serializers


class UserInputSerializer(serializers.Serializer):
    #id = serializers.IntegerField(min_value=1)
    username = serializers.CharField()

class UserOutputSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('id','url', 'username', 'first_name', 'last_name', 'email', 'groups')


class UserProfileSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = UserProfile
        fields = ('id', 'url', 'user', 'description', 'url', 'auth_type',
                  'affiliation', 'commentaire')  # 'image',


class GroupSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Group
        fields = ('url', 'name')
