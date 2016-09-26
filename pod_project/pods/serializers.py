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

from pods.models import Pod
from pods.models import Type
from pods.models import EncodingPods
from pods.models import ContributorPods
from pods.models import ChapterPods
from filer.fields.image import FilerImageField
from rest_framework import serializers


class TypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Type
        exclude = ('slug',)
        #fields = ('title', 'description')
        #fields = '__all__'


class PodSerializer(serializers.ModelSerializer):

    class Meta:
        model = Pod
        fields = ('id', 'video', 'title', 'owner', 'type', 'cursus',
                  'main_lang', 'discipline', 'to_encode', 'description')
        read_only_fields = ('encoding_status', 'duration', 'thumbnail')
        #fields = '__all__'


class EncodingPodsSerializer(serializers.ModelSerializer):

    class Meta:
        model = EncodingPods
        fields = '__all__'


class ContributorPodsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContributorPods
        fields = '__all__'


class ChapterPodsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChapterPods
        exclude = ('slug',)

