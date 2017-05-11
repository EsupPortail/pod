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
import django
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
from pods.forms import ChannelForm, ThemeForm, PodForm, ContributorPodsForm, ChapterPodsForm, EnrichPodsForm
import threading
from core.utils import encode_video
import os
from filer.models.foldermodels import Folder
from filer.models.imagemodels import Image
"""
    test view
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
class ChannelsTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        remi = User.objects.create(username="remi")
        i = 1

        other_type = Type.objects.get(id=1)
        media_guard_hash = get_media_guard("remi", 1)
        pod = Pod.objects.create(type=other_type, title="Video2", encoding_status="b", encoding_in_progress=False,
                                 date_added=datetime.today().date(), owner=remi, date_evt=datetime.today().date(), video=os.path.join("videos", "remi", media_guard_hash, "test.mp4"),
                                 allow_downloading=True, view_count=2, description="fl", overview=os.path.join("videos", "remi", media_guard_hash, "1", "overview.jpg"), is_draft=False,
                                 duration=3, infoVideo="videotest", to_encode=False)
        EncodingPods.objects.create(
                video=pod, encodingType=EncodingType.objects.get(id=1))
        while i <= 15:
            c = Channel.objects.create(title="ChannelTest" + str(i), visible=True,
                                   color="Black", style="italic", description="blabla")
            t = Theme.objects.create(
                    title="Theme" + str(i), channel=Channel.objects.get(id=i))
            pod.channel.add(c)
            pod.theme.add(t)
            i += 1
        pod.save()
        print(" --->  SetUp of ChannelsTestView : OK !")

    def test_channels_with_paginator(self):
        channels = list(Channel.objects.filter(pod__is_draft=False, pod__encodingpods__gt=0).distinct())
        # test when a index of page is a caractere
        response = self.client.get("/channels/?page=a")
        self.assertEqual(response.status_code, 200)
        liste = list(response.context[u"channels"].__dict__["object_list"])
        paginator = Paginator(Channel.objects.filter(pod__is_draft=False, pod__encodingpods__gt=0).distinct(), 12)
        self.assertEqual(liste, channels[:12])

        self.assertEqual(
            response.context[u"channels"].__dict__["number"], paginator.page(1).number)
        self.assertEqual(
            response.context["video_count"], 1)

        # test the second page
        response = self.client.get("/channels/?page=1")
        self.assertEqual(response.status_code, 200)
        liste = list(response.context[u"channels"].__dict__["object_list"])
        self.assertEqual(liste, channels[12:])
        self.assertEqual(
            response.context[u"channels"].__dict__["number"], paginator.page(2).number)
        self.assertEqual(
            response.context["video_count"], 1)
        # test when a index of page is out of range
        response = self.client.get("/channels/?page=1000")
        self.assertEqual(response.status_code, 200)
        liste = list(response.context[u"channels"].__dict__["object_list"])
        self.assertEqual(liste, channels[12:])
        self.assertEqual(
            response.context[u"channels"].__dict__["number"], paginator.page(2).number)
        self.assertEqual(
            response.context["video_count"], 1)
        print(
            "   --->  test_channels_with_paginator of ChannelsTestView : OK !")

    def test_channels_with_ajax_request(self):
        response = self.client.get(
            "/channels/", perpage=24,  HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request[u'REQUEST_METHOD'], 'GET')
        self.assertEqual(response.request['perpage'], 24)
        print(
            "   --->  test_channels_with_ajax_request of ChannelsTestView : OK !")


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
class Owner_channels_listTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        self.user = User.objects.create(
            username='testuser', password='12345', is_active=True, is_staff=True, is_superuser=True)
        self.user.set_password('hello')
        self.user.save()

        remi = User.objects.get(username='testuser')

        i = 1
        while i <= 5:
            c = Channel.objects.create(title="ChannelTest" + str(i), visible=True,
                                       color="Black", style="italic", description="blabla")
            c.owners.add(remi)
            i += 1
        print(" --->  SetUp of Owner_channels_listTestView : OK !")

    def test_owner_channels_list(self):
        self.client = Client()
        self.user = User.objects.get(username="testuser")
        self.user = authenticate(username='testuser', password='hello')
        login = self.client.login(username='testuser', password='hello')
        channels = list(Channel.objects.filter(owners=self.user, pod__is_draft=False, pod__encodingpods__gt=0).distinct())
        self.assertEqual(login, True)
        response = self.client.get("/owner_channels_list/")
        self.assertEqual(response.status_code, 200)
        liste = list(response.context["CHANNELS"])
        self.assertEqual(liste, channels)
        self.assertEqual(response.context["video_count"], 0)
        print(
            "   --->  test_owner_channels_list of Owner_channels_listTestView : OK !")

    def test_owner_channels_with_ajax_request(self):
        self.client = Client()
        self.user = User.objects.get(username="testuser")
        self.user = authenticate(username='testuser', password='hello')
        login = self.client.login(username='testuser', password='hello')
        self.assertEqual(login, True)
        response = self.client.get(
            "/owner_channels_list/", perpage=48,  HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request[u'REQUEST_METHOD'], 'GET')
        self.assertEqual(response.request['perpage'], 48)
        print(
            "   --->  test_owner_channels_with_ajax_request of Owner_channels_listTestView : OK !")


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
class ChannelTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        remi = User.objects.create(username='testuser')
        c = Channel.objects.create(title="ChannelTest1", visible=True,
                                   color="Black", style="italic", description="blabla")
        t = Theme.objects.create(
            title="Theme1", channel=c)
        other_type = Type.objects.get(id=1)
        media_guard_hash = get_media_guard("remi", 1)
        pod = Pod.objects.create(type=other_type, title="Video2", encoding_status="b", encoding_in_progress=True,
                                 date_added=datetime.today().date(), owner=remi, date_evt=datetime.today().date(), video=os.path.join("videos", "remi", media_guard_hash, "test.mp4"),
                                 allow_downloading=True, view_count=2, description="fl", overview=os.path.join("videos", "remi", media_guard_hash, "1", "overview.jpg"), is_draft=False,
                                 duration=3, infoVideo="videotest", to_encode=False)
        pod.save()
        pod.theme.add(t)
        pod.channel.add(Channel.objects.get(id=1))
        pod.save()
        pod.theme.add(t)
        print(" --->  SetUp of ChannelTestView : OK !")

    def test_channel_without_theme_in_argument(self):
        c = Channel.objects.get(id=1)
        self.client = Client()
        response = self.client.get("/%s/" % c.slug)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context[u"channel"], Channel.objects.get(id=1))
        self.assertEqual(
            response.context[u"theme"], None)
        print(
            "   --->  test_channel_without_theme_in_argument of ChannelTestView : OK !")

    def test_channel_with_theme_in_argument(self):
        c = Channel.objects.get(id=1)
        t = Theme.objects.get(id=1)
        self.client = Client()
        response = self.client.get("/%s/%s/" % (c.slug, t.slug))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context[u"channel"], Channel.objects.get(id=1))
        self.assertEqual(
            response.context[u"theme"], Theme.objects.get(channel=Channel.objects.get(id=1)))
        print(
            "   --->  test_channel_with_theme_in_argument of ChannelTestView : OK !")

    def test_channel_with_ajax_request(self):
        c = Channel.objects.get(id=1)
        response = self.client.get(
            "/%s/" % c.slug, perpage=48,  HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request[u'REQUEST_METHOD'], 'GET')
        self.assertEqual(response.request['perpage'], 48)
        print(
            "   --->  test_channel_with_ajax_request of ChannelTestView : OK !")


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
class Channel_edit_TestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        self.user = User.objects.create(
            username='testuser', password='12345', is_active=True, is_staff=True, is_superuser=True)
        self.user.set_password('hello')
        self.user.save()
        user2 = User.objects.create(
            username='testuser2', password='12345', is_active=True, is_staff=True, is_superuser=False)
        user2.set_password('hello')
        user2.save()
        c = Channel.objects.create(title="ChannelTest1", visible=True,
                                   color="Black", style="italic", description="blabla")
        c.owners.add(self.user)
        print(" --->  SetUp of Channel_edit_TestView : OK !")

    def test_channel_edit_get_request(self):
        channel = Channel.objects.get(id=1)
        self.client = Client()
        self.user = User.objects.get(username="testuser")
        self.user = authenticate(username='testuser', password='hello')
        login = self.client.login(username='testuser', password='hello')
        self.assertEqual(login, True)
        response = self.client.get("/%s/edit" % channel.slug)
        self.assertEqual(response.status_code, 200)
        ThemeInlineFormSet = inlineformset_factory(
            Channel, Theme, form=ThemeForm, extra=0)
        formset = ThemeInlineFormSet(instance=channel)
        self.assertEqual(
            response.context['formset'].instance, formset.instance)
        self.assertEqual(response.context['referer'], None)
        self.assertEqual(response.context['form'].instance, channel)
        print(
            "   --->  test_channel_edit_get_request of Channel_edit_TestView : OK !")

    def test_channel_edit_post_request(self):
        channel = Channel.objects.get(id=1)
        self.client = Client()
        self.user = User.objects.get(username="testuser")
        self.user = authenticate(username='testuser', password='hello')
        login = self.client.login(username='testuser', password='hello')
        self.assertEqual(login, True)
        response = self.client.post('/%s/edit' % channel.slug, {u'style': [u'italicdss'], u'description': [u'<p>blabladsvvvv</p>\r\n'], u'action1': [u'Enregistrer'], u'referer': [
                                    u'/%s/edit' % channel.slug], u'themes-TOTAL_FORMS': [u'0'], u'headband': [u''], u'themes-INITIAL_FORMS': [u'0']})
        self.assertEqual(response.status_code, 200)
        self.assertTrue("The changes have been saved." in response.content)
        channel = Channel.objects.get(id=1)
        self.assertEqual(channel.description, u'<p>blabladsvvvv</p>\r\n')
        print(
            "   --->  test_channel_edit_post_request of Channel_edit_TestView : OK !")

    def test_channel_edit_user(self):
        channel = Channel.objects.get(id=1)
        self.client = Client()
        self.user = User.objects.get(username="testuser2")
        self.user = authenticate(username='testuser2', password='hello')
        login = self.client.login(username='testuser2', password='hello')
        self.assertEqual(login, True)
        response = self.client.get('/%s/edit' % channel.slug)
        self.assertEqual(response.status_code, 403)
        self.assertTrue("You cannot edit this channel." in response.content)
        self.assertFalse(channel.description == u'<p>ba</p>\r\n')
        print(
            "   --->  test_channel_edit_user of Channel_edit_TestView : OK !")

    def test_redirection_to_previous_page(self):
        channel = Channel.objects.get(id=1)
        self.client = Client()
        self.user = User.objects.get(username="testuser")
        self.user = authenticate(username='testuser', password='hello')
        login = self.client.login(username='testuser', password='hello')
        self.assertEqual(login, True)
        response = self.client.post('/%s/edit' % channel.slug, {u'description': [u'<p>bl</p>\r\n'], u'action2': [u'Save and back to previous page'], u'referer': [
                                    u'/channels/'], u'themes-TOTAL_FORMS': [u'0'], u'themes-INITIAL_FORMS': [u'0']}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(channel.description, u'<p>bl</p>\r\n')
        self.assertRedirects(
            response, u'/channels/', status_code=302, target_status_code=200, msg_prefix='')
        print(
            "   --->  test_redirection_to_previous_page of Channel_edit_TestView : OK !")

    def test_redirection_to_the_channel(self):
        channel = Channel.objects.get(id=1)
        self.client = Client()
        self.user = User.objects.get(username="testuser")
        self.user = authenticate(username='testuser', password='hello')
        login = self.client.login(username='testuser', password='hello')
        self.assertEqual(login, True)
        response = self.client.post('/%s/edit' % channel.slug, {u'description': [u'<p>bl</p>\r\n'], u'action3': [u'Save and see channel'], u'referer': [
                                    u'/channels/'], u'themes-TOTAL_FORMS': [u'0'], u'themes-INITIAL_FORMS': [u'0']}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(channel.description, u'<p>bl</p>\r\n')
        self.assertRedirects(
            response, u'/%s/' % channel.slug, status_code=302, target_status_code=200, msg_prefix='')
        print(
            "   --->  test_redirection_to_the_channel of Channel_edit_TestView : OK !")


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
class TypesTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        remi = User.objects.create_user(username="remi")
        other_type = Type.objects.get(id=1)
        media_guard_hash = get_media_guard("remi", 1)
        pod = Pod.objects.create(type=other_type, title="Video2", encoding_status="b", encoding_in_progress=True,
                                 date_added=datetime.today().date(), owner=remi, date_evt=datetime.today().date(), video=os.path.join("videos", "remi", media_guard_hash, "test.mp4"),
                                 allow_downloading=True, view_count=2, description="fl", overview=os.path.join("videos", "remi", media_guard_hash, "1", "overview.jpg"), is_draft=False,
                                 duration=3, infoVideo="videotest", to_encode=False)
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile=os.path.join("videos", "remi", media_guard_hash, "1", "video_1_240.mp4"), encodingFormat="video/mp4")
        ENCODE_WEBM = getattr(settings, 'ENCODE_WEBM', True)
        if ENCODE_WEBM:
            EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
                id=1), encodingFile=os.path.join("videos", "remi", media_guard_hash, "1", "video_1_240.webm"), encodingFormat="video/webm")
        pod.save()
        Type.objects.create(title="Type2")
        print(" --->  SetUp of TypesTestView : OK !")

    def test_types(self):
        types = list(Type.objects.filter(pod__is_draft=False, pod__encodingpods__gt=0).distinct())
        response = self.client.get("/types/")
        liste = list(response.context[u"types"].__dict__["object_list"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(liste, types)
        self.assertEqual(response.context["video_count"], 1)
        print("   --->  test_types of TypesTestView : OK !")

    def test_types_with_ajax_request(self):
        response = self.client.get(
            "/types/", perpage=48,  HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request[u'REQUEST_METHOD'], 'GET')
        self.assertEqual(response.request['perpage'], 48)
        print("   --->  test_types_with_ajax_request of TypesTestView : OK !")


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
class OwnersTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        remi = User.objects.create_user(username="Remi", last_name="Lefevbre")
        other_type = Type.objects.get(id=1)
        media_guard_hash = get_media_guard("remi", 1)
        pod = Pod.objects.create(type=other_type, title="Video2", encoding_status="b", encoding_in_progress=True,
                                 date_added=datetime.today().date(), owner=remi, date_evt=datetime.today().date(), video=os.path.join("videos", "remi", media_guard_hash, "test.mp4"),
                                 allow_downloading=True, view_count=2, description="fl", overview=os.path.join("videos", "remi", media_guard_hash, "1", "overview.jpg"), is_draft=False,
                                 duration=3, infoVideo="videotest", to_encode=False)
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile=os.path.join("videos", "remi", media_guard_hash, "1", "video_1_240.mp4"), encodingFormat="video/mp4")
        ENCODE_WEBM = getattr(settings, 'ENCODE_WEBM', True)
        if ENCODE_WEBM:
            EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
                id=1), encodingFile=os.path.join("videos", "remi", media_guard_hash, "1", "video_1_240.webm"), encodingFormat="video/webm")
        pod.save()
        print(" --->  SetUp of OwnersTestView : OK !")

    def test_owners(self):
        owners = list(User.objects.filter(
            pod__in=Pod.objects.filter(is_draft=False, encodingpods__gt=0)))
        response = self.client.get("/owners/")
        liste = list(response.context[u"owners"].__dict__["object_list"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(liste, owners)
        self.assertEqual(response.context["video_count"], 1)
        print("   --->  test_owners of OwnersTestView : OK !")

    def test_owners_with_filter_in_argument(self):
        owners = list(User.objects.filter(
            pod__in=Pod.objects.filter(is_draft=False, encodingpods__gt=0)))
        self.client = Client()
        response = self.client.get("/owners/?owners_filter=[a-d]")
        nbowners = response.context[u"owners"].__dict__["object_list"].count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(nbowners, 0)
        response = self.client.get("/owners/?owners_filter=[i-l]")
        liste = list(response.context[u"owners"].__dict__["object_list"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(liste, owners)
        print(
            "   --->  test_owners_with_filter_in_argument of OwnersTestView : OK !")

    def test_owners_with_ajax_request(self):

        response = self.client.get(
            "/owners/", perpage=24,  HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request[u'REQUEST_METHOD'], 'GET')
        self.assertEqual(response.request['perpage'], 24)
        print(
            "   --->  test_owners_with_ajax_request of OwnersTestView : OK !")


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
class DisciplinesTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        remi = User.objects.create_user(username="remi")
        Discipline.objects.create(title="Discipline1")
        other_type = Type.objects.get(id=1)
        d1 = Discipline.objects.create(title="Discipline2")
        media_guard_hash = get_media_guard("remi", 1)
        pod = Pod.objects.create(type=other_type, title="Video2", encoding_status="b", encoding_in_progress=True,
                                 date_added=datetime.today().date(), owner=remi, date_evt=datetime.today().date(), video=os.path.join("videos", "remi", media_guard_hash, "test.mp4"),
                                 allow_downloading=True, view_count=2, description="fl", overview=os.path.join("videos", "remi", media_guard_hash, "1", "overview.jpg"), is_draft=False,
                                 duration=3, infoVideo="videotest", to_encode=False)
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile=os.path.join("videos", "remi", media_guard_hash, "1", "video_1_240.mp4"), encodingFormat="video/mp4")
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile=os.path.join("videos", "remi", media_guard_hash, "1", "video_1_240.webm"), encodingFormat="video/webm")
        pod.discipline.add(d1)
        pod.save()
        print(" --->  SetUp of DisciplinesTestView : OK !")

    def test_disciplines(self):
        disciplines = list(Discipline.objects.filter(pod__is_draft=False, pod__encodingpods__gt=0).distinct())
        response = self.client.get("/disciplines/")
        liste = list(response.context[u"disciplines"].__dict__["object_list"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(liste, disciplines)
        self.assertEqual(response.context["video_count"], 1)
        print("   --->  test_disciplines of DisciplinesTestView : OK !")

    def test_disciplines_with_ajax_request(self):
        response = self.client.get(
            "/disciplines/", perpage=24,  HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request[u'REQUEST_METHOD'], 'GET')
        self.assertEqual(response.request['perpage'], 24)
        print(
            "   --->  test_disciplines_with_ajax_request of DisciplinesTestView : OK !")


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
class Owner_Videos_listTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        self.user = User.objects.create(
            username='testuser', password='12345', is_active=True, is_staff=True, is_superuser=True)
        self.user.set_password('hello')
        self.user.save()
        other_type = Type.objects.get(id=1)
        media_guard_hash = get_media_guard("remi", 1)
        i = 1
        while i < 3:
            pod = Pod.objects.create(type=other_type, title="Video" + str(i), encoding_status="b", encoding_in_progress=True,
                                     date_added=datetime.today().date(), owner=self.user, date_evt=datetime.today().date(), video=os.path.join("videos", "remi", media_guard_hash, "test.mp4"),
                                     allow_downloading=True, view_count=2, description="fl", overview=os.path.join("videos", "remi", media_guard_hash, "1", "overview.jpg"), is_draft=False,
                                     duration=3, infoVideo="videotest", to_encode=False)

            pod.save()
            i += 1
        print(" --->  SetUp of Owner_Videos_listTestView : OK !")

    def test_owners_video_list(self):
        self.client = Client()
        self.user = User.objects.get(username="testuser")
        self.user = authenticate(username='testuser', password='hello')
        login = self.client.login(username='testuser', password='hello')
        videos = list(Pod.objects.filter(owner=self.user))
        self.assertEqual(login, True)
        response = self.client.get("/owner_videos_list/")
        self.assertEqual(response.status_code, 200)
        liste = list(response.context["videos"])
        self.assertEqual(liste, videos)
        print(
            "   --->  test_owners_video_list of Owner_Videos_listTestView : OK !")

    def test_owners_video_list_with_ajax_request(self):
        self.client = Client()
        self.user = User.objects.get(username="testuser")
        self.user = authenticate(username='testuser', password='hello')
        login = self.client.login(username='testuser', password='hello')
        self.assertEqual(login, True)
        response = self.client.get(
            "/owner_videos_list/", perpage=24,  HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request[u'REQUEST_METHOD'], 'GET')
        self.assertEqual(response.request['perpage'], 24)
        print(
            "   --->  test_owners_video_list_with_ajax_request of Owner_Videos_listTestView : OK !")


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
class Tags_TestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        remi = User.objects.create_user(username="remi")
        other_type = Type.objects.get(id=1)
        media_guard_hash = get_media_guard("remi", 1)
        pod = Pod.objects.create(type=other_type, title="Video2", encoding_status="b", encoding_in_progress=True,
                                 date_added=datetime.today().date(), owner=remi, date_evt=datetime.today().date(), video=os.path.join("videos", "remi", media_guard_hash, "test.mp4"),
                                 allow_downloading=True, view_count=2, description="fl", overview=os.path.join("videos", "remi", media_guard_hash, "1", "overview.jpg"), is_draft=False,
                                 duration=3, infoVideo="videotest", to_encode=False)
        pod.tags.add(u"testtagVideo2")
        pod.tags.add(u"téstàvecâccent")
        pod.save()
        print(" --->  SetUp of Tags_TestView : OK !")

    def test_tags(self):
        pod = Pod.objects.get(id=1)
        response = self.client.get("/tags/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(pod.tags.get(id=1).name, u"testtagvideo2")
        self.assertEqual(pod.tags.get(id=2).name, u'testavecaccent')
        pod.tags.add("TESTTAGVIDEO2")
        self.assertEqual(pod.tags.all().count(), 2)
        print("   --->  test_tags of Tags_TestView : OK !")


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
class Video_add_favoriteTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        user = User.objects.create(
            username='testuser', password='12345', is_active=True, is_staff=False)
        user.set_password('hello')
        user.save()
        user2 = User.objects.create(
            username='testuser2', password='12345', is_active=True, is_staff=False)
        user2.set_password('hello')
        user2.save()
        other_type = Type.objects.get(id=1)
        media_guard_hash = get_media_guard("remi", 1)
        pod = Pod.objects.create(type=other_type, title="Video2", encoding_status="b", encoding_in_progress=True,
                                 date_added=datetime.today().date(), owner=user2, date_evt=datetime.today().date(), video=os.path.join("videos", "remi", media_guard_hash, "test.mp4"),
                                 allow_downloading=True, view_count=2, description="fl", overview=os.path.join("videos", "remi", media_guard_hash, "1", "overview.jpg"), is_draft=False,
                                 duration=3, infoVideo="videotest", to_encode=False)
        pod.save()
        print(" --->  SetUp of Video_add_favoriteTestView : OK !")

    def test_add_favorite(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        self.user = User.objects.get(username="testuser")
        self.user = authenticate(username='testuser', password='hello')
        login = self.client.login(username='testuser', password='hello')
        self.assertEqual(login, True)
        response = self.client.post(
            "/video_add_favorite/%s/" % pod.slug, {'submit': ['true']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Favorites.objects.get(user=self.user).video, Pod.objects.get(id=1))

        print(
            "   --->  test_add_favorite_with_ajax_requete of Video_add_favoriteTestView : OK !")

    def test_video_edit_not_good_user(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        user = User.objects.get(username="testuser2")
        user = authenticate(username='testuser2', password='hello')
        login = self.client.login(username='testuser2', password='hello')
        self.assertEqual(login, True)
        response = self.client.get('/video_add_favorite/%s/' % pod.slug)
        self.assertEqual(response.status_code, 403)
        self.assertTrue("You cannot acces this page." in response.content)

    def test_delete_favorite(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        self.user = User.objects.get(username="testuser")
        self.user = authenticate(username='testuser', password='hello')
        login = self.client.login(username='testuser', password='hello')
        self.assertEqual(login, True)
        Favorites.objects.create(user=self.user, video=Pod.objects.get(id=1))
        response2 = self.client.post(
            "/video_add_favorite/%s/" % pod.slug, {'submit': ['true']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(Favorites.objects.filter(user=self.user).count(), 0)
        print(
            "   --->  test_delete_favorite of Video_add_favoriteTestView : OK !")


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
class Video_add_reportTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        user = User.objects.create(
            username='testuser', password='12345', is_active=True, is_staff=False)
        user.set_password('hello')
        user.save()
        user2 = User.objects.create(
            username='testuser2', password='12345', is_active=True, is_staff=False)
        user2.set_password('hello')
        user2.save()
        other_type = Type.objects.get(id=1)
        media_guard_hash = get_media_guard("remi", 1)
        pod = Pod.objects.create(type=other_type, title="Video2", encoding_status="b", encoding_in_progress=True,
                                 date_added=datetime.today().date(), owner=user2, date_evt=datetime.today().date(), video=os.path.join("videos", "remi", media_guard_hash, "test.mp4"),
                                 allow_downloading=True, view_count=2, description="fl", overview=os.path.join("videos", "remi", media_guard_hash, "1", "overview.jpg"), is_draft=False,
                                 duration=3, infoVideo="videotest", to_encode=False)
        pod.save()
        print(" --->  SetUp of Video_add_reportTestView : OK !")

    def test_add_report(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        self.user = User.objects.get(username="testuser")
        self.user = authenticate(username='testuser', password='hello')
        login = self.client.login(username='testuser', password='hello')
        self.assertEqual(login, True)
        response = self.client.post(
            "/video_add_report/%s/" % pod.slug, {'submit': ['true']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            "/video_add_report/%s/" % pod.slug, {'comment': ['message']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        reportVideo = ReportVideo.objects.get(video=pod)
        self.assertEqual(reportVideo.user, self.user)
        self.assertEqual(reportVideo.comment, "message")
        print(
            "   --->  test_add_report of Video_add_reportTestView : OK !")

    def test_add_report_with_not_authentificate(self):
        pod = Pod.objects.get(id=1)
        response = self.client.post(
            "/video_add_report/%s/" % pod.slug, {'comment': ['message']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse('account_login') + '?next=/video_add_report/%s/' % pod.slug, status_code=302, target_status_code=200, msg_prefix='')
        print(
            "   --->  test_add_report_with_not_authentificate of Video_add_reportTestView : OK !")


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
class Favorites_videos_listTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        user = User.objects.create(
            username='testuser', password='12345', is_active=True, is_staff=False)
        user.set_password('hello')
        user.save()
        user2 = User.objects.create(
            username='testuser2', password='12345', is_active=True, is_staff=False)
        user2.set_password('hello')
        user2.save()
        other_type = Type.objects.get(id=1)
        media_guard_hash = get_media_guard("remi", 1)
        i = 1
        while i < 5:
            pod = Pod.objects.create(type=other_type, title="Video" + str(i), encoding_status="b", encoding_in_progress=True,
                                     date_added=datetime.today().date(), owner=user2, date_evt=datetime.today().date(), video=os.path.join("videos", "remi", media_guard_hash, "test.mp4"),
                                     allow_downloading=True, view_count=2, description="fl", overview=os.path.join("videos", "remi", media_guard_hash, "1", "overview.jpg"), is_draft=False,
                                     duration=3, infoVideo="videotest", to_encode=False)
            pod.save()
            i += 1
        print(" --->  SetUp of Favorites_videos_listTestView : OK !")

    def test_favorites_video_list(self):
        #csrf_client = Client(enforce_csrf_checks=True)
        self.client = Client()
        self.user = User.objects.get(username="testuser")
        self.user = authenticate(username='testuser', password='hello')
        login = self.client.login(username='testuser', password='hello')
        self.assertEqual(login, True)
        i = 1
        while i < 5:
            response = self.client.post(
                "/video_add_favorite/000" + str(i) + "-video" + str(i) + "/", {'submit': ['true']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(response.status_code, 200)
            i += 1
        videos = list(Pod.objects.all())
        response = self.client.get("/favorites_videos_list/")
        self.assertEqual(response.status_code, 200)
        liste = list(response.context["videos"])
        self.assertEqual(liste, videos)
        print(
            "   --->  test_favorites_video_list of Favorites_videos_listTestView : OK !")

    def test_favorites_video_list_with_ajax_request(self):
        self.client = Client()
        self.user = User.objects.get(username="testuser")
        self.user = authenticate(username='testuser', password='hello')
        login = self.client.login(username='testuser', password='hello')
        self.assertEqual(login, True)
        response = self.client.get(
            "/favorites_videos_list/", perpage=24,  HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request[u'REQUEST_METHOD'], 'GET')
        self.assertEqual(response.request['perpage'], 24)
        print(
            "   --->  test_favorites_video_list_with_ajax_request of Favorites_videos_listTestView : OK !")


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
class VideosTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        d1 = Discipline.objects.create(title="Discipline1")
        user = User.objects.create(
            username='remi', last_name="lefevbre",  password='12345', is_active=True, is_staff=False)
        user.set_password('hello')
        user.save()
        type1 = Type.objects.create(title="type1")
        media_guard_hash = get_media_guard("remi", 1)
        i = 1
        while i < 5:
            pod = Pod.objects.create(type=type1, title="Video" + str(i), encoding_status="b", encoding_in_progress=True,
                                     date_added=datetime.today().date(), owner=user, date_evt=datetime.today().date(), video=os.path.join("videos", "remi", media_guard_hash, "test.mp4"),
                                     allow_downloading=True, view_count=0, description="fl", overview=os.path.join("videos", "remi", media_guard_hash, "1", "overview.jpg"), is_draft=False,
                                     duration=3, infoVideo="videotest", to_encode=False)
            EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
                id=1), encodingFile=os.path.join("media", "videos", "remi", media_guard_hash, "1", "video_1_240.mp4"))
            ENCODE_WEBM = getattr(settings, 'ENCODE_WEBM', True)
            if ENCODE_WEBM:
                EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
                    id=1), encodingFile=os.path.join("media", "videos", "remi", media_guard_hash, "1", "video_1_240.webm"))
            pod.tags.add("videotests")
            if i % 2:
                pod.discipline.add(d1)
            pod.save()
            i += 1
        print(" --->  SetUp of videosTestView : OK !")

    def test_videos_discipline_filtre(self):
        d1 = Discipline.objects.get(id=1)
        videos = list(Pod.objects.filter(discipline=d1))
        response = self.client.get(
            "/videos/?discipline=discipline1&type=type1")
        liste_videos = list(response.context["videos"].__dict__["object_list"])
        liste_discipline = response.context["disciplines"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(liste_videos, videos)
        self.assertEqual(
            liste_discipline[0], list(Discipline.objects.all())[0].title.lower())
        print(
            "   --->  test_videos_discipline_filtre of videosTestView : OK !")

    def test_videos_owners_filtre(self):
        videos = Pod.objects.filter(owner=User.objects.get(id=1))
        owner = User.objects.get(id=1)
        response = self.client.get("/videos/?owner=remi")
        self.assertEqual(response.status_code, 200)
        liste_videos = list(response.context["videos"].__dict__["object_list"])
        self.assertEqual(liste_videos, list(videos))
        print(
            "   --->  test_videos_owners_filtre of videosTestView : OK !")

    def test_videos_with_ajax_request(self):
        response = self.client.get(
            "/videos/", perpage=24,  HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request[u'REQUEST_METHOD'], 'GET')
        self.assertEqual(response.request['perpage'], 24)
        print(
            "   --->  test_videos_with_ajax_request of videosTestView : OK !")


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
class VideoTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        user = User.objects.create(
            username='remi', password='12345', is_active=True)
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
        type1 = Type.objects.create(title="type1")
        media_guard_hash = get_media_guard("remi", 1)
        pod = Pod.objects.create(type=type1, title=u'Bunny',
                                 date_added=datetime.today().date(), owner=user, date_evt=datetime.today().date(), video=os.path.join("videos", "remi", media_guard_hash, "test.mp4"), overview=os.path.join('videos', 'remi', media_guard_hash, '1', 'overview.jpg'),
                                 allow_downloading=False, duration=33, encoding_in_progress=False, view_count=0, description="fl", is_draft=True,
                                 to_encode=False)

        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile=os.path.join('videos', 'remi', media_guard_hash, '1', 'video_1_240.mp4'), encodingFormat="video/mp4")

        ENCODE_WEBM = getattr(settings, 'ENCODE_WEBM', True)
        if ENCODE_WEBM:
            EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
                id=1), encodingFile=os.path.join("videos", "remi", media_guard_hash, "1", "video_1_240.webm"), encodingFormat="video/webm")

        pod.channel.add(c)
        pod.theme.add(t)
        pod.save()
        print(" --->  SetUp of videoTestView : OK !")

    def test_video(self):
        pod = Pod.objects.get(id=1)
        response = self.client.get("/video/%s/" % pod.slug)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse('account_login') + '?next=/video/%s/' % pod.slug, status_code=302, target_status_code=200, msg_prefix='')
        pod = Pod.objects.get(id=1)
        pod.is_restricted = True
        pod.is_draft = False
        pod.save()
        response = self.client.get("/video/%s/" % pod.slug)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse('account_login') + '?next=/video/%s/' % pod.slug, status_code=302, target_status_code=200, msg_prefix='')
        print(
            "   --->  test_video of VideoTestView : OK !")

    def test_video_draft_not_good_user(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        user = User.objects.get(id=1)
        user = authenticate(username='remi2', password='hello')
        login = self.client.login(username='remi2', password='hello')
        self.assertEqual(login, True)
        response = self.client.get("/video/%s/" % pod.slug)
        self.assertEqual(response.status_code, 403)
        self.assertTrue("You cannot watch this video." in response.content)
        print(
            "   --->  test_video_draft_not_good_user of VideoTestView : OK !")

    def test_video_with_authenticated(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        user = User.objects.get(id=1)
        user = authenticate(username='remi', password='hello')
        login = self.client.login(username='remi', password='hello')
        self.assertEqual(login, True)
        response = self.client.get("/video/%s/" % pod.slug)
        self.assertEqual(response.status_code, 200)
        pod.is_draft = False
        pod.save()
        self.client = Client()
        user = User.objects.get(id=2)
        user = authenticate(username='remi2', password='hello')
        login = self.client.login(username='remi2', password='hello')
        self.assertEqual(login, True)
        response = self.client.get("/video/%s/" % pod.slug)
        self.assertEqual(response.status_code, 200)
        print(
            "   --->  test_video_with_authenticated of VideoTestView : OK !")

    def test_video_password(self):
        pod = Pod.objects.get(id=1)
        pod.is_draft = False
        pod.password = u"toto"
        pod.save()
        self.client = Client()
        c = Channel.objects.get(id=1)
        response = self.client.post(
            "/%s/video/%s/" % (c.slug, pod.slug), {u'password': [u'toto'], u'action1': [u'Send']})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context[u'channel'], Channel.objects.get(id=1))
        self.assertEqual(response.context[u'video'], pod)
        response = self.client.post(
            "/video/%s/" % pod.slug, {u'password': [u'toto2'], u'action1': [u'Send']})
        self.assertEqual(response.status_code, 200)

        print(
            "   --->  test_video_password of VideoTestView : OK !")


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
class Video_edit_testCase(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        user = User.objects.create(
            username='remi', password='12345', is_active=True)
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
                                 date_added=datetime.today().date(), owner=user, date_evt=datetime.today().date(), video=os.path.join("videos", "remi", media_guard_hash, "test.mp4"), overview=os.path.join("videos", "remi", media_guard_hash, "1", "overview.jpg"),
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
        print(" --->  SetUp of Video_edit_testCase : OK !")

    def test_video_edit(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        response = self.client.get("/video_edit/%s/" % pod.slug)
        self.assertEqual(response.status_code, 302)
        print(
            "   --->  test_video_edit of Video_edit_testCase : OK !")

    def test_video_edit_not_good_user(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        user = User.objects.get(username="remi2")
        user = authenticate(username='remi2', password='hello')
        login = self.client.login(username='remi2', password='hello')
        self.assertEqual(login, True)
        response = self.client.post('/video_edit/%s/' % pod.slug)
        self.assertEqual(response.status_code, 403)
        self.assertTrue("You cannot edit this video." in response.content)
        print(
            "   --->  test_video_edit_not_good_user of Video_edit_testCase : OK !")

    '''
    def test_edit_video_redirection_to_previous_page(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        self.user = User.objects.get(username="remi")
        self.user = authenticate(username='remi', password='hello')
        login = self.client.login(username='remi', password='hello')
        self.assertEqual(login, True)
        response = self.client.post('/video_edit/%s/' % pod.slug, {u'password': [u''], u'description': [u'<p>sdfsdf</p>\r\n'], u'title': [u'Bunny'], u'tags': [u''], u'action2': [u'Save and back to previous page'], u'date_evt': [
                                    u''], u'cursus':0, u'main_lang':'en', u'video': [u''], u'date_added': [u'20/04/2015'], u'allow_downloading': [u'on'], u'type': [u'1'], u'referer': [
            u'/channels/']})
        self.assertEqual(response.status_code, 302)
        video = Pod.objects.get(id=1)
        self.assertEqual(video.description, u'<p>sdfsdf</p>\r\n')
        self.assertRedirects(
            response, u'/channels/', status_code=302, target_status_code=200, msg_prefix='')
        print(
            "   --->  test_edit_video_redirection_to_previous_page of Video_edit_testCase : OK !")
    '''

    def test_save_edit_video(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        self.user = User.objects.get(username="remi")
        self.user = authenticate(username='remi', password='hello')
        login = self.client.login(username='remi', password='hello')
        self.assertEqual(login, True)
        response = self.client.post('/video_edit/%s/' % pod.slug, {u'password': [u'b'], u'description': [u'<p>bbla</p>\r\n'], u'title': [u'Bunny'], u'tags': [u''], u'action3': [u'Save and watch the video'], u'date_evt': [
                                    u''], u'cursus': 0, u'main_lang': 'en', u'video': [u''], u'date_added': [u'20/04/2015'], u'allow_downloading': [u'on'], u'type': [u'1']})
        self.assertEqual(response.status_code, 302)
        video = Pod.objects.get(id=1)
        self.assertEqual(video.password, "b")
        self.assertRedirects(
            response, u'/video/%s/' % pod.slug, status_code=302, target_status_code=200, msg_prefix='')
        print(
            "   --->  test_save_edit_video of Video_edit_testCase : OK !")


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
class Video_notesTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        user = User.objects.create(
            username='remi', password='12345', is_active=True)
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
                                 date_added=datetime.today().date(), owner=user, date_evt=datetime.today().date(), video=os.path.join("videos", "remi", media_guard_hash, "test.mp4"), overview=os.path.join('videos', 'remi', media_guard_hash, '1', 'overview.jpg'),
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
        print(" --->  SetUp of Video_notesTestView : OK !")

    def test_video_notes(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        self.user = User.objects.get(username="remi")
        self.user = authenticate(username='remi', password='hello')
        login = self.client.login(username='remi', password='hello')
        self.assertEqual(login, True)
        response = self.client.post(
            '/video_notes/%s/' % pod.slug, {u'note': [u'dddd']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Notes.objects.get(video=Pod.objects.get(id=1), user=self.user).note, u'dddd')
        print(
            "   --->  test_video_notes of Video_notesTestView : OK !")

    def test_video_notes_not_authenticated(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        user = User.objects.get(username="remi2")
        user = authenticate(username='remi2', password='hello')
        login = self.client.login(username='remi2', password='hello')
        self.assertEqual(login, True)
        response = self.client.post('/video_notes/%s/' % pod.slug)
        self.assertEqual(response.status_code, 403)
        print(
            "   --->  test_video_notes_not_authenticated of Video_notesTestView : OK !")


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
class Video_completion_TestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        user = User.objects.create(
            username='remi', password='12345', is_active=True, is_staff=True)
        user.set_password('hello')
        user.save()
        user2 = User.objects.create(
            username='remi2', password='12345', is_active=True, is_staff=True)
        user2.set_password('hello')
        user2.save()
        userNoStaff = User.objects.create(
            username='userNoStaff', password='12345', is_active=True, is_staff=False)
        userNoStaff.set_password('hello')
        userNoStaff.save()
        c = Channel.objects.create(title="ChannelTest1", visible=True,
                                   color="Black", style="italic", description="blabla")
        t = Theme.objects.create(
            title="Theme1", channel=c)
        other_type = Type.objects.get(id=1)
        media_guard_hash = get_media_guard("remi", 1)
        pod = Pod.objects.create(type=other_type, title=u'Bunny',
                                 date_added=datetime.today().date(), owner=user, date_evt=datetime.today().date(), video=os.path.join("videos", "remi", media_guard_hash, "test.mp4"), overview=os.path.join('videos', 'remi', media_guard_hash, '1', 'overview.jpg'),
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

        # create file to subtitle and download
        folder, created = Folder.objects.get_or_create(
            name="remi", owner=pod.owner, level=0)
        upc_document, created = Image.objects.get_or_create(
            folder=folder, name="test.vtt")
        upc_document, created = Image.objects.get_or_create(
            folder=folder, name="test2")

        print(" --->  SetUp of Video_completion_TestView : OK !")

    def test_video_completion(self):
        pod = Pod.objects.get(id=1)
        response = self.client.get("/video_completion/%s/" % pod.slug)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse('account_login') + '?next=/video_completion/%s/' % pod.slug, status_code=302, target_status_code=200, msg_prefix='')
        print(
            "   --->  test_video_completion of Video_completion_TestView : OK !")

    def test_completion_with_authenticated(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        self.user = User.objects.get(username="remi2")
        self.user = authenticate(username='remi2', password='hello')
        login = self.client.login(username='remi2', password='hello')
        self.assertEqual(login, True)
        response = self.client.get("/video_completion/%s/" % pod.slug)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            "You cannot complement this video." in response.content)

        response = self.client.get(
            "/video_completion_contributor/%s/" % pod.slug)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            "You cannot complement this video." in response.content)

        response = self.client.get("/video_completion_subtitle/%s/" % pod.slug)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            "You cannot complement this video." in response.content)

        response = self.client.get("/video_completion_download/%s/" % pod.slug)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            "You cannot complement this video." in response.content)

        # change pod owner to none staff

        self.client.logout()

        self.user = User.objects.get(username="userNoStaff")

        pod.owner = self.user
        pod.save()

        self.user = authenticate(username='userNoStaff', password='hello')
        login = self.client.login(username='userNoStaff', password='hello')
        self.assertEqual(login, True)

        # check acces to completion et contributor and NOT subtitle and
        # download
        response = self.client.get("/video_completion/%s/" % pod.slug)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(
            "/video_completion_contributor/%s/" % pod.slug)
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/video_completion_subtitle/%s/" % pod.slug)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            "Acces denied" in response.content)
        response = self.client.get("/video_completion_download/%s/" % pod.slug)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            "Acces denied" in response.content)

        print(
            "   --->  test_completion_with_authenticated of Video_completion_TestView : OK !")

    # check crud action for contributor
    def test_crud_completion_contributor(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        self.user = User.objects.get(username="remi")
        self.user = authenticate(username='remi', password='hello')
        login = self.client.login(username='remi', password='hello')
        self.assertEqual(login, True)
        # new
        response = self.client.post(
            "/video_completion_contributor/%s/" % pod.slug, {u'action': [u'new']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form_contributor'] != "")
        self.assertTrue("<form  id=\"form_contributor\"" in response.content)
        # save
        response = self.client.post(
            "/video_completion_contributor/%s/" % pod.slug, {
                u'name': [u'nicolas can'],
                u'weblink': [u'http://moodle.univ-lille1.fr/'],
                u'role': [u'director'],
                u'action': [u'save'],
                u'video': [u'1'],
                u'email_address': [u'nicolas.can@univ-lille1.fr']
            })
        self.assertEqual(response.status_code, 200)

        list_contributor = pod.contributorpods_set.all()
        self.assertEqual(len(list_contributor), 1)
        self.assertEqual(list_contributor[0].name, u'nicolas can')
        self.assertEqual(
            list_contributor[0].weblink, u'http://moodle.univ-lille1.fr/')
        self.assertEqual(list_contributor[0].role, u'director')
        self.assertEqual(
            list_contributor[0].email_address, u'nicolas.can@univ-lille1.fr')
        self.assertEqual(list_contributor[0].video.id, 1)
        self.assertEqual(len(response.context['list_contributor']), 1)
        self.assertEqual(
            response.context['list_contributor'][0].name, u'nicolas can')

        # modify
        response = self.client.post(
            "/video_completion_contributor/%s/" % pod.slug, {u'action': [u'modify'], u'id': [u'1']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form_contributor'] != "")
        self.assertTrue("<form  id=\"form_contributor\"" in response.content)

        response = self.client.post(
            "/video_completion_contributor/%s/" % pod.slug,
            {
                u'name': [u'nicolas can'],
                u'weblink': [u'http://moodle.univ-lille1.fr/'],
                u'role': [u'author'],
                u'action': [u'save'],
                u'video': [u'1'],
                u'email_address': [u'nicolas.can@univ-lille1.fr'],
                u'contributor_id': [u'1']
            })

        self.assertEqual(response.status_code, 200)
        list_contributor = pod.contributorpods_set.all()
        self.assertEqual(len(list_contributor), 1)
        self.assertEqual(list_contributor[0].role, u'author')

        # delete
        response = self.client.post(
            "/video_completion_contributor/%s/" % pod.slug, {u'action': [u'delete'],  u'id': [u'1']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        list_contributor = pod.contributorpods_set.all()
        self.assertEqual(len(response.context['list_contributor']), 0)
        self.assertEqual(len(list_contributor), 0)

        print(
            "   --->  test_crud_completion_contributor of Video_completion_TestView : OK !")

    # test crud action video_completion_subtitle
    def test_crud_completion_subtitle(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        self.user = User.objects.get(username="remi")
        self.user = authenticate(username='remi', password='hello')
        login = self.client.login(username='remi', password='hello')
        self.assertEqual(login, True)
        # new
        response = self.client.post(
            "/video_completion_subtitle/%s/" % pod.slug, {u'action': [u'new']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form_subtitle'] != "")
        self.assertTrue("<form  id=\"form_subtitle\"" in response.content)

        # save
        response = self.client.post(
            "/video_completion_subtitle/%s/" % pod.slug, {
                u'lang': [u'fr'],
                u'src': [u'1'],
                u'kind': [u'subtitles'],
                u'subtitle_id': [u'None'],
                u'action': [u'save'],
                u'video': [u'1']
            })
        self.assertEqual(response.status_code, 200)

        list_subtitle = pod.trackpods_set.all()

        self.assertEqual(len(list_subtitle), 1)

        self.assertEqual(list_subtitle[0].lang, u'fr')
        self.assertEqual(list_subtitle[0].src.id, 1)
        self.assertEqual(list_subtitle[0].kind, u'subtitles')
        self.assertEqual(list_subtitle[0].video.id, 1)

        # modify
        response = self.client.post(
            "/video_completion_subtitle/%s/" % pod.slug, {u'action': [u'modify'], u'id': [u'1']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form_subtitle'] != "")
        self.assertTrue("<form  id=\"form_subtitle\"" in response.content)

        response = self.client.post(
            "/video_completion_subtitle/%s/" % pod.slug, {
                u'lang': [u'en'],
                u'src': [u'1'],
                u'kind': [u'subtitles'],
                u'subtitle_id': [u'1'],
                u'action': [u'save'],
                u'video': [u'1']
            })

        self.assertEqual(response.status_code, 200)
        list_subtitle = pod.trackpods_set.all()
        self.assertEqual(len(list_subtitle), 1)
        self.assertEqual(list_subtitle[0].lang, u'en')

        # delete
        response = self.client.post(
            "/video_completion_subtitle/%s/" % pod.slug, {u'action': [u'delete'],  u'id': [u'1']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        list_subtitle = pod.trackpods_set.all()
        self.assertEqual(len(response.context['list_subtitle']), 0)
        self.assertEqual(len(list_subtitle), 0)

        print(
            "   --->  test_crud_completion_subtitle of Video_completion_TestView : OK !")

    # test crud action video_completion_download
    def test_crud_completion_download(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        self.user = User.objects.get(username="remi")
        self.user = authenticate(username='remi', password='hello')
        login = self.client.login(username='remi', password='hello')
        self.assertEqual(login, True)
        # new
        response = self.client.post(
            "/video_completion_download/%s/" % pod.slug, {u'action': [u'new']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form_download'] != "")
        self.assertTrue("<form  id=\"form_download\"" in response.content)

        # save
        response = self.client.post(
            "/video_completion_download/%s/" % pod.slug, {
                u'document': [u'1'],
                u'action': [u'save'],
                u'download_id': [u'None'],
                u'video': [u'1']
            })
        self.assertEqual(response.status_code, 200)

        list_download = pod.docpods_set.all()

        self.assertEqual(len(list_download), 1)
        self.assertEqual(list_download[0].document.id, 1)
        self.assertEqual(list_download[0].video.id, 1)

        # modify
        response = self.client.post(
            "/video_completion_download/%s/" % pod.slug, {u'action': [u'modify'], u'id': [u'1']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form_download'] != "")
        self.assertTrue("<form  id=\"form_download\"" in response.content)

        response = self.client.post(
            "/video_completion_download/%s/" % pod.slug, {
                u'document': [u'2'],
                u'action': [u'save'],
                u'download_id': [u'1'],
                u'video': [u'1']
            })
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.status_code, 200)
        list_download = pod.docpods_set.all()
        self.assertEqual(len(list_download), 1)
        self.assertEqual(list_download[0].document.id, 2)

        # delete
        response = self.client.post(
            "/video_completion_download/%s/" % pod.slug, {u'action': [u'delete'],  u'id': [u'1']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        list_download = pod.docpods_set.all()
        self.assertEqual(len(response.context['list_download']), 0)
        self.assertEqual(len(list_download), 0)

        print(
            "   --->  test_crud_completion_download of Video_completion_TestView : OK !")


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
class Video_chapterTestView(TestCase):
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
                                 date_added=datetime.today().date(), owner=user, date_evt=datetime.today().date(), video=os.path.join("videos", "remi", media_guard_hash, "test.mp4"), overview=os.path.join('videos', 'remi', media_guard_hash, '1', 'overview.jpg'),
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
        print(" --->  SetUp of Video_chapterTestView : OK !")

    def test_insert_chapter(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        user = User.objects.get(username="remi")
        user = authenticate(
            username='remi', password='hello')
        login = self.client.login(
            username='remi', password='hello')
        self.assertEqual(login, True)
        # access to the page
        response = self.client.get("/video_chapter/%s/" % pod.slug)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['list_chapter']), 0)
        # click 'add new enrichment' button
        response = self.client.post(
            "/video_chapter/%s/" % pod.slug, {u'action': [u'new']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form_chapter'] != "")
        # send form with 'save' button
        response = self.client.post("/video_chapter/%s/" % pod.slug, {u'title': [u'chap1'], u'chapter_id': [u'None'],
                                                                      u'video': [u'1'], u'time': [u'1'], u'action': [u'save']})
        list_chapter = pod.chapterpods_set.all()
        self.assertEqual(len(list_chapter), 1)
        self.assertEqual(list_chapter[0].title, u'chap1')
        self.assertEqual(list_chapter[0].time, 1)
        self.assertEqual(list_chapter[0].video.id, 1)
        self.assertEqual(len(response.context['list_chapter']), 1)
        self.assertEqual(response.context['list_chapter'][0].title, u'chap1')
        # click 'modify' button
        response = self.client.post(
            "/video_chapter/%s/" % pod.slug, {u'action': [u'modify'], u'id': [u'1']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form_chapter'] != "")
        self.assertTrue(
            '<input type="hidden" id="id_chapter" name="chapter_id" value="1">' in response.content)
        response = self.client.post("/video_chapter/%s/" % pod.slug, {u'title': [u'chap2'], u'chapter_id': [u'1'],
                                                                      u'video': [u'1'], u'time': [u'1'], u'action': [u'save']})
        self.assertEqual(response.status_code, 200)
        list_chapter = pod.chapterpods_set.all()
        self.assertEqual(len(list_chapter), 1)
        self.assertEqual(list_chapter[0].title, u'chap2')
        # cancel and delete enrich
        response = self.client.post(
            "/video_chapter/%s/" % pod.slug, {u'action': [u'cancel']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('"Add a new chapter"' in response.content)
        response = self.client.post(
            "/video_chapter/%s/" % pod.slug, {u'action': [u'delete'],  u'id': [u'1']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(len(response.context['list_chapter']), 0)
        list_chapter = pod.chapterpods_set.all()
        self.assertEqual(len(list_chapter), 0)

        print(
            "   --->  test_insert_chapter of Video_chapterTestView : OK !")

    def test_insert_chapter_with_overlap_errors(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        user = User.objects.get(username="remi")
        user = authenticate(
            username='remi', password='hello')
        login = self.client.login(
            username='remi', password='hello')
        self.assertEqual(login, True)
        # access to the page
        response = self.client.get("/video_chapter/%s/" % pod.slug)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['list_chapter']), 0)
        # click 'add new enrichment' button
        response = self.client.post(
            "/video_chapter/%s/" % pod.slug, {u'action': [u'new']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form_chapter'] != "")
        # send form with 'save' button
        response = self.client.post("/video_chapter/%s/" % pod.slug, {u'title': [u'chap1'], u'chapter_id': [u'None'],
                                                                      u'video': [u'1'], u'time': [u'1'], u'action': [u'save']})
        # click 'add new enrichment' button
        response = self.client.post(
            "/video_chapter/%s/" % pod.slug, {u'action': [u'new']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        # test to add new enrich with overlap
        response = self.client.post("/video_chapter/%s/" % pod.slug, {u'title': [u'chap1'], u'chapter_id': [u'None'],
                                                                      u'video': [u'1'], u'time': [u'1'], u'action': [u'save']})

        list_chapter = pod.chapterpods_set.all()
        self.assertEqual(len(list_chapter), 1)
        print(
            "   --->  test_insert_chapter_with_overlap_errors of Video_chapterTestView : OK !")

    def test_insert_chapter_with_title_errors(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        user = User.objects.get(username="remi")
        user = authenticate(
            username='remi', password='hello')
        login = self.client.login(
            username='remi', password='hello')
        self.assertEqual(login, True)
        # access to the page
        response = self.client.get("/video_chapter/%s/" % pod.slug)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['list_chapter']), 0)
        # click 'add new enrichment' button
        response = self.client.post(
            "/video_chapter/%s/" % pod.slug, {u'action': [u'new']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form_chapter'] != "")
        # send form with 'save' button
        response = self.client.post("/video_chapter/%s/" % pod.slug, {u'title': [u't'], u'chapter_id': [u'None'],
                                                                      u'time': [u'0'], u'video': [u'1'], u'action': [u'save']})

        list_chapter = pod.chapterpods_set.all()
        self.assertEqual(len(list_chapter), 0)
        print(
            "   --->  test_insert_chapter_with_title_errors of Video_chapterTestView : OK !")

    def test_acces_to_chapter_with_other_authenticating(self):
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
        response = self.client.get("/video_chapter/%s/" % pod.slug)
        self.assertEqual(response.status_code, 403)
        self.assertTrue("You cannot chapter this video." in response.content)
        print(
            "   --->  test_acces_to_chapter_with_other_authenticating of Video_chapterTestView : OK !")


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
class Video_search_videos(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        user = User.objects.create(
            username='remi', password='12345', is_active=True, is_staff=True)
        user.set_password('hello')
        user.save()

        other_type = Type.objects.get(id=1)
        media_guard_hash = get_media_guard("remi", 1)
        pod = Pod.objects.create(type=other_type, title=u'Bunny',
                                 date_added=datetime.today().date(), owner=user, date_evt=datetime.today().date(), video=os.path.join("videos", "remi", media_guard_hash, "test.mp4"), overview=os.path.join('videos', 'remi', media_guard_hash, '1', 'overview.jpg'),
                                 allow_downloading=True, duration=33, encoding_in_progress=False, view_count=0, description="bugs", is_draft=False,
                                 to_encode=False)
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile=os.path.join("videos", "remi", media_guard_hash, "1", "video_1_240.mp4"), encodingFormat="video/mp4")

        ENCODE_WEBM = getattr(settings, 'ENCODE_WEBM', True)
        if ENCODE_WEBM:
            EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
                id=1), encodingFile=os.path.join("videos", "remi", media_guard_hash, "1", "video_1_240.webm"), encodingFormat="video/webm")
        pod.save()

        pod2 = Pod.objects.create(type=other_type, title=u'NoIndex',
                                  date_added=datetime.today().date(), owner=user, date_evt=datetime.today().date(), video=os.path.join("videos", "remi", media_guard_hash, "test.mp4"), overview=os.path.join('videos', 'remi', media_guard_hash, '1', 'overview.jpg'),
                                  allow_downloading=True, duration=33, encoding_in_progress=False, view_count=0, description="no index", is_draft=True,
                                  to_encode=False)
        EncodingPods.objects.create(video=pod2, encodingType=EncodingType.objects.get(
            id=1), encodingFile=os.path.join("videos", "remi", media_guard_hash, "1", "video_1_240.mp4"), encodingFormat="video/mp4")
        if ENCODE_WEBM:
            EncodingPods.objects.create(video=pod2, encodingType=EncodingType.objects.get(
                id=1), encodingFile=os.path.join("videos", "remi", media_guard_hash, "1", "video_1_240.webm"), encodingFormat="video/webm")
        pod2.save()

        print(" --->  SetUp of Video_enrichTestView : OK !")

    def test_search_video(self):
        self.client = Client()
        response = self.client.get("/search/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['result']["hits"]["total"], 1)
        self.assertEqual(response.context['result']["hits"][
                         "hits"][0]["_source"]["title"], "Bunny")

        response = self.client.get("/search/?q=bunn")  # title
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['result']["hits"]["total"], 1)
        self.assertEqual(response.context['result']["hits"][
                         "hits"][0]["_source"]["title"], "Bunny")

        response = self.client.get("/search/?q=remi")  # owner
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['result']["hits"]["total"], 1)
        self.assertEqual(response.context['result']["hits"][
                         "hits"][0]["_source"]["title"], "Bunny")

        response = self.client.get("/search/?q=bugs")  # description
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['result']["hits"]["total"], 1)
        self.assertEqual(response.context['result']["hits"][
                         "hits"][0]["_source"]["title"], "Bunny")

        # test draft video is no index
        response = self.client.get("/search/?q=NoIndex")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['result']["hits"]["total"], 0)

        response = self.client.get("/search/?q=toto")  # test random query
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['result']["hits"]["total"], 0)

        response = self.client.get("/search/?q=Other")  # test type filtre
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['result']["hits"]["total"], 1)
        self.assertEqual(response.context['result']["hits"][
                         "hits"][0]["_source"]["title"], "Bunny")

        response = self.client.get(
            "/search/?q=&start_date=17%2F07%2F2015")  # test date filtre
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['result']["hits"]["total"], 1)
        self.assertEqual(response.context['result']["hits"][
                         "hits"][0]["_source"]["title"], "Bunny")

        print(
            "   --->  test_search_video of Video_search_videos : OK !")


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
class Video_enrichTestView(TestCase):
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
                                 date_added=datetime.today().date(), owner=user, date_evt=datetime.today().date(), video=os.path.join("videos", "remi", media_guard_hash, "test.mp4"), overview=os.path.join('videos', 'remi', media_guard_hash, '1', 'overview.jpg'),
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
        print(" --->  SetUp of Video_enrichTestView : OK !")

    def test_insert_enrich(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        user = User.objects.get(username="remi")
        user = authenticate(
            username='remi', password='hello')
        login = self.client.login(
            username='remi', password='hello')
        self.assertEqual(login, True)
        # access to the page
        response = self.client.get("/video_enrich/%s/" % pod.slug)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['list_enrichment']), 0)
        # click 'add new enrichment' button
        response = self.client.post(
            "/video_enrich/%s/" % pod.slug, {u'action': [u'new']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form_enrich'] != "")
        # send form with 'save' button
        response = self.client.post("/video_enrich/%s/" % pod.slug, {u'end': [u'1'], u'title': [u'test'], u'image': [u''],
                                                                     u'weblink': [u''], u'richtext': [u'sdfg'], u'enrich_id': [u'None'],
                                                                     u'start': [u'0'], u'video': [u'1'], u'action': [u'save'],
                                                                     u'document': [u''], u'type': [u'richtext'], u'embed': [u'']})
        list_enrichment = pod.enrichpods_set.all()
        self.assertEqual(len(list_enrichment), 1)
        self.assertEqual(list_enrichment[0].title, u'test')
        self.assertEqual(list_enrichment[0].end, 1)
        self.assertEqual(list_enrichment[0].start, 0)
        self.assertEqual(list_enrichment[0].video.id, 1)
        self.assertEqual(list_enrichment[0].type, u'richtext')
        self.assertEqual(list_enrichment[0].richtext, u'sdfg')
        self.assertEqual(len(response.context['list_enrichment']), 1)
        self.assertEqual(response.context['list_enrichment'][0].title, u'test')
        # click 'modify' button
        response = self.client.post(
            "/video_enrich/%s/" % pod.slug, {u'action': [u'modify'], u'id': [u'1']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form_enrich'] != "")
        self.assertTrue(
            '<input type="hidden" id="id_enrich" name="enrich_id" value="1">' in response.content)
        response = self.client.post("/video_enrich/%s/" % pod.slug, {u'end': [u'1'], u'title': [u'test2'], u'image': [u''],
                                                                     u'weblink': [u''], u'richtext': [u'sdfg'], u'enrich_id': [u'1'],
                                                                     u'start': [u'0'], u'video': [u'1'], u'action': [u'save'],
                                                                     u'document': [u''], u'type': [u'richtext'], u'embed': [u'']})
        list_enrichment = pod.enrichpods_set.all()
        self.assertEqual(len(list_enrichment), 1)
        self.assertEqual(list_enrichment[0].title, u'test2')
        # cancel and delete enrich
        response = self.client.post(
            "/video_enrich/%s/" % pod.slug, {u'action': [u'cancel']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('"Add a new enrichment"' in response.content)
        response = self.client.post(
            "/video_enrich/%s/" % pod.slug, {u'action': [u'delete'],  u'id': [u'1']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(len(response.context['list_enrichment']), 0)
        list_enrichment = pod.enrichpods_set.all()
        self.assertEqual(len(list_enrichment), 0)
        print(
            "   --->  test_insert_enrich of Video_enrichTestView : OK !")

    def test_insert_enrich_with_field_and_overlap_errors(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        user = User.objects.get(username="remi")
        user = authenticate(
            username='remi', password='hello')
        login = self.client.login(
            username='remi', password='hello')
        self.assertEqual(login, True)
        # access to the page
        response = self.client.get("/video_enrich/%s/" % pod.slug)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['list_enrichment']), 0)
        # click 'add new enrichment' button
        response = self.client.post(
            "/video_enrich/%s/" % pod.slug, {u'action': [u'new']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form_enrich'] != "")
        # send form with 'save' button
        response = self.client.post("/video_enrich/%s/" % pod.slug, {u'end': [u'1'], u'title': [u'test'], u'image': [u''],
                                                                     u'weblink': [u''], u'richtext': [u'sdfg'], u'enrich_id': [u'None'],
                                                                     u'start': [u'0'], u'video': [u'1'], u'action': [u'save'],
                                                                     u'document': [u''], u'type': [u'richtext'], u'embed': [u'']})
        # click 'add new enrichment' button
        response = self.client.post(
            "/video_enrich/%s/" % pod.slug, {u'action': [u'new']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        # test to add new enrich with overlap
        response = self.client.post("/video_enrich/%s/" % pod.slug, {u'end': [u'1'], u'title': [u't'], u'image': [u''],
                                                                     u'weblink': [u''], u'richtext': [u''], u'enrich_id': [u'None'],
                                                                     u'start': [u'0'], u'video': [u'1'], u'action': [u'save'],
                                                                     u'document': [u''], u'type': [u'richtext'], u'embed': [u'']})

        list_enrichment = pod.enrichpods_set.all()
        self.assertEqual(len(list_enrichment), 1)
        print(
            "   --->  test_insert_enrich_with_field_and_overlap_errors of Video_enrichTestView : OK !")

    def test_insert_enrich_with_title_errors(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        user = User.objects.get(username="remi")
        user = authenticate(
            username='remi', password='hello')
        login = self.client.login(
            username='remi', password='hello')
        self.assertEqual(login, True)
        # access to the page
        response = self.client.get("/video_enrich/%s/" % pod.slug)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['list_enrichment']), 0)
        # click 'add new enrichment' button
        response = self.client.post(
            "/video_enrich/%s/" % pod.slug, {u'action': [u'new']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form_enrich'] != "")
        # send form with 'save' button
        response = self.client.post("/video_enrich/%s/" % pod.slug, {u'end': [u'1'], u'title': [u't'], u'image': [u''],
                                                                     u'weblink': [u''], u'richtext': [u''], u'enrich_id': [u'None'],
                                                                     u'start': [u'0'], u'video': [u'1'], u'action': [u'save'],
                                                                     u'document': [u''], u'type': [u'richtext'], u'embed': [u'']})

        list_enrichment = pod.enrichpods_set.all()
        self.assertEqual(len(list_enrichment), 0)
        print(
            "   --->  test_insert_enrich_with_title_errors of Video_enrichTestView : OK !")

    def test_access_to_enrich_with_other_authenticating(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        user = User.objects.get(username="remi2")
        user.is_staff = True
        user.save()
        user = authenticate(
            username='remi2', password='hello')
        login = self.client.login(
            username='remi2', password='hello')
        self.assertEqual(login, True)
        response = self.client.get("/video_enrich/%s/" % pod.slug)
        self.assertEqual(response.status_code, 403)
        self.assertTrue("You cannot enrich this video." in response.content)
        print(
            "   --->  test_access_to_enrich_with_other_authenticating of Video_enrichTestView : OK !")


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
class Video_mediacourses(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        # user is staff but user2 not
        user = User.objects.create(
            username='remi', password='12345', is_active=True, is_staff=True)
        user.set_password('hello')
        user.save()

        user2 = User.objects.create(
            username='remi2', password='12345', is_active=True)
        user2.set_password('hello')
        user2.save()
        print(" --->  SetUp of Video_mediacourses : OK !")

    def test_access_user_staff_mediacourses_add(self):
        self.client = Client()
        user = User.objects.get(username="remi")
        user = authenticate(
            username='remi', password='hello')
        login = self.client.login(
            username='remi', password='hello')
        self.assertEqual(login, True)
        response = self.client.get("/mediacourses_add/?mediapath=abcdefg.zip")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)
        self.client.logout()
        self.assertTrue(self.client.session.get('_auth_user_id') == None)
        print(
            "   --->  test_access_user_staff_mediacourses_add of Video_mediacourses : OK !")

    def test_access_user_mediacourses_add(self):
        self.client = Client()
        user = User.objects.get(username="remi2")
        user = authenticate(
            username='remi2', password='hello')
        login = self.client.login(
            username='remi2', password='hello')
        self.assertEqual(login, True)
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)
        response = self.client.get("/mediacourses_add/?mediapath=abcdefg.zip")
        version = django.get_version()
        if version < 1.7:
            self.assertTrue("this_is_the_login_form" in response.content)
        else:
            self.assertRedirects(
                response, '/admin/login/?next=/mediacourses_add/%3Fmediapath%3Dabcdefg.zip', status_code=302, target_status_code=200, msg_prefix='')
        print(
            "   --->  test_access_user_mediacourses_add of Video_mediacourses : OK !")

    def test_access_user_mediacourses_add_without_mediapath(self):
        self.client = Client()
        user = User.objects.get(username="remi")
        user = authenticate(
            username='remi', password='hello')
        login = self.client.login(
            username='remi', password='hello')
        self.assertEqual(login, True)
        response = self.client.get("/mediacourses_add/")
        self.assertEqual(response.status_code, 403)
        print(
            "   --->  test_access_user_mediacourses_add_without_mediapath of Video_mediacourses : OK !")
    """
    def test_post_data_mediacourses_add(self):
        self.client = Client()
        user = User.objects.get(username="remi")
        user = authenticate(
            username='remi', password='hello')
        login = self.client.login(
            username='remi', password='hello')
        self.assertEqual(login, True)
        response = self.client.post("/mediacourses_add/?mediapath=abcdefg.zip", {u'title': [u'my first course']})
        self.assertEqual(response.status_code, 200)
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
class Video_mediacourses_notify(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        # add building
        building = Building.objects.create(name='my building')
        # add recorder
        recorder = Recorder.objects.create(
            name='my recorder', adress_ip='192.168.1.59', building=building)
        print(" --->  SetUp of Video_mediacourses_notify : OK !")

    def test_mediacourses_notify_args(self):
        response = self.client.get("/mediacourses_notify/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content, "nok : recordingPlace or mediapath or key are missing")
        response = self.client.get("/mediacourses_notify/?toto=toto")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content, "nok : recordingPlace or mediapath or key are missing")
        #?recordingPlace=192_168_1_59&mediapath=4b2652fb-d890-46d4-bb15-9a47c6666239.zip&key=a81c115af212b6ae406ce1509bce8ef6
        response = self.client.get(
            "/mediacourses_notify/?recordingPlace=192_168_1_59")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content, "nok : recordingPlace or mediapath or key are missing")
        response = self.client.get(
            "/mediacourses_notify/?recordingPlace=192_168_1_59&mediapath=4b2652fb-d890-46d4-bb15-9a47c6666239.zip")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content, "nok : recordingPlace or mediapath or key are missing")
        response = self.client.get(
            "/mediacourses_notify/?recordingPlace=192_168_1_59&mediapath=4b2652fb-d890-46d4-bb15-9a47c6666239.zip&key=a81c115af212b6ae406ce1509bce8ef6")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "nok : key is not valid")
        print(
            "   --->  test_mediacourses_notify_args of Video_mediacourses_notify : OK !")

    def test_mediacourses_notify_without_good_recorder(self):
        import hashlib
        m = hashlib.md5()
        m.update("192_168_1_10" + settings.RECORDER_SALT)
        response = self.client.get(
            "/mediacourses_notify/?recordingPlace=192_168_1_10&mediapath=4b2652fb-d890-46d4-bb15-9a47c6666239.zip&key=%s" % m.hexdigest())
        self.assertEqual(response.status_code, 404)
        print(
            "   --->  test_mediacourses_notify_without_good_recorder of Video_mediacourses_notify : OK !")

    def test_mediacourses_notify_good(self):
        import hashlib
        m = hashlib.md5()
        m.update("192_168_1_59" + settings.RECORDER_SALT)
        response = self.client.get(
            "/mediacourses_notify/?recordingPlace=192_168_1_59&mediapath=4b2652fb-d890-46d4-bb15-9a47c6666239.zip&key=%s" % m.hexdigest())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "ok")
        print(
            "   --->  test_mediacourses_notify_good of Video_mediacourses_notify : OK !")
