from django.core.management.base import BaseCommand, CommandError
import json
from elasticsearch import Elasticsearch
from django.conf import settings
from elasticsearch.exceptions import TransportError


ES_URL = getattr(settings, 'ES_URL', ['http://127.0.0.1:9200/'])


class Command(BaseCommand):
    args = ''
    help = 'Create the Pod index in leasticsearch engine'

    def handle(self, *args, **options):
        es = Elasticsearch(ES_URL)
        json_data = open('pods/search_template.json')
        es_template = json.load(json_data)
        try:
            create = es.indices.create(index='pod', body=es_template)  # ignore=[400, 404]
        except TransportError as e:
            # (400, u'IndexAlreadyExistsException[[pod] already exists]')
            if e.status_code == 400:
                print "l'index Pod est existant : %s" % e.error
            else:
                print "Une erreur est survenue lors de la creation de l'index : %s-%s" % (e.status_code, e.error)
