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

    def setUp(self):
        group, created = Group.objects.get_or_create(name='can delete file')
        remi = User.objects.create_user("Remi")
        i = 1
        while i <= 15:
            Channel.objects.create(title="ChannelTest" + str(i), visible=True,
                                   color="Black", owner=remi, style="italic", description="blabla")
            i += 1

        t = Theme.objects.create(
            title="Theme1", channel=Channel.objects.get(id=1))
        type1 = Type.objects.create(title="Type1")
        pod = Pod.objects.create(type=type1, title="Video2", encoding_status="b", encoding_in_progress=True,
                                 date_added=datetime.today(), owner=remi, date_evt=datetime.today(), video="example.mp4",
                                 allow_downloading=True, view_count=2, description="fl", overview="schema_bdd.jpg", is_draft=False,
                                 duration=3, infoVideo="videotest", to_encode=True)

        rootFolder = Folder.objects.create(
            name=pod.owner, owner=pod.owner, level=0)
        folder = Folder.objects.create(
            name=pod.slug, owner=pod.owner, parent=rootFolder)
        upc_image1 = Image.objects.create(
            folder=folder, name="%s_%s.png" % (pod.slug, 1))
        pod.thumbnail = upc_image1
        EncodingType.objects.create(
            name="test_encoding", bitrate_audio=300, bitrate_video=300)
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1))
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

    def setUp(self):
        group, created = Group.objects.get_or_create(name='can delete file')
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

    def setUp(self):
        group, created = Group.objects.get_or_create(name='can delete file')
        remi = User.objects.create(username='testuser')
        c = Channel.objects.create(title="ChannelTest1", visible=True,
                                   color="Black", owner=remi, style="italic", description="blabla")
        t = Theme.objects.create(
            title="Theme1", channel=c)
        type1 = Type.objects.create(title="Type1")
        pod = Pod.objects.create(type=type1, title="Video2", encoding_status="b", encoding_in_progress=True,
                                 date_added=datetime.today(), owner=remi, date_evt=datetime.today(), video="example.mp4",
                                 allow_downloading=True, view_count=2, description="fl", overview="schema_bdd.jpg", is_draft=False,
                                 duration=3, infoVideo="videotest", to_encode=True)

        rootFolder = Folder.objects.create(
            name=pod.owner, owner=pod.owner, level=0)
        folder = Folder.objects.create(
            name=pod.slug, owner=pod.owner, parent=rootFolder)
        upc_image1 = Image.objects.create(
            folder=folder, name="%s_%s.png" % (pod.slug, 1))
        pod.thumbnail = upc_image1
        EncodingType.objects.create(
            name="test_encoding", bitrate_audio=300, bitrate_video=300)
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1))
        pod.save()
        pod.theme.add(t)
        pod.channel.add(Channel.objects.get(id=1))
        pod.save()
        pod.theme.add(t)
        print (" --->  SetUp of ChannelTestView : OK !")

    def test_channel_without_theme_in_argument(self):
        self.client = Client()
        response = self.client.get("/channeltest1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context[u"channel"], Channel.objects.get(id=1))
        self.assertEqual(
            response.context[u"theme"], None)
        print (
            "   --->  test_channel_without_theme_in_argument of ChannelTestView : OK !")

    def test_channel_with_theme_in_argument(self):
        self.client = Client()
        response = self.client.get("/channeltest1/theme1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context[u"channel"], Channel.objects.get(id=1))
        self.assertEqual(
            response.context[u"theme"], Theme.objects.get(channel=Channel.objects.get(id=1)))
        print (
            "   --->  test_channel_with_theme_in_argument of ChannelTestView : OK !")

    def test_channel_with_ajax_request(self):
        response = self.client.get(
            "/channeltest1/", perpage=48,  HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request[u'REQUEST_METHOD'], 'GET')
        self.assertEqual(response.request['perpage'], 48)
        print (
            "   --->  test_channel_with_ajax_request of ChannelTestView : OK !")


class Channel_edit_TestView(TestCase):

    def setUp(self):
        group, created = Group.objects.get_or_create(name='can delete file')
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
        response = self.client.get("/channeltest1/edit")
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
        response = self.client.post('/channeltest1/edit', {u'style': [u'italicdss'], u'description': [u'<p>blabladsvvvv</p>\r\n'], u'action1': [u'Enregistrer'], u'referer': [
                                    u'/channeltest1/edit'], u'themes-TOTAL_FORMS': [u'0'], u'headband': [u''], u'themes-INITIAL_FORMS': [u'0']})
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
        response = self.client.get('/channeltest1/edit')
        self.assertEqual(response.status_code, 403)
        self.assertTrue("You cannot edit this channel" in response.content)
        self.assertFalse(channel.description == u'<p>ba</p>\r\n')
        print (
            "   --->  test_channel_edit_user of Channel_edit_TestView : OK !")

    def test_redirection_to_previous_page(self):
        self.client = Client()
        self.user = User.objects.get(username="testuser")
        self.user = authenticate(username='testuser', password='hello')
        login = self.client.login(username='testuser', password='hello')
        self.assertEqual(login, True)
        response = self.client.post('/channeltest1/edit', {u'description': [u'<p>bl</p>\r\n'], u'action2': [u'Save and back to previous page'], u'referer': [
                                    u'/channels/'], u'themes-TOTAL_FORMS': [u'0'], u'themes-INITIAL_FORMS': [u'0']}, follow=True)
        self.assertEqual(response.status_code, 200)
        channel = Channel.objects.get(id=1)
        self.assertTrue(channel.description, u'<p>bl</p>\r\n')
        self.assertRedirects(
            response, u'/channels/', status_code=302, target_status_code=200, msg_prefix='')
        print (
            "   --->  test_redirection_to_previous_page of Channel_edit_TestView : OK !")

    def test_redirection_to_the_channel(self):
        self.client = Client()
        self.user = User.objects.get(username="testuser")
        self.user = authenticate(username='testuser', password='hello')
        login = self.client.login(username='testuser', password='hello')
        self.assertEqual(login, True)
        response = self.client.post('/channeltest1/edit', {u'description': [u'<p>bl</p>\r\n'], u'action3': [u'Save and see channel'], u'referer': [
                                    u'/channels/'], u'themes-TOTAL_FORMS': [u'0'], u'themes-INITIAL_FORMS': [u'0']}, follow=True)
        self.assertEqual(response.status_code, 200)
        channel = Channel.objects.get(id=1)
        self.assertTrue(channel.description, u'<p>bl</p>\r\n')
        self.assertRedirects(
            response, u'/channeltest1/', status_code=302, target_status_code=200, msg_prefix='')
        print (
            "   --->  test_redirection_to_the_channel of Channel_edit_TestView : OK !")


class TypesTestView(TestCase):

    def setUp(self):
        group, created = Group.objects.get_or_create(name='can delete file')
        remi = User.objects.create_user(username="remi")
        type1 = Type.objects.create(title="Type1")
        pod = Pod.objects.create(type=type1, title="Video2", encoding_status="b", encoding_in_progress=True,
                                 date_added=datetime.today(), owner=remi, date_evt=datetime.today(), video="example.mp4",
                                 allow_downloading=True, view_count=2, description="fl", overview="schema_bdd.jpg", is_draft=False,
                                 duration=3, infoVideo="videotest", to_encode=True)

        rootFolder = Folder.objects.create(
            name=pod.owner, owner=pod.owner, level=0)
        folder = Folder.objects.create(
            name=pod.slug, owner=pod.owner, parent=rootFolder)
        upc_image1 = Image.objects.create(
            folder=folder, name="%s_%s.png" % (pod.slug, 1))
        pod.thumbnail = upc_image1
        EncodingType.objects.create(
            name="test_encoding", bitrate_audio=300, bitrate_video=300)
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1))
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

    def setUp(self):
        group, created = Group.objects.get_or_create(name='can delete file')
        remi = User.objects.create_user(username="Remi", last_name="Lefevbre")
        type1 = Type.objects.create(title="Type1")
        pod = Pod.objects.create(type=type1, title="Video2", encoding_status="b", encoding_in_progress=True,
                                 date_added=datetime.today(), owner=remi, date_evt=datetime.today(), video="example.mp4",
                                 allow_downloading=True, view_count=2, description="fl", overview="schema_bdd.jpg", is_draft=False,
                                 duration=3, infoVideo="videotest", to_encode=True)

        rootFolder = Folder.objects.create(
            name=pod.owner, owner=pod.owner, level=0)
        folder = Folder.objects.create(
            name=pod.slug, owner=pod.owner, parent=rootFolder)
        upc_image1 = Image.objects.create(
            folder=folder, name="%s_%s.png" % (pod.slug, 1))
        pod.thumbnail = upc_image1
        EncodingType.objects.create(
            name="test_encoding", bitrate_audio=300, bitrate_video=300)
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1))
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

    def setUp(self):
        group, created = Group.objects.get_or_create(name='can delete file')
        remi = User.objects.create_user(username="remi")
        Discipline.objects.create(title="Discipline1")
        type1 = Type.objects.create(title="Type1")
        d1 = Discipline.objects.create(title="Discipline2")
        pod = Pod.objects.create(type=type1, title="Video2", encoding_status="b", encoding_in_progress=True,
                                 date_added=datetime.today(), owner=remi, date_evt=datetime.today(), video="example.mp4",
                                 allow_downloading=True, view_count=2, description="fl", overview="schema_bdd.jpg", is_draft=False,
                                 duration=3, infoVideo="videotest", to_encode=True)

        rootFolder = Folder.objects.create(
            name=pod.owner, owner=pod.owner, level=0)
        folder = Folder.objects.create(
            name=pod.slug, owner=pod.owner, parent=rootFolder)
        upc_image1 = Image.objects.create(
            folder=folder, name="%s_%s.png" % (pod.slug, 1))
        pod.thumbnail = upc_image1
        EncodingType.objects.create(
            name="test_encoding", bitrate_audio=300, bitrate_video=300)
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1))
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

    def setUp(self):
        group, created = Group.objects.get_or_create(name='can delete file')
        self.user = User.objects.create(
            username='testuser', password='12345', is_active=True, is_staff=True, is_superuser=True)
        self.user.set_password('hello')
        self.user.save()
        type1 = Type.objects.create(title="Type1")
        i = 1
        while i < 3:
            pod = Pod.objects.create(type=type1, title="Video" + str(i), encoding_status="b", encoding_in_progress=True,
                                     date_added=datetime.today(), owner=self.user, date_evt=datetime.today(), video="example.mp4",
                                     allow_downloading=True, view_count=2, description="fl", overview="schema_bdd.jpg", is_draft=False,
                                     duration=3, infoVideo="videotest", to_encode=True)
            rootFolder = Folder.objects.create(
                name=pod.owner, owner=pod.owner, level=0)
            folder = Folder.objects.create(
                name=pod.slug, owner=pod.owner, parent=rootFolder)
            upc_image1 = Image.objects.create(
                folder=folder, name="%s_%s.png" % (pod.slug, 1))
            pod.thumbnail = upc_image1
            EncodingType.objects.create(
                name="test_encoding", bitrate_audio=300, bitrate_video=300)
            EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
                id=1))
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

    def setUp(self):
        group, created = Group.objects.get_or_create(name='can delete file')
        remi = User.objects.create_user(username="remi")
        type1 = Type.objects.create(title="Type1")
        pod = Pod.objects.create(type=type1, title="Video2", encoding_status="b", encoding_in_progress=True,
                                 date_added=datetime.today(), owner=remi, date_evt=datetime.today(), video="example.mp4",
                                 allow_downloading=True, view_count=2, description="fl", overview="schema_bdd.jpg", is_draft=False,
                                 duration=3, infoVideo="videotest", to_encode=True)
        rootFolder = Folder.objects.create(
            name=pod.owner, owner=pod.owner, level=0)
        folder = Folder.objects.create(
            name=pod.slug, owner=pod.owner, parent=rootFolder)
        upc_image1 = Image.objects.create(
            folder=folder, name="%s_%s.png" % (pod.slug, 1))
        pod.thumbnail = upc_image1
        EncodingType.objects.create(
            name="test_encoding", bitrate_audio=300, bitrate_video=300)
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1))
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

    def setUp(self):
        group, created = Group.objects.get_or_create(name='can delete file')
        user = User.objects.create(
            username='testuser', password='12345', is_active=True, is_staff=False)
        user.set_password('hello')
        user.save()
        user2 = User.objects.create(
            username='testuser2', password='12345', is_active=True, is_staff=False)
        user2.set_password('hello')
        user2.save()
        type1 = Type.objects.create(title="Type1")
        pod = Pod.objects.create(type=type1, title="Video2", encoding_status="b", encoding_in_progress=True,
                                 date_added=datetime.today(), owner=user2, date_evt=datetime.today(), video="example.mp4",
                                 allow_downloading=True, view_count=2, description="fl", overview="schema_bdd.jpg", is_draft=False,
                                 duration=3, infoVideo="videotest", to_encode=True)

        rootFolder = Folder.objects.create(
            name=pod.owner, owner=pod.owner, level=0)
        folder = Folder.objects.create(
            name=pod.slug, owner=pod.owner, parent=rootFolder)
        upc_image1 = Image.objects.create(
            folder=folder, name="%s_%s.png" % (pod.slug, 1))
        pod.thumbnail = upc_image1
        EncodingType.objects.create(
            name="test_encoding", bitrate_audio=300, bitrate_video=300)
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile="/videos/Remi/example.mp4")
        pod.save()
        print (" --->  SetUp of Video_add_favoriteTestView : OK !")

    def test_add_favorite(self):
        self.client = Client()
        self.user = User.objects.get(username="testuser")
        self.user = authenticate(username='testuser', password='hello')
        login = self.client.login(username='testuser', password='hello')
        self.assertEqual(login, True)
        response = self.client.post(
            "/video_add_favorite/0001-video2/", {u'csrfmiddlewaretoken': [u'sGqNLim1IYHikKhAeCXUcn55O6Fny8ZG']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Favorites.objects.get(user=self.user).video, Pod.objects.get(id=1))

        print (
            "   --->  test_add_favorite_with_ajax_requete of Video_add_favoriteTestView : OK !")

    def test_video_edit_not_good_user(self):
        self.client = Client()
        user = User.objects.get(username="testuser2")
        user = authenticate(username='testuser2', password='hello')
        login = self.client.login(username='testuser2', password='hello')
        self.assertEqual(login, True)
        response = self.client.get('/video_add_favorite/0001-video2/')
        self.assertEqual(response.status_code, 403)
        self.assertTrue("You cannot view this page" in response.content)

    def test_delete_favorite(self):
        self.client = Client()
        self.user = User.objects.get(username="testuser")
        self.user = authenticate(username='testuser', password='hello')
        login = self.client.login(username='testuser', password='hello')
        self.assertEqual(login, True)
        Favorites.objects.create(user=self.user, video=Pod.objects.get(id=1))
        response2 = self.client.post(
            "/video_add_favorite/0001-video2/", {u'csrfmiddlewaretoken': [u'sGqNLim1IYHikKhAeCXUcn5O6Fny8kZG']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(Favorites.objects.filter(user=self.user).count(), 0)
        print (
            "   --->  test_delete_favorite of Video_add_favoriteTestView : OK !")


class Favorites_videos_listTestView(TestCase):

    def setUp(self):
        group, created = Group.objects.get_or_create(name='can delete file')
        user = User.objects.create(
            username='testuser', password='12345', is_active=True, is_staff=False)
        user.set_password('hello')
        user.save()
        user2 = User.objects.create(
            username='testuser2', password='12345', is_active=True, is_staff=False)
        user2.set_password('hello')
        user2.save()
        type1 = Type.objects.create(title="Type1")
        i = 1
        while i < 5:
            pod = Pod.objects.create(type=type1, title="Video" + str(i), encoding_status="b", encoding_in_progress=True,
                                     date_added=datetime.today(), owner=user2, date_evt=datetime.today(), video="example.mp4",
                                     allow_downloading=True, view_count=2, description="fl", overview="schema_bdd.jpg", is_draft=False,
                                     duration=3, infoVideo="videotest", to_encode=True)

            rootFolder = Folder.objects.create(
                name=pod.owner, owner=pod.owner, level=0)
            folder = Folder.objects.create(
                name=pod.slug, owner=pod.owner, parent=rootFolder)
            upc_image1 = Image.objects.create(
                folder=folder, name="%s_%s.png" % (pod.slug, 1))
            pod.thumbnail = upc_image1
            EncodingType.objects.create(
                name="test_encoding", bitrate_audio=300, bitrate_video=300)
            EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
                id=1), encodingFile="/videos/Remi/example.mp4")
            pod.save()
            i += 1
        print (" --->  SetUp of Favorites_videos_listTestView : OK !")

    def test_favorites_video_list(self):
        self.client = Client()
        self.user = User.objects.get(username="testuser")
        self.user = authenticate(username='testuser', password='hello')
        login = self.client.login(username='testuser', password='hello')
        self.assertEqual(login, True)
        i = 1
        while i < 5:
            response = self.client.post(
                "/video_add_favorite/000" + str(i) + "-video" + str(i) + "/", {u'csrfmiddlewaretoken': [u'sGqNLim1IYHikKhAeCXUcn55O6Fny8ZG']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
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

    def setUp(self):
        group, created = Group.objects.get_or_create(name='can delete file')
        d1 = Discipline.objects.create(title="Discipline1")
        user = User.objects.create(
            username='remi', last_name="lefevbre",  password='12345', is_active=True, is_staff=False)
        user.set_password('hello')
        user.save()
        type1 = Type.objects.create(title="Type1")
        i = 1
        while i < 5:
            pod = Pod.objects.create(type=type1, title="Video" + str(i), encoding_status="b", encoding_in_progress=True,
                                     date_added=datetime.today(), owner=user, date_evt=datetime.today(), video="example.mp4",
                                     allow_downloading=True, view_count=0, description="fl", overview="schema_bdd.jpg", is_draft=False,
                                     duration=3, infoVideo="videotest", to_encode=True)

            rootFolder = Folder.objects.create(
                name=pod.owner, owner=pod.owner, level=0)
            folder = Folder.objects.create(
                name=pod.slug, owner=pod.owner, parent=rootFolder)
            upc_image1 = Image.objects.create(
                folder=folder, name="%s_%s.png" % (pod.slug, 1))
            pod.thumbnail = upc_image1
            EncodingType.objects.create(
                name="test_encoding", bitrate_audio=300, bitrate_video=300)
            EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
                id=1), encodingFile="/videos/Remi/example.mp4")
            pod.tags.add("videotests")
            pod.save()
            if i % 2:
                pod.discipline.add(d1)
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

    def setUp(self):
        group, created = Group.objects.get_or_create(name='can delete file')
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
        type1 = Type.objects.create(title="Type1")
        pod = Pod.objects.create(type=type1, title=u'Bunny',
                                 date_added=datetime.today(), owner=user, date_evt=datetime.today(), video="videos/root/bunny.mp4", overview=u'videos/root/11/overview.jpg',
                                 allow_downloading=True, duration=33, encoding_in_progress=False, view_count=0, description="fl", is_draft=True,
                                 to_encode=False)
        EncodingType.objects.create(
            name=240, bitrate_audio=300, bitrate_video=300)
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile="videos/root/11/video_11_240.mp4")
        pod.channel.add(c)
        pod.theme.add(t)
        pod.save()
        print (" --->  SetUp of videoTestView : OK !")

    def test_video(self):
        response = self.client.get("/video/0001-bunny/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse('account_login') + '?next=/video/0001-bunny/', status_code=302, target_status_code=200, msg_prefix='')
        pod = Pod.objects.get(id=1)
        pod.is_restricted = True
        pod.is_draft = False
        pod.save()
        response = self.client.get("/video/0001-bunny/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse('account_login') + '?next=/video/0001-bunny/', status_code=302, target_status_code=200, msg_prefix='')
        print (
            "   --->  test_video of VideoTestView : OK !")

    def test_video_draft_not_good_user(self):
        pod = Pod.objects.get(id=1)
        self.client = Client()
        user = User.objects.get(id=1)
        user = authenticate(username='remi2', password='hello')
        login = self.client.login(username='remi2', password='hello')
        self.assertEqual(login, True)
        response = self.client.get("/video/0001-bunny/")
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
        response = self.client.get("/video/0001-bunny/")
        self.assertEqual(response.status_code, 200)
        pod.is_draft = False
        pod.save()
        self.client = Client()
        user = User.objects.get(id=2)
        user = authenticate(username='remi2', password='hello')
        login = self.client.login(username='remi2', password='hello')
        self.assertEqual(login, True)
        response = self.client.get("/video/0001-bunny/")
        self.assertEqual(response.status_code, 200)
        print (
            "   --->  test_video_with_authenticated of VideoTestView : OK !")

    def test_video_password(self):
        pod = Pod.objects.get(id=1)
        pod.is_draft = False
        pod.password = u"toto"
        pod.save()
        self.client = Client()
        response = self.client.post("/channeltest1/theme1/video/0001-bunny/", {u'csrfmiddlewaretoken': [
                                    u'UjpqG82BJAKfVCrFAbBV1caEAn39FYj7'], u'password': [u'toto'], u'action1': [u'Send']})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context[u'channel'], Channel.objects.get(id=1))
        self.assertEqual(response.context[u'video'], pod)
        response = self.client.post("/video/0001-bunny/", {u'csrfmiddlewaretoken': [
                                    u'UjpqG82BJAKfVCrFAbBV1caEAn39FYj7'], u'password': [u'toto2'], u'action1': [u'Send']})
        self.assertEqual(response.status_code, 200)

        print (
            "   --->  test_video_password of VideoTestView : OK !")


class Video_edit_testCase(TestCase):

    def setUp(self):
        group, created = Group.objects.get_or_create(name='can delete file')
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
        type1 = Type.objects.create(title="Type1")
        pod = Pod.objects.create(type=type1, title=u'Bunny',
                                 date_added=datetime.today(), owner=user, date_evt=datetime.today(), video="videos/root/bunny.mp4", overview=u'videos/root/11/overview.jpg',
                                 allow_downloading=True, duration=33, encoding_in_progress=False, view_count=0, description="fl", is_draft=True,
                                 to_encode=False)
        EncodingType.objects.create(
            name=240, bitrate_audio=300, bitrate_video=300)
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile="videos/root/11/video_11_240.mp4")
        pod.channel.add(c)
        pod.theme.add(t)
        pod.save()
        print (" --->  SetUp of Video_edit_testCase : OK !")

    def test_video_edit(self):
        self.client = Client()
        response = self.client.get("/video_edit/0001-bunny/")
        self.assertEqual(response.status_code, 302)
        print (
            "   --->  test_video_edit of Video_edit_testCase : OK !")

    def test_video_edit_not_good_user(self):
        self.client = Client()
        user = User.objects.get(username="remi2")
        user = authenticate(username='remi2', password='hello')
        login = self.client.login(username='remi2', password='hello')
        self.assertEqual(login, True)
        response = self.client.post('/video_edit/0001-bunny/')
        self.assertEqual(response.status_code, 403)
        self.assertTrue("You cannot edit this video" in response.content)
        print (
            "   --->  test_video_edit_not_good_user of Video_edit_testCase : OK !")

    def test_edit_video_redirection_to_previous_page(self):
        self.client = Client()
        self.user = User.objects.get(username="remi")
        self.user = authenticate(username='remi', password='hello')
        login = self.client.login(username='remi', password='hello')
        self.assertEqual(login, True)
        print Pod.objects.get(id=1).owner.id
        response = self.client.post('/video_edit/0001-bunny/', {u'password': [u''], u'description': [u'<p>sdfsdf</p>\r\n'], u'title': [u'Bunny'], u'tags': [u''], u'action2': [u'Save and back to the previous page'], u'date_evt': [
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
        self.client = Client()
        self.user = User.objects.get(username="remi")
        self.user = authenticate(username='remi', password='hello')
        login = self.client.login(username='remi', password='hello')
        self.assertEqual(login, True)
        response = self.client.post('/video_edit/0001-bunny/', {u'password': [u'b'], u'description': [u'<p>bbla</p>\r\n'], u'title': [u'Bunny'], u'tags': [u''], u'action3': [u'Save and watch the video'], u'date_evt': [
                                    u''], u'video': [u''], u'date_added': [u'20/04/2015'], u'allow_downloading': [u'on'], u'type': [u'1']})
        self.assertEqual(response.status_code, 302)
        video = Pod.objects.get(id=1)
        self.assertEqual(video.password, "b")
        self.assertRedirects(
            response, u'/video/0001-bunny/', status_code=302, target_status_code=200, msg_prefix='')
        print (
            "   --->  test_save_edit_video of Video_edit_testCase : OK !")


class Video_notesTestView(TestCase):

    def setUp(self):
        group, created = Group.objects.get_or_create(name='can delete file')
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
        type1 = Type.objects.create(title="Type1")
        pod = Pod.objects.create(type=type1, title=u'Bunny',
                                 date_added=datetime.today(), owner=user, date_evt=datetime.today(), video="videos/root/bunny.mp4", overview=u'videos/root/11/overview.jpg',
                                 allow_downloading=True, duration=33, encoding_in_progress=False, view_count=0, description="fl", is_draft=True,
                                 to_encode=False)
        EncodingType.objects.create(
            name=240, bitrate_audio=300, bitrate_video=300)
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile="videos/root/11/video_11_240.mp4")
        pod.channel.add(c)
        pod.theme.add(t)
        pod.save()
        print (" --->  SetUp of Video_notesTestView : OK !")

    def test_video_notes(self):
        self.client = Client()
        self.user = User.objects.get(username="remi")
        self.user = authenticate(username='remi', password='hello')
        login = self.client.login(username='remi', password='hello')
        self.assertEqual(login, True)
        response = self.client.post(
            '/video_notes/0001-bunny/', {u'note': [u'dddd']}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Notes.objects.get(video=Pod.objects.get(id=1), user=self.user).note, u'dddd')
        print (
            "   --->  test_video_notes of Video_notesTestView : OK !")

    def test_video_notes_not_authenticated(self):
        self.client = Client()
        user = User.objects.get(username="remi2")
        user = authenticate(username='remi2', password='hello')
        login = self.client.login(username='remi2', password='hello')
        self.assertEqual(login, True)
        response = self.client.post('/video_notes/0001-bunny/')
        self.assertEqual(response.status_code, 403)
        print (
            "   --->  test_video_notes_not_authenticated of Video_notesTestView : OK !")


class Video_completion_TestView(TestCase):

    def setUp(self):
        group, created = Group.objects.get_or_create(name='can delete file')
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
        type1 = Type.objects.create(title="Type1")
        pod = Pod.objects.create(type=type1, title=u'Bunny',
                                 date_added=datetime.today(), owner=user, date_evt=datetime.today(), video="videos/root/bunny.mp4", overview=u'videos/root/11/overview.jpg',
                                 allow_downloading=True, duration=33, encoding_in_progress=False, view_count=0, description="fl", is_draft=True,
                                 to_encode=False)
        EncodingType.objects.create(
            name=240, bitrate_audio=300, bitrate_video=300)
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile="videos/root/11/video_11_240.mp4")
        pod.channel.add(c)
        pod.theme.add(t)
        pod.save()
        print (" --->  SetUp of Video_completion_TestView : OK !")

    def test_video_completion(self):
        response = self.client.get("/video_completion/0001-bunny/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse('account_login') + '?next=/video_completion/0001-bunny/', status_code=302, target_status_code=200, msg_prefix='')
        print (
            "   --->  test_video_completion of Video_completion_TestView : OK !")

    def test_completion_with_authenticated(self):
        self.client = Client()
        self.user = User.objects.get(username="remi2")
        self.user = authenticate(username='remi2', password='hello')
        login = self.client.login(username='remi2', password='hello')
        self.assertEqual(login, True)
        response = self.client.get("/video_completion/0001-bunny/")
        self.assertEqual(response.status_code, 403)
        self.assertTrue("You cannot complete this video" in response.content)
        print (
            "   --->  test_completion_with_authenticated of Video_completion_TestView : OK !")

    def test_completion_post_request(self):
        self.client = Client()
        self.user = User.objects.get(username="remi")
        self.user = authenticate(
            username='remi', password='hello', is_staff=True)
        login = self.client.login(
            username='remi', password='hello', is_staff=True)
        self.assertEqual(login, True)
        response = self.client.get("/video_completion/0001-bunny/")
        self.assertEqual(response.status_code, 200)
        response = response = self.client.post("/video_completion/0001-bunny/",
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
        self.client = Client()
        user = User.objects.get(username="remi")
        user.is_staff = False
        user.save()
        user = authenticate(
            username='remi', password='hello')
        login = self.client.login(
            username='remi', password='hello')
        self.assertEqual(login, True)
        response = self.client.get("/video_completion/0001-bunny/")
        self.assertEqual(response.status_code, 200)
        response = response = self.client.post("/video_completion/0001-bunny/",
                                               {u'track_form-0-src': [u''], u'track_form-TOTAL_FORMS': [u'1'], u'doc_form-INITIAL_FORMS': [u'0'],
                                                u'contributor_form-TOTAL_FORMS': [u'0'], u'track_form-0-id': [u''], u'track_form-0-lang': [u'as'],
                                                u'action2': [u'Save and back to the previous page'], u'track_form-0-kind': [u'subtitles'], u'doc_form-TOTAL_FORMS': [u'0'],
                                                u'doc_form-MAX_NUM_FORMS': [u'1000'], u'track_form-0-video': [u'1'], u'referer': [u''],
                                                u'track_form-INITIAL_FORMS': [u'0'], u'contributor_form-MAX_NUM_FORMS': [u'1000'], u'contributor_form-INITIAL_FORMS': [u'0'],
                                                u'csrfmiddlewaretoken': [u'lPzdMGHrywbqLt9PfraVgYWUabjjLawg'], u'track_form-MAX_NUM_FORMS': [u'1000']})
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

    def setUp(self):
        group, created = Group.objects.get_or_create(name='can delete file')
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
        type1 = Type.objects.create(title="Type1")
        pod = Pod.objects.create(type=type1, title=u'Bunny',
                                 date_added=datetime.today(), owner=user, date_evt=datetime.today(), video="videos/root/bunny.mp4", overview=u'videos/root/11/overview.jpg',
                                 allow_downloading=True, duration=33, encoding_in_progress=False, view_count=0, description="fl", is_draft=True,
                                 to_encode=False)
        EncodingType.objects.create(
            name=240, bitrate_audio=300, bitrate_video=300)
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile="videos/root/11/video_11_240.mp4")
        pod.channel.add(c)
        pod.theme.add(t)
        pod.save()
        print (" --->  SetUp of Video_chapterTestView : OK !")

    def test_insert_chapter(self):
        self.client = Client()
        user = User.objects.get(username="remi")
        user.is_staff = False
        user.save()
        user = authenticate(
            username='remi', password='hello')
        login = self.client.login(
            username='remi', password='hello')
        self.assertEqual(login, True)
        response = self.client.get("/video_chapter/0001-bunny/")
        self.assertEqual(response.status_code, 200)
        response = self.client.post("/video_chapter/0001-bunny/", {u'chapter_form-TOTAL_FORMS': [u'1'], u'chapter_form-0-title': [u'hjkl'],
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
        self.client = Client()
        user = User.objects.get(username="remi2")
        user.is_staff = False
        user.save()
        user = authenticate(
            username='remi2', password='hello')
        login = self.client.login(
            username='remi2', password='hello')
        self.assertEqual(login, True)
        response = self.client.get("/video_chapter/0001-bunny/")
        self.assertEqual(response.status_code, 403)
        self.assertTrue("You cannot chapter this video" in response.content)


class Video_enrichTestView(TestCase):

    def setUp(self):
        group, created = Group.objects.get_or_create(name='can delete file')
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
        type1 = Type.objects.create(title="Type1")
        pod = Pod.objects.create(type=type1, title=u'Bunny',
                                 date_added=datetime.today(), owner=user, date_evt=datetime.today(), video="videos/root/bunny.mp4", overview=u'videos/root/11/overview.jpg',
                                 allow_downloading=True, duration=33, encoding_in_progress=False, view_count=0, description="fl", is_draft=True,
                                 to_encode=False)
        EncodingType.objects.create(
            name=240, bitrate_audio=300, bitrate_video=300)
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile="videos/root/11/video_11_240.mp4")
        pod.channel.add(c)
        pod.theme.add(t)
        pod.save()
        print (" --->  SetUp of Video_enrichTestView : OK !")

    def test_insert_enrich(self):
        self.client = Client()
        user = User.objects.get(username="remi")
        user.save()
        user = authenticate(
            username='remi', password='hello')
        login = self.client.login(
            username='remi', password='hello')
        self.assertEqual(login, True)
        response = self.client.get("/video_enrich/0001-bunny/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(login, True)
        response = self.client.post("/video_enrich/0001-bunny/", {u'enrich_form-0-type': [u'richtext'], u'enrich_form-0-id': [u''],
                                                                  u'enrich_form-0-title': [u'dfghdfgh'], u'enrich_form-0-weblink': [u''], u'action1': [u'Enregistrer'], u'enrich_form-INITIAL_FORMS': [u'0'],
                                                                  u'enrich_form-0-document': [u''], u'enrich_form-TOTAL_FORMS': [u'1'], u'enrich_form-0-image': [u''], u'enrich_form-MAX_NUM_FORMS': [u'1000'],
                                                                  u'enrich_form-0-richtext': [u'<p>fdghdfghdfhdfh</p>\r\n'], u'enrich_form-0-embed': [u''], u'enrich_form-0-video': [u'1'],
                                                                  u'csrfmiddlewaretoken': [u'lPzdMGHrywbqLt9PfraVgYWUabjjLawg'], u'enrich_form-0-end': [u'5'], u'enrich_form-0-start': [u'1']})
        EnrichInlineFormSet = inlineformset_factory(
            Pod, EnrichPods, form=EnrichPodsForm, extra=0, can_delete=True)
        enrichformset = EnrichInlineFormSet(
            instance=Pod.objects.get(id=1), prefix='enrich_form')
        self.assertEqual(login, True)
        self.assertEqual(
            list(enrichformset.queryset), list(response.context['enrichformset'].queryset))
        print (
            "   --->  test_insert_enrich of Video_enrichTestView : OK !")

    def test_access_to_enrich_with_other_authenticating(self):
        self.client = Client()
        user = User.objects.get(username="remi2")
        user.is_staff = False
        user.save()
        user = authenticate(
            username='remi2', password='hello')
        login = self.client.login(
            username='remi2', password='hello')
        self.assertEqual(login, True)
        response = self.client.get("/video_enrich/0001-bunny/")
        self.assertEqual(response.status_code, 403)
        self.assertTrue("You cannot enrich this video" in response.content)
        print (
            "   --->  test_access_to_enrich_with_other_authenticating of Video_enrichTestView : OK !")


class Video_deleteTestView(TestCase):

    def setUp(self):
        group, created = Group.objects.get_or_create(name='can delete file')
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
        type1 = Type.objects.create(title="Type1")
        pod = Pod.objects.create(type=type1, title=u'Bunny',
                                 date_added=datetime.today(), owner=user, date_evt=datetime.today(), video="videos/root/bunny.mp4", overview=u'videos/root/14/overview.jpg',
                                 allow_downloading=True, duration=33, encoding_in_progress=False, view_count=0, description="fl", is_draft=True,
                                 to_encode=False)
        EncodingType.objects.create(
            name=240, bitrate_audio=300, bitrate_video=300)
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile="videos/root/14/video_14_240.mp4")
        pod.channel.add(c)
        pod.theme.add(t)
        pod.save()
        print (" --->  SetUp of video_deleteTestView : OK !")

    def test_video_delete(self):
        self.client = Client()
        user = User.objects.get(username="remi")
        user.save()
        user = authenticate(
            username='remi', password='hello')
        login = self.client.login(
            username='remi', password='hello')
        self.assertEqual(login, True)
        response = self.client.get("/video_delete/0001-bunny/")
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            "/video_delete/0001-bunny/", {u'action1': [u'delete']})
        self.assertEqual(Pod.objects.all().count(), 0)
        print (
            "   --->  test_video_delete of video_deleteTestView : OK !")

    def test_acces_to_delete_with_other_authenticating(self):
        self.client = Client()
        user = User.objects.get(username="remi2")
        user.is_staff = False
        user.save()
        user = authenticate(
            username='remi2', password='hello')
        login = self.client.login(
            username='remi2', password='hello')
        self.assertEqual(login, True)
        response = self.client.get("/video_delete/0001-bunny/")
        self.assertEqual(response.status_code, 403)
        self.assertTrue('You can\'t delete this video' in response.content)
        print (
            "   --->  test_acces_to_delete_with_other_authenticating of video_deleteTestView : OK !")
"""
class Video_encodingTestView(TestCase):

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
        test_type = Type.objects.create(title="typecreate")
        pod = Pod.objects.create(type=test_type, title=u'Bunny',
                                 date_added=datetime.today(), owner=user, date_evt=datetime.today(), video="videos/root/bunny.mp4", overview=u'videos/root/11/overview.jpg',
                                 allow_downloading=True, duration=33, encoding_in_progress=False, view_count=0, description="fl", is_draft=True,
                                 to_encode=True)
        EncodingType.objects.create(
            name=240, bitrate_audio=300, bitrate_video=300)
        EncodingPods.objects.create(video=pod, encodingType=EncodingType.objects.get(
            id=1), encodingFile="videos/root/11/video_11_240.mp4")
        pod.channel.add(c)
        pod.theme.add(t)
        pod.save()
        print (" --->  SetUp of Video_encodingTestView : OK !")        

    def tests_encoding(self):
        print Pod.objects.get(id=1)"""
