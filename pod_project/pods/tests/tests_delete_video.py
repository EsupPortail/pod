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
from filer.models.imagemodels import Image
from django.test import Client
from django.test.client import RequestFactory
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate
from django.forms.models import inlineformset_factory
import threading
from core.utils import encode_video
import os
# Create your tests here.
"""
    test view delete video
"""


@override_settings(
    MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'media'),
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite',
        }
    },
    LANGUAGE_CODE='en'
)
class Video_deleteTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        user = User.objects.create(
            username='remi', password='12345', is_active=True, is_staff=True)
        user.set_password('hello')
        user.save()
        user2 = User.objects.create(
            username='remi2', password='12345', is_active=True)
        user2.set_password('hello')
        user2.save()
        c = Channel.objects.create(title="ChannelTest1", visible=True,
                                   color="Black", style="italic", description="blabla")
        t = Theme.objects.create(
            title="Theme1", channel=c)
        other_type = Type.objects.get(id=1)
        media_guard_hash = get_media_guard("remi", 1)
        pod = Pod.objects.create(type=other_type, title=u'Bunny',
                                 date_added=datetime.today(), owner=user, date_evt=datetime.today(), video=os.path.join("videos", "remi", media_guard_hash, "test.mp4"), overview=os.path.join('videos', 'remi', media_guard_hash, '1', 'overview.jpg'),
                                 allow_downloading=True, duration=33, encoding_in_progress=False, view_count=0, description="fl", is_draft=True,
                                 to_encode=False)
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile=os.path.join("videos", "remi", media_guard_hash, "1", "video_1_240.mp4"), encodingFormat="video/mp4")
        ENCODE_WEBM = getattr(settings, 'ENCODE_WEBM', True)
        if ENCODE_WEBM:
            EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
                id=1), encodingFile=os.path.join("videos", "remi", media_guard_hash, "1", "video_1_240.webm"), encodingFormat="video/webm")
        pod.channel.add(c)
        pod.theme.add(t)
        pod.save()
        print(" --->  SetUp of video_deleteTestView : OK !")

    def test_video_delete(self):
        self.client = Client()
        user = User.objects.get(username="remi")
        user.save()
        user = authenticate(
            username='remi', password='hello')
        login = self.client.login(
            username='remi', password='hello')
        self.assertEqual(login, True)
        pod = Pod.objects.get(id=1)
        response = self.client.get("/video_delete/%s/" % pod.slug)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            "/video_delete/%s/" % pod.slug, {u'action1': [u'delete']})
        self.assertEqual(Pod.objects.all().count(), 0)
        print(
            "   --->  test_video_delete of video_deleteTestView : OK !")

    def test_acces_to_delete_with_other_authenticating(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        user = User.objects.get(username="remi2")
        user.is_staff = False
        user.save()
        user = authenticate(
            username='remi2', password='hello')
        login = self.client.login(
            username='remi2', password='hello')
        self.assertEqual(login, True)
        response = self.client.get("/video_delete/%s/" % pod.slug)
        self.assertEqual(response.status_code, 403)
        self.assertTrue('You cannot delete this video.' in response.content)
        print(
            "   --->  test_acces_to_delete_with_other_authenticating of video_deleteTestView : OK !")
