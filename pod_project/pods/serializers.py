# -*- coding: utf-8 -*-
from pods.models import Pod, Type
from rest_framework import serializers


class TypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Type
        fields = ('title', 'description')


class PodSerializer(serializers.HyperlinkedModelSerializer):
    #type = serializers.HyperlinkedIdentityField(view_name="pods:type")
    #type = TypeSerializer()

    class Meta:
        model = Pod
        fields = ('video', 'title', 'owner', 'type')
