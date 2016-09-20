# -*- coding: utf-8 -*-
from pods.models import Pod, Type, EncodingPods, ContributorPods, ChapterPods
from filer.fields.image import FilerImageField
from rest_framework import serializers


class TypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Type
        #fields = ('title', 'description')
        #fields = '__all__'
        exclude = ('slug',)



class PodSerializer(serializers.ModelSerializer): #serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Pod
        fields = ('id', 'video', 'title', 'owner', 'type', 'cursus', 'main_lang', 'discipline', 'to_encode', 'description')
        read_only_fields = ('encoding_status', 'duration', 'thumbnail')
        #fields = '__all__'


#EncodingPods
class EncodingPodsSerializer(serializers.ModelSerializer):
    #serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EncodingPods
        fields = '__all__'
        
#ContributorPods
class ContributorPodsSerializer(serializers.ModelSerializer):
    #serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ContributorPods
        fields = '__all__'
#ChapterPods
class ChapterPodsSerializer(serializers.ModelSerializer):
    #serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChapterPods
        exclude = ('slug',)
        
        
        
        
