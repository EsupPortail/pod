# -*- coding: utf-8 -*-
"""
Copyright (C) 2014 Nicolas Can
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
from haystack import indexes
from pods.models import Pod
from django.utils import translation
from django.conf import settings

class PodIndex(indexes.SearchIndex, indexes.Indexable):

    
    translation.activate(settings.MODELTRANSLATION_DEFAULT_LANGUAGE)

    text = indexes.CharField(document=True, use_template=True)
    #text = indexes.EdgeNgramField(document=True, use_template=True)
    owner = indexes.CharField(model_attr='owner', faceted=True)
    type = indexes.CharField(model_attr='type', faceted=True)
    date_added = indexes.DateField(model_attr='date_added')
    title = indexes.CharField(model_attr='title', boost=1.125)
    # We add this for autocomplete.
    title_auto = indexes.EdgeNgramField(model_attr='title')
    owner_auto = indexes.EdgeNgramField(model_attr='owner')
    id_auto = indexes.EdgeNgramField(model_attr='id')
    tags = indexes.FacetMultiValueField()
    discipline = indexes.FacetMultiValueField()
    channel = indexes.FacetMultiValueField()
    
    url = indexes.CharField(indexed=False)
    
    def prepare_url(self, obj):
        return obj.get_absolute_url()
        
    def index_queryset(self, using=None):
        #Used when the entire index for model is updated.
        return Pod.objects.filter(is_draft=False, encodingpods__gt=0).distinct()
    
    def prepare_owner(self, obj):
        return "%s" % (obj.owner.get_full_name())
    
    def prepare_owner_auto(self, obj):
        return "%s" % (obj.owner.get_full_name())
    
    def prepare_tags(self, obj):
        # Since we're using a M2M relationship with a complex lookup,
        # we can prepare the list here.
        return [u'%s' %tag.name for tag in obj.tags.all()] #obj.tags.all()#[tag.name for tag in obj.tags.all()]
    
    def prepare_discipline(self, obj):
        # Since we're using a M2M relationship with a complex lookup,
        # we can prepare the list here.
        return [u'%s' %disc.title for disc in obj.discipline.all()] #obj.discipline.all()
        
    def prepare_channel(self, obj):
        # Since we're using a M2M relationship with a complex lookup,
        # we can prepare the list here.
        return [u'%s' %channel.title for channel in obj.channel.all()] #obj.channel.all()
    
    def get_model(self):
        return Pod

