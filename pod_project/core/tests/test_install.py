# -*- coding: utf-8 -*-
"""
Copyright (C) 2015 Remi Kroll review by Nicolas Can
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
from django.core.files import File
from core.models import *
from django.conf import settings
from django.test import TestCase, override_settings
from pods.models import *
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User, Group
from django.test import Client
from django.test.client import RequestFactory
import threading
import ldap
import urllib3
import shutil
from django.core.files.temp import NamedTemporaryFile
from core.utils import encode_video
import os

@override_settings(
    MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'media'),
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite',
        }
    }
    )
class CasTestView(TestCase):

    def setUp(self):
        print "CasTestView"

    def test_cas(self):
        if settings.USE_CAS == True:
            cas_url = settings.CAS_SERVER_URL
            print " -> cas_url : %s " % cas_url
            http = urllib3.PoolManager()
            r = http.request('GET', cas_url)
            self.assertEqual(r.status, 200)
            print "TEST CAS OK"
        else:
            print "not cas server used USE_CAS is set to False"

@override_settings(
    MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'media'),
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite',
        }
    }
    )
class LdapTestView(TestCase):

    def setUp(self):
        print "LdapTestView"

    def test_ldap(self):
        if settings.USE_CAS == True and settings.USE_LDAP_TO_POPULATE_USER and settings.AUTH_LDAP_UID_TEST != "":
            try:
                l = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
                l.protocol_version = ldap.VERSION3
                if settings.AUTH_LDAP_BIND_DN != '':
                    l.simple_bind_s(
                        settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
                ldap_scope = {
                    'ONELEVEL': ldap.SCOPE_ONELEVEL, 'SUBTREE': ldap.SCOPE_SUBTREE}

                list_value = []
                for val in settings.AUTH_USER_ATTR_MAP.values():
                    list_value.append(str(val))
                try:
                    r = l.search_s(settings.AUTH_LDAP_USER_SEARCH[0], ldap_scope[
                                   settings.AUTH_LDAP_SCOPE], settings.AUTH_LDAP_USER_SEARCH[1] % {"uid": settings.AUTH_LDAP_UID_TEST}, list_value)
                    (dn, attrs) = r[0]  # une seule entree par uid
                    if settings.AUTH_USER_ATTR_MAP.get('first_name') and attrs.get(settings.AUTH_USER_ATTR_MAP['first_name']):
                        # get first value
                        print "First name : %s" % attrs[settings.AUTH_USER_ATTR_MAP['first_name']][0]
                    if settings.AUTH_USER_ATTR_MAP.get('last_name') and attrs.get(settings.AUTH_USER_ATTR_MAP['last_name']):
                        # get first value
                        print "Last name : %s" % attrs[settings.AUTH_USER_ATTR_MAP['last_name']][0]
                    if settings.AUTH_USER_ATTR_MAP.get('email') and attrs.get(settings.AUTH_USER_ATTR_MAP['email']):
                        # get first value
                        print "email : %s" % attrs[settings.AUTH_USER_ATTR_MAP['email']][0]

                    if settings.AUTH_USER_ATTR_MAP.get('affiliation') and attrs.get(settings.AUTH_USER_ATTR_MAP['affiliation']):
                        try:
                            # get first value
                            print "Affiliation : %s" % attrs[settings.AUTH_USER_ATTR_MAP['affiliation']][0]
                            if attrs[settings.AUTH_USER_ATTR_MAP['affiliation']][0] in settings.AFFILIATION_STAFF:
                                print "is staff : True"
                            else:
                                print "is staff : False"
                        except:
                            print u'\n*****Unexpected error link :%s - %s' % (sys.exc_info()[0], sys.exc_info()[1])
                except:
                    print u'\n*****Unexpected error link :%s - %s' % (sys.exc_info()[0], sys.exc_info()[1])
            except ldap.LDAPError, e:
                print e
        else:
            print "not cas server used or not ldap server used USE_LDAP_TO_POPULATE_USER is set to False or settings.AUTH_LDAP_UID_TEST is none"

@override_settings(
    MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'media'),
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite',
        }
    }
    )
class EsTestView(TestCase):

    def setUp(self):
        print "EsTestView"

    def test_es(self):
        es_url = getattr(settings, 'ES_URL', ['http://127.0.0.1:9200/'])
        print "> Elastic search url : %s " % es_url
        http = urllib3.PoolManager()
        r = http.request('GET', es_url[0])
        self.assertEqual(r.status, 200)
        print "\n   --->  test_es of EsTestView : OK ! \n info : \n %s \n" % r.data

@override_settings(
    MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'media'),
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite',
        }
    }
    )
class EncodingFileTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        remi = User.objects.create(username="remi")
        other_type = Type.objects.get(id=1)
        media_guard_hash = get_media_guard("remi", 1)
        file_path = os.path.join(settings.MEDIA_ROOT, 'videos', remi.username, media_guard_hash, 'test.mp4')
        if not os.path.exists(file_path):
            url = "http://pod.univ-lille1.fr/media/pod.mp4"
            print "Download video file from %s" %url
            tempfile = NamedTemporaryFile(delete=True)
            HTTP_PROXY=getattr(settings, 'HTTP_PROXY', None)
            if HTTP_PROXY:
                proxy = urllib3.ProxyManager(settings.HTTP_PROXY)
                with proxy.request('GET', url, preload_content=False) as r, open(tempfile.name, 'wb') as out_file:
                    shutil.copyfileobj(r, out_file)
            else:
                http = urllib3.PoolManager()
                with http.request('GET', url, preload_content=False) as r, open(tempfile.name, 'wb') as out_file:
                    shutil.copyfileobj(r, out_file)
            pod = Pod.objects.create(
                type=other_type, title="Video", owner=remi, video="-", to_encode=False)
            pod.video.save("test.mp4", File(tempfile))
        else :
            print "File already exist"
            pod = Pod.objects.create(
                type=other_type, title="Video", owner=remi, video="-", to_encode=False)
            pod.video.name = os.path.join('videos', remi.username, media_guard_hash, 'test.mp4')
            pod.save()
        print "\n --->  SetUp of EncodingFileTestView : OK !"

    def test_encoding(self):
        remi = User.objects.get(username="remi")
        pod = Pod.objects.get(id=1)
        print "\n ---> lancement Encodage"
        encode_video(pod)
        print "\n ---> Fin Encodage"
        self.assertTrue(
            u'video_1_240.mp4' in pod.get_encoding_240()[0].encodingFile.url)

        ENCODE_WEBM=getattr(settings, 'ENCODE_WEBM', True)
        if ENCODE_WEBM:
            self.assertTrue(
                u'video_1_240.webm' in pod.get_encoding_240()[1].encodingFile.url)
