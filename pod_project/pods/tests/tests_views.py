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
from django.test import TestCase
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
# Create your tests here.
"""
    test view
"""


class ChannelsTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        remi = User.objects.create(username="remi")
        i = 1
        while i <= 15:
            Channel.objects.create(title="ChannelTest" + str(i), visible=True,
                                   color="Black", owner=remi, style="italic", description="blabla")
            i += 1

        t = Theme.objects.create(
            title="Theme1", channel=Channel.objects.get(id=1))
        other_type = Type.objects.get(id=1)
        pod = Pod.objects.create(type=other_type, title="Video2", encoding_status="b", encoding_in_progress=False,
                                 date_added=datetime.today(), owner=remi, date_evt=datetime.today(), video="videos/remi/test.mp4",
                                 allow_downloading=True, view_count=2, description="fl", overview="videos/remi/1/overview.jpg", is_draft=False,
                                 duration=3, infoVideo="videotest", to_encode=False)
        EncodingPods.objects.create(
            video=pod, encodingType=EncodingType.objects.get(id=1))
        pod.theme.add(t)
        pod.channel.add(Channel.objects.get(id=1))
        pod.save()
        print (" --->  SetUp of ChannelsTestView : OK !")

    def test_channels_with_paginator(self):
        channels = list(Channel.objects.all())
        # test when a index of page is a caractere
        response = self.client.get("/channels/?page=a")
        self.assertEqual(response.status_code, 200)
        liste = list(response.context[u"channels"].__dict__["object_list"])
        paginator = Paginator(Channel.objects.all(), 12)
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
        print (
            "   --->  test_channels_with_paginator of ChannelsTestView : OK !")

    def test_channels_with_ajax_request(self):
        response = self.client.get(
            "/channels/", perpage=24,  HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request[u'REQUEST_METHOD'], 'GET')
        self.assertEqual(response.request['perpage'], 24)
        print (
            "   --->  test_channels_with_ajax_request of ChannelsTestView : OK !")


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
            Channel.objects.create(title="ChannelTest" + str(i), visible=True,
                                   color="Black", owner=remi, style="italic", description="blabla")
            i += 1
        print (" --->  SetUp of Owner_channels_listTestView : OK !")

    def test_owner_channels_list(self):
        self.client = Client()
        self.user = User.objects.get(username="testuser")
        self.user = authenticate(username='testuser', password='hello')
        login = self.client.login(username='testuser', password='hello')
        channels = list(Channel.objects.filter(owner=self.user))
        self.assertEqual(login, True)
        response = self.client.get("/owner_channels_list/")
        self.assertEqual(response.status_code, 200)
        liste = list(response.context["CHANNELS"])
        self.assertEqual(liste, channels)
        self.assertEqual(response.context["video_count"], 0)
        print (
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
        print (
            "   --->  test_owner_channels_with_ajax_request of Owner_channels_listTestView : OK !")


class ChannelTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        remi = User.objects.create(username='testuser')
        c = Channel.objects.create(title="ChannelTest1", visible=True,
                                   color="Black", owner=remi, style="italic", description="blabla")
        t = Theme.objects.create(
            title="Theme1", channel=c)
        other_type = Type.objects.get(id=1)
        pod = Pod.objects.create(type=other_type, title="Video2", encoding_status="b", encoding_in_progress=True,
                                 date_added=datetime.today(), owner=remi, date_evt=datetime.today(), video="videos/remi/test.mp4",
                                 allow_downloading=True, view_count=2, description="fl", overview="videos/remi/1/overview.jpg", is_draft=False,
                                 duration=3, infoVideo="videotest", to_encode=False)
        pod.save()
        pod.theme.add(t)
        pod.channel.add(Channel.objects.get(id=1))
        pod.save()
        pod.theme.add(t)
        print (" --->  SetUp of ChannelTestView : OK !")

    def test_channel_without_theme_in_argument(self):
        c = Channel.objects.get(id=1)
        self.client = Client()
        response = self.client.get("/%s/" % c.slug)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context[u"channel"], Channel.objects.get(id=1))
        self.assertEqual(
            response.context[u"theme"], None)
        print (
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
        print (
            "   --->  test_channel_with_theme_in_argument of ChannelTestView : OK !")

    def test_channel_with_ajax_request(self):
        c = Channel.objects.get(id=1)
        response = self.client.get(
            "/%s/" % c.slug, perpage=48,  HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request[u'REQUEST_METHOD'], 'GET')
        self.assertEqual(response.request['perpage'], 48)
        print (
            "   --->  test_channel_with_ajax_request of ChannelTestView : OK !")


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
        Channel.objects.create(title="ChannelTest1", visible=True,
                               color="Black", owner=self.user, style="italic", description="blabla")
        print (" --->  SetUp of Channel_edit_TestView : OK !")

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
        print (
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
        self.assertTrue("The changes have been saved" in response.content)
        channel = Channel.objects.get(id=1)
        self.assertEqual(channel.description, u'<p>blabladsvvvv</p>\r\n')
        print (
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
        self.assertTrue("You cannot edit this channel" in response.content)
        self.assertFalse(channel.description == u'<p>ba</p>\r\n')
        print (
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
        print (
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
        print (
            "   --->  test_redirection_to_the_channel of Channel_edit_TestView : OK !")


class TypesTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        remi = User.objects.create_user(username="remi")
        other_type = Type.objects.get(id=1)
        pod = Pod.objects.create(type=other_type, title="Video2", encoding_status="b", encoding_in_progress=True,
                                 date_added=datetime.today(), owner=remi, date_evt=datetime.today(), video="videos/remi/test.mp4",
                                 allow_downloading=True, view_count=2, description="fl", overview="videos/remi/1/overview.jpg", is_draft=False,
                                 duration=3, infoVideo="videotest", to_encode=False)
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile="videos/remi/1/video_1_240.mp4", encodingFormat="video/mp4")
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile="videos/remi/1/video_1_240.webm", encodingFormat="video/webm")
        pod.save()
        Type.objects.create(title="Type2")
        print (" --->  SetUp of TypesTestView : OK !")

    def test_types(self):
        types = list(Type.objects.all())
        response = self.client.get("/types/")
        liste = list(response.context[u"types"].__dict__["object_list"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(liste, types)
        self.assertEqual(response.context["video_count"], 1)
        print ("   --->  test_types of TypesTestView : OK !")

    def test_types_with_ajax_request(self):
        response = self.client.get(
            "/types/", perpage=48,  HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request[u'REQUEST_METHOD'], 'GET')
        self.assertEqual(response.request['perpage'], 48)
        print ("   --->  test_types_with_ajax_request of TypesTestView : OK !")


class OwnersTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        remi = User.objects.create_user(username="Remi", last_name="Lefevbre")
        other_type = Type.objects.get(id=1)
        pod = Pod.objects.create(type=other_type, title="Video2", encoding_status="b", encoding_in_progress=True,
                                 date_added=datetime.today(), owner=remi, date_evt=datetime.today(), video="videos/remi/test.mp4",
                                 allow_downloading=True, view_count=2, description="fl", overview="videos/remi/1/overview.jpg", is_draft=False,
                                 duration=3, infoVideo="videotest", to_encode=False)
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile="videos/remi/1/video_1_240.mp4", encodingFormat="video/mp4")
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile="videos/remi/1/video_1_240.webm", encodingFormat="video/webm")
        pod.save()
        print (" --->  SetUp of OwnersTestView : OK !")

    def test_owners(self):
        owners = list(User.objects.filter(
            pod__in=Pod.objects.filter(is_draft=False, encodingpods__gt=0)))
        response = self.client.get("/owners/")
        liste = list(response.context[u"owners"].__dict__["object_list"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(liste, owners)
        self.assertEqual(response.context["video_count"], 1)
        print ("   --->  test_owners of OwnersTestView : OK !")

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
        print (
            "   --->  test_owners_with_filter_in_argument of OwnersTestView : OK !")

    def test_owners_with_ajax_request(self):

        response = self.client.get(
            "/owners/", perpage=24,  HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request[u'REQUEST_METHOD'], 'GET')
        self.assertEqual(response.request['perpage'], 24)
        print (
            "   --->  test_owners_with_ajax_request of OwnersTestView : OK !")


class DisciplinesTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        remi = User.objects.create_user(username="remi")
        Discipline.objects.create(title="Discipline1")
        other_type = Type.objects.get(id=1)
        d1 = Discipline.objects.create(title="Discipline2")
        pod = Pod.objects.create(type=other_type, title="Video2", encoding_status="b", encoding_in_progress=True,
                                 date_added=datetime.today(), owner=remi, date_evt=datetime.today(), video="videos/remi/test.mp4",
                                 allow_downloading=True, view_count=2, description="fl", overview="videos/remi/1/overview.jpg", is_draft=False,
                                 duration=3, infoVideo="videotest", to_encode=False)
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile="videos/remi/1/video_1_240.mp4", encodingFormat="video/mp4")
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile="videos/remi/1/video_1_240.webm", encodingFormat="video/webm")
        pod.discipline.add(d1)
        pod.save()
        print (" --->  SetUp of DisciplinesTestView : OK !")

    def test_disciplines(self):
        disciplines = list(Discipline.objects.all())
        response = self.client.get("/disciplines/")
        liste = list(response.context[u"disciplines"].__dict__["object_list"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(liste, disciplines)
        self.assertEqual(response.context["video_count"], 1)
        print ("   --->  test_disciplines of DisciplinesTestView : OK !")

    def test_disciplines_with_ajax_request(self):
        response = self.client.get(
            "/disciplines/", perpage=24,  HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request[u'REQUEST_METHOD'], 'GET')
        self.assertEqual(response.request['perpage'], 24)
        print (
            "   --->  test_disciplines_with_ajax_request of DisciplinesTestView : OK !")


class Owner_Videos_listTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        self.user = User.objects.create(
            username='testuser', password='12345', is_active=True, is_staff=True, is_superuser=True)
        self.user.set_password('hello')
        self.user.save()
        other_type = Type.objects.get(id=1)
        i = 1
        while i < 3:
            pod = Pod.objects.create(type=other_type, title="Video" + str(i), encoding_status="b", encoding_in_progress=True,
                                     date_added=datetime.today(), owner=self.user, date_evt=datetime.today(), video="videos/remi/test.mp4",
                                     allow_downloading=True, view_count=2, description="fl", overview="videos/remi/1/overview.jpg", is_draft=False,
                                     duration=3, infoVideo="videotest", to_encode=False)

            pod.save()
            i += 1
        print (" --->  SetUp of Owner_Videos_listTestView : OK !")

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
        print (
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
        print (
            "   --->  test_owners_video_list_with_ajax_request of Owner_Videos_listTestView : OK !")


class Tags_TestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        remi = User.objects.create_user(username="remi")
        other_type = Type.objects.get(id=1)
        pod = Pod.objects.create(type=other_type, title="Video2", encoding_status="b", encoding_in_progress=True,
                                 date_added=datetime.today(), owner=remi, date_evt=datetime.today(), video="videos/remi/test.mp4",
                                 allow_downloading=True, view_count=2, description="fl", overview="videos/remi/1/overview.jpg", is_draft=False,
                                 duration=3, infoVideo="videotest", to_encode=False)
        pod.tags.add(u"testtagVideo2")
        pod.tags.add(u"téstàvecâccent")
        pod.save()
        print (" --->  SetUp of Tags_TestView : OK !")

    def test_tags(self):
        pod = Pod.objects.get(id=1)
        response = self.client.get("/tags/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(pod.tags.get(id=1).name, u"testtagvideo2")
        self.assertEqual(pod.tags.get(id=2).name, u'testavecaccent')
        pod.tags.add("TESTTAGVIDEO2")
        self.assertEqual(pod.tags.all().count(), 2)
        print ("   --->  test_tags of Tags_TestView : OK !")


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
        pod = Pod.objects.create(type=other_type, title="Video2", encoding_status="b", encoding_in_progress=True,
                                 date_added=datetime.today(), owner=user2, date_evt=datetime.today(), video="videos/remi/test.mp4",
                                 allow_downloading=True, view_count=2, description="fl", overview="videos/remi/1/overview.jpg", is_draft=False,
                                 duration=3, infoVideo="videotest", to_encode=False)
        pod.save()
        print (" --->  SetUp of Video_add_favoriteTestView : OK !")

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

        print (
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
        self.assertTrue("You cannot view this page" in response.content)

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
        print (
            "   --->  test_delete_favorite of Video_add_favoriteTestView : OK !")


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
        i = 1
        while i < 5:
            pod = Pod.objects.create(type=other_type, title="Video" + str(i), encoding_status="b", encoding_in_progress=True,
                                     date_added=datetime.today(), owner=user2, date_evt=datetime.today(), video="videos/remi/test.mp4",
                                     allow_downloading=True, view_count=2, description="fl", overview="videos/remi/1/overview.jpg", is_draft=False,
                                     duration=3, infoVideo="videotest", to_encode=False)
            pod.save()
            i += 1
        print (" --->  SetUp of Favorites_videos_listTestView : OK !")

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
        print (
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
        print (
            "   --->  test_favorites_video_list_with_ajax_request of Favorites_videos_listTestView : OK !")


class VideosTestView(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        d1 = Discipline.objects.create(title="Discipline1")
        user = User.objects.create(
            username='remi', last_name="lefevbre",  password='12345', is_active=True, is_staff=False)
        user.set_password('hello')
        user.save()
        type1 = Type.objects.create(title="type1")
        i = 1
        while i < 5:
            pod = Pod.objects.create(type=type1, title="Video" + str(i), encoding_status="b", encoding_in_progress=True,
                                     date_added=datetime.today(), owner=user, date_evt=datetime.today(), video="videos/remi/test.mp4",
                                     allow_downloading=True, view_count=0, description="fl", overview="videos/remi/1/overview.jpg", is_draft=False,
                                     duration=3, infoVideo="videotest", to_encode=False)
            EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
                id=1), encodingFile="/media/videos/remi/1/video_1_240.mp4")
            pod.tags.add("videotests")
            if i % 2:
                pod.discipline.add(d1)
            pod.save()
            i += 1
        print (" --->  SetUp of videosTestView : OK !")

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
        print (
            "   --->  test_videos_discipline_filtre of videosTestView : OK !")

    def test_videos_owners_filtre(self):
        videos = Pod.objects.filter(owner=User.objects.get(id=1))
        owner = User.objects.get(id=1)
        response = self.client.get("/videos/?owner=remi")
        self.assertEqual(response.status_code, 200)
        liste_videos = list(response.context["videos"].__dict__["object_list"])
        self.assertEqual(liste_videos, list(videos))
        print (
            "   --->  test_videos_owners_filtre of videosTestView : OK !")

    def test_videos_with_ajax_request(self):
        response = self.client.get(
            "/videos/", perpage=24,  HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request[u'REQUEST_METHOD'], 'GET')
        self.assertEqual(response.request['perpage'], 24)
        print (
            "   --->  test_videos_with_ajax_request of videosTestView : OK !")


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
                                   color="Black", owner=user, style="italic", description="blabla")
        t = Theme.objects.create(
            title="Theme1", channel=c)
        type1 = Type.objects.create(title="type1")
        pod = Pod.objects.create(type=type1, title=u'Bunny',
                                 date_added=datetime.today(), owner=user, date_evt=datetime.today(), video="videos/remi/test.mp4", overview=u'videos/remi/1/overview.jpg',
                                 allow_downloading=False, duration=33, encoding_in_progress=False, view_count=0, description="fl", is_draft=True,
                                 to_encode=False)

        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile="videos/remi/1/video_1_240.mp4", encodingFormat="video/mp4")
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile="videos/remi/1/video_1_240.webm", encodingFormat="video/webm")

        pod.channel.add(c)
        pod.theme.add(t)
        pod.save()
        print (" --->  SetUp of videoTestView : OK !")

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
        print (
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
        self.assertTrue("You cannot watch this video" in response.content)
        print (
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
        print (
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

        print (
            "   --->  test_video_password of VideoTestView : OK !")


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
                                   color="Black", owner=user, style="italic", description="blabla")
        t = Theme.objects.create(
            title="Theme1", channel=c)
        other_type = Type.objects.get(id=1)
        pod = Pod.objects.create(type=other_type, title=u'Bunny',
                                 date_added=datetime.today(), owner=user, date_evt=datetime.today(), video="videos/remi/test.mp4", overview=u'videos/remi/1/overview.jpg',
                                 allow_downloading=True, duration=33, encoding_in_progress=False, view_count=0, description="fl", is_draft=True,
                                 to_encode=False)
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile="videos/remi/1/video_1_240.mp4", encodingFormat="video/mp4")
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile="videos/remi/1/video_1_240.webm", encodingFormat="video/webm")
        pod.channel.add(c)
        pod.theme.add(t)
        pod.save()
        print (" --->  SetUp of Video_edit_testCase : OK !")

    def test_video_edit(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        response = self.client.get("/video_edit/%s/" % pod.slug)
        self.assertEqual(response.status_code, 302)
        print (
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
        self.assertTrue("You cannot edit this video" in response.content)
        print (
            "   --->  test_video_edit_not_good_user of Video_edit_testCase : OK !")

    def test_edit_video_redirection_to_previous_page(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        self.user = User.objects.get(username="remi")
        self.user = authenticate(username='remi', password='hello')
        login = self.client.login(username='remi', password='hello')
        self.assertEqual(login, True)
        response = self.client.post('/video_edit/%s/' % pod.slug, {u'password': [u''], u'description': [u'<p>sdfsdf</p>\r\n'], u'title': [u'Bunny'], u'tags': [u''], u'action2': [u'Save and back to the previous page'], u'date_evt': [
                                    u''], u'video': [u''], u'date_added': [u'20/04/2015'], u'allow_downloading': [u'on'], u'type': [u'1'], u'referer': [
            u'/channels/']})
        self.assertEqual(response.status_code, 302)
        video = Pod.objects.get(id=1)
        self.assertEqual(video.description, u'<p>sdfsdf</p>\r\n')
        self.assertRedirects(
            response, u'/channels/', status_code=302, target_status_code=200, msg_prefix='')
        print (
            "   --->  test_edit_video_redirection_to_previous_page of Video_edit_testCase : OK !")

    def test_save_edit_video(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        self.user = User.objects.get(username="remi")
        self.user = authenticate(username='remi', password='hello')
        login = self.client.login(username='remi', password='hello')
        self.assertEqual(login, True)
        response = self.client.post('/video_edit/%s/' % pod.slug, {u'password': [u'b'], u'description': [u'<p>bbla</p>\r\n'], u'title': [u'Bunny'], u'tags': [u''], u'action3': [u'Save and watch the video'], u'date_evt': [
                                    u''], u'video': [u''], u'date_added': [u'20/04/2015'], u'allow_downloading': [u'on'], u'type': [u'1']})
        self.assertEqual(response.status_code, 302)
        video = Pod.objects.get(id=1)
        self.assertEqual(video.password, "b")
        self.assertRedirects(
            response, u'/video/%s/' % pod.slug, status_code=302, target_status_code=200, msg_prefix='')
        print (
            "   --->  test_save_edit_video of Video_edit_testCase : OK !")


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
                                   color="Black", owner=user, style="italic", description="blabla")
        t = Theme.objects.create(
            title="Theme1", channel=c)
        other_type = Type.objects.get(id=1)
        pod = Pod.objects.create(type=other_type, title=u'Bunny',
                                 date_added=datetime.today(), owner=user, date_evt=datetime.today(), video="videos/remi/test.mp4", overview=u'videos/remi/1/overview.jpg',
                                 allow_downloading=True, duration=33, encoding_in_progress=False, view_count=0, description="fl", is_draft=True,
                                 to_encode=False)
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile="videos/remi/1/video_1_240.mp4", encodingFormat="video/mp4")
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile="videos/remi/1/video_1_240.webm", encodingFormat="video/webm")

        pod.channel.add(c)
        pod.theme.add(t)
        pod.save()
        print (" --->  SetUp of Video_notesTestView : OK !")

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
        print (
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
        print (
            "   --->  test_video_notes_not_authenticated of Video_notesTestView : OK !")


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
        c = Channel.objects.create(title="ChannelTest1", visible=True,
                                   color="Black", owner=user, style="italic", description="blabla")
        t = Theme.objects.create(
            title="Theme1", channel=c)
        other_type = Type.objects.get(id=1)
        pod = Pod.objects.create(type=other_type, title=u'Bunny',
                                 date_added=datetime.today(), owner=user, date_evt=datetime.today(), video="videos/remi/test.mp4", overview=u'videos/remi/1/overview.jpg',
                                 allow_downloading=True, duration=33, encoding_in_progress=False, view_count=0, description="fl", is_draft=True,
                                 to_encode=False)
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile="videos/remi/1/video_1_240.mp4", encodingFormat="video/mp4")
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile="videos/remi/1/video_1_240.webm", encodingFormat="video/webm")

        pod.channel.add(c)
        pod.theme.add(t)
        pod.save()
        print (" --->  SetUp of Video_completion_TestView : OK !")

    def test_video_completion(self):
        pod = Pod.objects.get(id=1)
        response = self.client.get("/video_completion/%s/" % pod.slug)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse('account_login') + '?next=/video_completion/%s/' % pod.slug, status_code=302, target_status_code=200, msg_prefix='')
        print (
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
        self.assertTrue("You cannot complete this video" in response.content)
        print (
            "   --->  test_completion_with_authenticated of Video_completion_TestView : OK !")

    def test_completion_post_request(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        self.user = User.objects.get(username="remi")
        self.user = authenticate(
            username='remi', password='hello', is_staff=True)
        login = self.client.login(
            username='remi', password='hello', is_staff=True)
        self.assertEqual(login, True)
        response = self.client.get("/video_completion/%s/" % pod.slug)
        self.assertEqual(response.status_code, 200)
        response = response = self.client.post("/video_completion/%s/" % pod.slug,
                                               {u'track_form-TOTAL_FORMS': [u'0'], u'contributor_form-0-name': [u'l'], u'contributor_form-0-weblink': [u''], u'contributor_form-TOTAL_FORMS': [u'1'], u'contributor_form-MAX_NUM_FORMS': [u'1000'], u'action1': [u'Enregistrer'], u'doc_form-INITIAL_FORMS': [u'0'], u'doc_form-TOTAL_FORMS': [u'0'],
                                                u'contributor_form-0-email_address': [u''], u'doc_form-MAX_NUM_FORMS': [u'1000'], u'contributor_form-0-role': [u'authors'], u'referer': [u''],
                                                u'track_form-INITIAL_FORMS': [u'0'], u'contributor_form-0-id': [u''], u'contributor_form-INITIAL_FORMS': [u'0'], u'csrfmiddlewaretoken': [u'lPzdMGHrywbqLt9PfraVgYWUabjjLawg'],
                                                u'track_form-MAX_NUM_FORMS': [u'1000'], u'contributor_form-0-video': [u'1']})
        self.assertEqual(response.status_code, 200)
        ContributorInlineFormSet = inlineformset_factory(
            Pod, ContributorPods, form=ContributorPodsForm, extra=0, can_delete=True)
        contributorformset = ContributorInlineFormSet(
            instance=Pod.objects.get(id=1), prefix='contributor_form')
        self.assertEqual(
            list(contributorformset.queryset), list(response.context['contributorformset'].queryset))
        print (
            "   --->  test_completion_post_request of Video_completion_TestView : OK !")

    def test_completion_other_post_request(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        user = User.objects.get(username="remi")
        user.is_staff = False
        user.save()
        user = authenticate(
            username='remi', password='hello')
        login = self.client.login(
            username='remi', password='hello')
        self.assertEqual(login, True)
        response = self.client.get("/video_completion/%s/" % pod.slug)
        self.assertEqual(response.status_code, 200)
        response = response = self.client.post("/video_completion/%s/" % pod.slug,
                                               {u'track_form-0-src': [u''], u'track_form-TOTAL_FORMS': [u'1'], u'doc_form-INITIAL_FORMS': [u'0'],
                                                u'contributor_form-TOTAL_FORMS': [u'0'], u'track_form-0-id': [u''], u'track_form-0-lang': [u'as'],
                                                u'action2': [u'Save and back to the previous page'], u'track_form-0-kind': [u'subtitles'], u'doc_form-TOTAL_FORMS': [u'0'],
                                                u'doc_form-MAX_NUM_FORMS': [u'1000'], u'track_form-0-video': [u'1'], u'referer': [u''],
                                                u'track_form-INITIAL_FORMS': [u'0'], u'contributor_form-MAX_NUM_FORMS': [u'1000'], u'contributor_form-INITIAL_FORMS': [u'0'],
                                                u'track_form-MAX_NUM_FORMS': [u'1000']})
        self.assertEqual(response.status_code, 200)
        ContributorInlineFormSet = inlineformset_factory(
            Pod, ContributorPods, form=ContributorPodsForm, extra=0, can_delete=True)
        contributorformset = ContributorInlineFormSet(
            instance=Pod.objects.get(id=1), prefix='contributor_form')
        self.assertEqual(
            list(contributorformset.queryset), list(response.context['contributorformset'].queryset))
        print (
            "   --->  test_completion_other_post_request of Video_completion_TestView : OK !")


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
                                   color="Black", owner=user, style="italic", description="blabla")
        t = Theme.objects.create(
            title="Theme1", channel=c)
        other_type = Type.objects.get(id=1)
        pod = Pod.objects.create(type=other_type, title=u'Bunny',
                                 date_added=datetime.today(), owner=user, date_evt=datetime.today(), video="videos/remi/test.mp4", overview=u'videos/remi/1/overview.jpg',
                                 allow_downloading=True, duration=33, encoding_in_progress=False, view_count=0, description="fl", is_draft=True,
                                 to_encode=False)
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile="videos/remi/1/video_1_240.mp4", encodingFormat="video/mp4")
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile="videos/remi/1/video_1_240.webm", encodingFormat="video/webm")

        pod.channel.add(c)
        pod.theme.add(t)
        pod.save()
        print (" --->  SetUp of Video_chapterTestView : OK !")

    def test_insert_chapter(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        user = User.objects.get(username="remi")
        user.is_staff = False
        user.save()
        user = authenticate(
            username='remi', password='hello')
        login = self.client.login(
            username='remi', password='hello')
        self.assertEqual(login, True)
        response = self.client.get("/video_chapter/%s/" % pod.slug)
        self.assertEqual(response.status_code, 200)
        response = self.client.post("/video_chapter/%s/" % pod.slug, {u'chapter_form-TOTAL_FORMS': [u'1'], u'chapter_form-0-title': [u'hjkl'],
                                                                      u'chapter_form-INITIAL_FORMS': [u'0'], u'action1': [u'Enregistrer'], u'chapter_form-MAX_NUM_FORMS': [u'1000'], u'chapter_form-0-time': [u'0'],
                                                                      u'chapter_form-0-video': [u'1'], u'csrfmiddlewaretoken': [u'lPzdMGHrywbqLt9PfraVgYWUabjjLawg'], u'chapter_form-0-id': [u'']})
        ChapterInlineFormSet = inlineformset_factory(
            Pod, ChapterPods, form=ChapterPodsForm, extra=0, can_delete=True)
        chapterformset = ChapterInlineFormSet(
            instance=Pod.objects.get(id=1), prefix='chapter_form')
        self.assertEqual(
            list(chapterformset.queryset), list(response.context['chapterformset'].queryset))
        print (
            "   --->  test_insert_chapter of Video_chapterTestView : OK !")

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
        self.assertTrue("You cannot chapter this video" in response.content)


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
                                   color="Black", owner=user, style="italic", description="blabla")
        t = Theme.objects.create(
            title="Theme1", channel=c)
        other_type = Type.objects.get(id=1)
        pod = Pod.objects.create(type=other_type, title=u'Bunny',
                                 date_added=datetime.today(), owner=user, date_evt=datetime.today(), video="videos/remi/test.mp4", overview="videos/remi/1/overview.jpg",
                                 allow_downloading=True, duration=33, encoding_in_progress=False, view_count=0, description="fl", is_draft=True,
                                 to_encode=False)
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile="videos/remi/1/video_1_240.mp4", encodingFormat="video/mp4")
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile="videos/remi/1/video_1_240.webm", encodingFormat="video/webm")

        pod.channel.add(c)
        pod.theme.add(t)
        pod.save()
        print (" --->  SetUp of Video_enrichTestView : OK !")

    def test_insert_enrich(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        user = User.objects.get(username="remi")
        user = authenticate(
            username='remi', password='hello')
        login = self.client.login(
            username='remi', password='hello')
        self.assertEqual(login, True)
        response = self.client.get("/video_enrich/%s/" % pod.slug)
        self.assertEqual(response.status_code, 200)
        response = self.client.post("/video_enrich/%s/" % pod.slug, {u'enrich_form-0-type': [u'richtext'], u'enrich_form-0-id': [u''],
                                                                     u'enrich_form-0-title': [u'dfghdfgh'], u'enrich_form-0-weblink': [u''], u'action1': [u'Enregistrer'], u'enrich_form-INITIAL_FORMS': [u'0'],
                                                                     u'enrich_form-0-document': [u''], u'enrich_form-TOTAL_FORMS': [u'1'], u'enrich_form-0-image': [u''], u'enrich_form-MAX_NUM_FORMS': [u'1000'],
                                                                     u'enrich_form-0-richtext': [u'<p>fdghdfghdfhdfh</p>\r\n'], u'enrich_form-0-embed': [u''], u'enrich_form-0-video': [u'1'],
                                                                     u'enrich_form-0-end': [u'5'], u'enrich_form-0-start': [u'1']})
        EnrichInlineFormSet = inlineformset_factory(
            Pod, EnrichPods, form=EnrichPodsForm, extra=0, can_delete=True)
        enrichformset = EnrichInlineFormSet(
            instance=Pod.objects.get(id=1), prefix='enrich_form')
        self.assertEqual(
            list(enrichformset.queryset), list(response.context['enrichformset'].queryset))
        print (
            "   --->  test_insert_enrich of Video_enrichTestView : OK !")

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
        self.assertTrue("You cannot enrich this video" in response.content)
        print (
            "   --->  test_access_to_enrich_with_other_authenticating of Video_enrichTestView : OK !")


class Video_mediacourses(TestCase):
    fixtures = ['initial_data.json', ]
    def setUp(self):
        #user is staff but user2 not
        user = User.objects.create(
            username='remi', password='12345', is_active=True, is_staff=True)
        user.set_password('hello')
        user.save()

        user2 = User.objects.create(
            username='remi2', password='12345', is_active=True)
        user2.set_password('hello')
        user2.save()

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
        self.assertEqual(self.client.session['_auth_user_id'], user.pk)
        self.client.logout()
        self.assertTrue(self.client.session.get('_auth_user_id')==None)

    def test_access_user_mediacourses_add(self):
        self.client = Client()
        user = User.objects.get(username="remi2")
        user = authenticate(
            username='remi2', password='hello')
        login = self.client.login(
            username='remi2', password='hello')
        self.assertEqual(login, True)
        self.assertEqual(self.client.session['_auth_user_id'], user.pk)
        response = self.client.get("/mediacourses_add/?mediapath=abcdefg.zip")
        self.assertTrue("this_is_the_login_form" in response.content)

    def test_access_user_mediacourses_add_without_mediapath(self):
        self.client = Client()
        user = User.objects.get(username="remi")
        user = authenticate(
            username='remi', password='hello')
        login = self.client.login(
            username='remi', password='hello')
        self.assertEqual(login, True)
        response = self.client.get("/mediacourses_add/?mediapath=abcdefg.zip")
        self.assertEqual(response.status_code, 403)
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

    