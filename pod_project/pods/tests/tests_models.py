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
import urllib3
import shutil
from django.core.files.temp import NamedTemporaryFile
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User, Group
from filer.models.imagemodels import Image
from django.test import Client
from django.test.client import RequestFactory
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your tests here.
"""
    test the channel
"""


class ChannelTestCase(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        remi = User.objects.create_user("Remi")
        Channel.objects.create(title="ChannelTest1", slug="blabla", owner=remi)
        Channel.objects.create(title="ChannelTest2", visible=True,
                               color="Black", owner=remi, style="italic", description="blabla")

        print (" --->  SetUp of ChannelTestCase : OK !")
    """
		test all attributs when a channel have been save with the minimum of attributs
	"""

    def test_Channel_null_attribut(self):
        channel = Channel.objects.get(title="ChannelTest1")
        self.assertEqual(channel.visible, False)
        self.assertFalse(channel.slug == slugify("blabla"))
        self.assertEqual(channel.color, None)
        self.assertEqual(channel.description, '')
        self.assertEqual(channel.headband, None)
        self.assertEqual(channel.style, None)
        self.assertEqual(channel.owner, User.objects.get(username="Remi"))
        self.assertEqual(channel.__unicode__(), 'ChannelTest1')
        self.assertEqual(channel.video_count(), 0)
        self.assertEqual(channel.get_absolute_url(), "/" + channel.slug + "/")

        print (
            "   --->  test_Channel_null_attribut of ChannelTestCase : OK !")

    """
		test attributs when a channel have many attributs
	"""

    def test_Channel_with_attributs(self):
        channel = Channel.objects.get(title="ChannelTest2")
        self.assertEqual(channel.visible, True)
        channel.color = "Blue"
        self.assertEqual(channel.color, "Blue")
        self.assertEqual(channel.description, 'blabla')
        self.assertEqual(channel.headband, None)
        self.assertEqual(channel.style, "italic")
        self.assertEqual(channel.owner, User.objects.get(username="Remi"))
        self.assertEqual(channel.__unicode__(), 'ChannelTest2')
        self.assertEqual(channel.video_count(), 0)
        self.assertEqual(channel.get_absolute_url(), "/" + channel.slug + "/")

        print (
            "   --->  test_Channel_with_attributs of ChannelTestCase : OK !")

    """ 
        test delete object
    """

    def test_delete_object(self):
        Channel.objects.get(id=1).delete()
        Channel.objects.get(id=2).delete()
        self.assertEquals(Channel.objects.all().count(), 0)

        print (
            "   --->  test_delete_object of ChannelTestCase : OK !")

"""
	test the theme
"""


class ThemeTestCase(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        remi = User.objects.create_user("Remi")
        Channel.objects.create(title="ChannelTest1", owner=remi)
        Theme.objects.create(
            title="Theme1", slug="blabla", channel=Channel.objects.get(title="ChannelTest1"))

        print (" --->  SetUp of ThemeTestCase : OK !")

    """
		test all attributs when a theme have been save with the minimum of attributs
	"""

    def test_Theme_null_attribut(self):
        theme = Theme.objects.get(title="Theme1")
        self.assertFalse(theme.slug == slugify("blabla"))
        self.assertEqual(theme.headband, None)
        self.assertEqual(theme.__unicode__(), "ChannelTest1: Theme1")
        self.assertEqual(theme.video_count(), 0)
        self.assertEqual(theme.description, None)
        self.assertEqual(
            theme.get_absolute_url(), "/" + theme.channel.slug + "/" + theme.slug + "/")

        print (
            "   --->  test_Theme_null_attribut of ThemeTestCase : OK !")
    """
		test attributs when a theme have many attributs
	"""

    def test_Theme_with_attributs(self):
        theme = Theme.objects.get(title="Theme1")
        theme.description = "blabla"
        self.assertEqual(theme.description, 'blabla')

        print (
            "   --->  test_Theme_with_attributs of ThemeTestCase : OK !")

    """
        test delete object
    """

    def test_delete_object(self):
        Theme.objects.get(id=1).delete()
        self.assertEquals(Theme.objects.all().count(), 0)

        print (
            "   --->  test_delete_object of ThemeTestCase : OK !")

"""
	test the type
"""


class TypeTestCase(TestCase):

    def setUp(self):
        Type.objects.create(title="Type1", slug="blabla")

        print (" --->  SetUp of TypeTestCase : OK !")

    """
		test all attributs when a type have been save with the minimum of attributs
	"""

    def test_Type_null_attribut(self):
        type1 = Type.objects.get(title="Type1")
        self.assertFalse(type1.slug == slugify("blabla"))
        self.assertEqual(type1.headband, None)
        self.assertEqual(type1.__unicode__(), "Type1")
        self.assertEqual(type1.video_count(), 0)
        self.assertEqual(type1.description, None)

        print (
            "   --->  test_Type_null_attribut of TypeTestCase : OK !")

    """
		test attributs when a type have many attributs
	"""

    def test_Type_with_attributs(self):
        type1 = Type.objects.get(title="Type1")
        type1.description = "blabla"
        self.assertEqual(type1.description, 'blabla')

        print (
            "   --->  test_Type_with_attributs of TypeTestCase : OK !")

    """
        test delete object
    """

    def test_delete_object(self):
        Type.objects.get(id=1).delete()
        self.assertEquals(Type.objects.all().count(), 0)

        print (
            "   --->  test_delete_object of TypeTestCase : OK !")


"""
	test the discipline
"""


class DisciplineTestCase(TestCase):

    def setUp(self):
        Discipline.objects.create(title="Discipline1", slug="blabla")

        print (" --->  SetUp of DisciplineTestCase : OK !")

    """
		test all attributs when a discipline have been save with the minimum of attributs
	"""

    def test_Discipline_null_attribut(self):
        discipline = Discipline.objects.get(title="Discipline1")
        self.assertFalse(discipline.slug == slugify("blabla"))
        self.assertEqual(discipline.headband, None)
        self.assertEqual(discipline.__unicode__(), "Discipline1")
        self.assertEqual(discipline.video_count(), 0)
        self.assertEqual(discipline.description, None)

        print (
            "   --->  test_Discipline_null_attribut of DisciplineTestCase : OK !")

    """
		test attributs when a discipline have many attributs
	"""

    def test_Discipline_with_attributs(self):
        discipline = Discipline.objects.get(title="Discipline1")
        discipline.description = "blabla"
        self.assertEqual(discipline.description, 'blabla')

        print (
            "   --->  test_Discipline_with_attributs of DisciplineTestCase : OK !")

    """
        test delete object
    """

    def test_delete_object(self):
        Discipline.objects.get(id=1).delete()
        self.assertEquals(Discipline.objects.all().count(), 0)

        print (
            "   --->  test_delete_object of DisciplineTestCase : OK !")


"""
	test the NextAutoIncrement
"""


class NextAutoIncrementTestCase(TestCase):

    def setUp(self):
        discipline = Discipline.objects.create(title="Discipline1")

        print (" --->  SetUp of NextAutoIncrementTestCase : OK !")

    """
		Verifie if the id is incremented
	"""

    def testAutoIncrementId(self):
        if('mysql' in settings.DATABASES['default']['ENGINE']):
            self.assertEqual(get_nextautoincrement(
                Discipline), Discipline.objects.get(title="Discipline1").id + 1)
        else:
            self.assertEqual(Discipline.objects.latest(
                'id').id + 1, Discipline.objects.get(title="Discipline1").id + 1)

            print (
                "   --->  testAutoIncrementId of NextAutoIncrementTestCase : OK !")

"""
	test the objet pod and Video
"""


class VideoTestCase(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        remi = User.objects.create_user("Remi")
        other_type = Type.objects.get(id=1)
        url = "http://pod.univ-lille1.fr/media/"
        # url = "http://fms.univ-lille1.fr/vod/videos/media/videos/ncan/730/video_730_240.mp4"
        http = urllib3.PoolManager()
        tempfile = NamedTemporaryFile(delete=True)
        with http.request('GET', url, preload_content=False) as r, open(tempfile.name, 'wb') as out_file:
            shutil.copyfileobj(r, out_file)
        pod = Pod.objects.create(
            type=other_type, title="Video1", owner=remi, video="", to_encode=False)
        Pod.objects.create(type=other_type, title="Video2", encoding_status="b", encoding_in_progress=True,
                           date_added=datetime.today(), owner=remi, date_evt=datetime.today(), video="/media/videos/remi/test.mp4", allow_downloading=True, view_count=2, description="fl",
                           overview="blabla.jpg", is_draft=False, duration=3, infoVideo="videotest", to_encode=False)
        print (" --->  SetUp of VideoTestCase : OK !")

    """
		test all attributs when a video have been save with the minimum of attributs
	"""

    def test_Video_null_attributs(self):
        pod = Pod.objects.get(id=1)
        self.assertEqual(pod.video.name, "")
        self.assertEqual(pod.allow_downloading, False)
        self.assertEqual(pod.description, '')
        self.assertFalse(pod.slug == slugify("tralala"))
        date = datetime.today()
        self.assertEqual(pod.owner, User.objects.get(username="Remi"))
        self.assertEqual(pod.date_added.year, date.year)
        self.assertEqual(pod.date_added.month, date.month)
        self.assertEqual(pod.date_added.day, date.day)
        self.assertEqual(pod.date_evt, pod.date_added)
        self.assertEqual(pod.view_count, 0)
        self.assertEqual(pod.is_draft, True)
        self.assertEqual(pod.to_encode, False)
        self.assertEqual(pod.encoding_status, None)
        self.assertEqual(pod.encoding_in_progress, False)
        self.assertEqual(pod.thumbnail, None)
        self.assertTrue(pod.to_encode == False)
        self.assertEqual(pod.duration, 0)
        self.assertEqual(pod.infoVideo, None)
        self.assertEqual(pod.get_absolute_url(), "/video/" + pod.slug + "/")
        self.assertEqual(pod.__unicode__(), "%s - %s" %
                         ('%04d' % pod.id, pod.title))  # pb unicode appel str

        print (
            "   --->  test_Video_null_attributs of VideoTestCase : OK !")

    """
		test attributs when a video have many attributs
	"""

    def test_Video_many_attributs(self):
        pod = Pod.objects.get(id=2)
        self.assertEqual(pod.video.name, u'/media/videos/remi/test.mp4')
        self.assertEqual(pod.allow_downloading, True)
        self.assertEqual(pod.description, 'fl')
        self.assertEqual(pod.overview.name, "blabla.jpg")
        self.assertEqual(pod.view_count, 2)
        self.assertEqual(pod.allow_downloading, True)
        self.assertEqual(pod.encoding_status, 'b')
        self.assertEqual(pod.to_encode, False)
        self.assertEqual(pod.is_draft, False)
        self.assertEqual(pod.encoding_in_progress, True)
        self.assertEqual(pod.duration, 3)
        self.assertEqual(pod.infoVideo, "videotest")
        self.assertEqual(pod.video.__unicode__(), pod.video.name)

        print (
            "   --->  test_Video_many_attributs of VideoTestCase : OK !")

    """
		test the function admin thumbnail
	"""

    def test_admin_thumbnail(self):
        video1 = Pod.objects.get(id=1)
        video2 = Pod.objects.get(id=2)
        self.assertEqual(video1.admin_thumbnail(), "")
        self.assertEqual(video2.admin_thumbnail(), "")  # test dans la vue

        print (
            "   --->  test_admin_thumbnail of VideoTestCase : OK !")

    """
		test the filename function
	"""

    def test_filename(self):
        video1 = Pod.objects.get(id=1)
        video2 = Pod.objects.get(id=2)
        self.assertEqual(video1.filename(), "")
        self.assertEqual(video2.filename(), u'test.mp4')

        print (
            "   --->  test_filename of VideoTestCase : OK !")

    """
		test the fucntion duration_in_time
	"""

    def test_duration_in_time(self):
        video1 = Pod.objects.get(id=1)
        video2 = Pod.objects.get(id=2)
        self.assertEqual(video1.duration_in_time(), "00:00:00")
        self.assertEqual(video2.duration_in_time(), "00:00:03")

        print (
            "   --->  test_duration_in_time of VideoTestCase : OK !")

    """
        test delete object
    """

    def test_delete_object(self):
        Pod.objects.get(id=1).delete()
        Pod.objects.get(id=2).delete()
        self.assertEquals(Pod.objects.all().count(), 0)

        print (
            "   --->  test_delete_object of VideoTestCase : OK !")

"""
	test the favorites object
"""


class FavoritesTestCase(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        remi = User.objects.create_user("Remi")
        other_type = Type.objects.get(id=1)
        pod = Pod.objects.create(
            type=other_type,  title="Video1", slug="tralala", owner=remi)
        Favorites.objects.create(user=remi, video=pod)

        print (" --->  SetUp of FavoritesTestCase : OK !")

    """
		test attributs and str function
	"""

    def test_attributs_and_str(self):
        favorite = Favorites.objects.get(id=1)
        self.assertEqual(favorite.user.username, "Remi")
        self.assertEqual(favorite.video.id, 1)
        self.assertEqual(favorite.__unicode__(), "%s-%s" %
                         (favorite.user.username, favorite.video))

        print (
            "   --->  test_attributs_and_str of FavoritesTestCase : OK !")
    """
        test delete object
    """

    def test_delete_object(self):
        Favorites.objects.get(id=1).delete()
        self.assertEquals(Favorites.objects.all().count(), 0)

        print (
            "   --->  test_delete_object of FavoritesTestCase : OK !")


"""
	test the objet Notes
"""


class NotesTestCase(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        remi = User.objects.create_user("Remi")
        other_type = Type.objects.get(id=1)
        pod = Pod.objects.create(
            type=other_type,  title="Video1", slug="tralala", owner=remi)
        pod2 = Pod.objects.create(
            type=other_type,  title="Video2", slug="tralala", owner=remi)
        Notes.objects.create(user=remi, video=pod, note="tata")
        Notes.objects.create(user=remi, video=pod2)

        print (" --->  SetUp of NotesTestCase : OK !")

    """
		test attributs and str function
	"""

    def test_attributs_and_str(self):
        note = Notes.objects.get(id=1)
        note2 = Notes.objects.get(id=2)
        self.assertEqual(note.user.username, "Remi")
        self.assertEqual(note.video.id, 1)
        self.assertEqual(note.note, "tata")
        self.assertEqual(note2.note, None)
        self.assertEqual(note.__unicode__(), "%s-%s" %
                         (note.user.username, note.video))

        print (
            "   --->  test_attributs_and_str of NotesTestCase : OK !")

    """
        test delete object
    """

    def test_delete_object(self):
        Notes.objects.get(id=1).delete()
        Notes.objects.get(id=2).delete()
        self.assertEquals(Notes.objects.all().count(), 0)

        print (
            "   --->  test_delete_object of NotesTestCase : OK !")

"""
	test the MediaCourses
"""


class MediaCoursesTestCase(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        remi = User.objects.create_user("Remi")
        remi2 = User.objects.create_user("Remi2")
        Mediacourses.objects.create(user=remi, title="media1", date_added=datetime.today(
        ), mediapath="blabla", started=True, error="error1")
        #Mediacourses.objects.get_or_create(user=remi2, title="media2")
        Mediacourses.objects.create(user=remi2, title="media2", started=True)
        print (" --->  SetUp of MediaCoursesTestCase : OK !")

    """
		test attributs
	"""

    def test_attributs(self):
        media = Mediacourses.objects.get(id=1)
        media2 = Mediacourses.objects.get(id=2)
        # test media
        self.assertEqual(media.user.username, "Remi")
        self.assertEqual(media.title, "media1")
        date = datetime.today()
        self.assertEqual(media.date_added.year, date.year)
        self.assertEqual(media.date_added.month, date.month)
        self.assertEqual(media.date_added.day, date.day)
        self.assertEqual(media.mediapath, "blabla")
        self.assertEqual(media.started, True)
        self.assertEqual(media.error, "error1")
        # test media2
        self.assertEqual(media2.date_added.strftime(
            "%d/%m/%y"), media.date_added.strftime("%d/%m/%y"))
        self.assertEqual(media2.title, "media2")
        self.assertEqual(media2.started, True)
        self.assertEqual(media2.error, None)

        print (
            "   --->  test_attributs of MediaCoursesTestCase : OK !")

    """
        test delete object
    """

    def test_delete_object(self):
        Mediacourses.objects.filter(title="media1").delete()
        self.assertEquals(Mediacourses.objects.all().count(), 1)

        print (
            "   --->  test_delete_object of MediaCoursesTestCase : OK !")


"""
	test building object
"""


class BuildingTestCase(TestCase):

    def setUp(self):
        building = Building.objects.create(name="bulding1")

        print (" --->  SetUp of BuildingTestCase : OK !")

    """
		test attributs
	"""

    def test_attributs(self):
        building = Building.objects.get(id=1)
        self.assertEqual(building.name, u"bulding1")

        print (
            "   --->  test_attributs of BuildingTestCase : OK !")

    """
        test delete object
    """

    def test_delete_object(self):
        Building.objects.get(id=1).delete()
        self.assertEquals(Building.objects.all().count(), 0)

        print (
            "   --->  test_delete_object of BuildingTestCase : OK !")

"""              
	test recorder object
"""


class RecoderTestCase(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        remi = User.objects.create_user("Remi")
        building = Building.objects.create(name="bulding1")
        image = Image.objects.create(owner=remi, original_filename="schema_bdd.jpg", file=File(
            open("schema_bdd.jpg"), "schema_bdd.jpg"))
        Recorder.objects.create(name="recorder1", image=image, adress_ip="201.10.20.10",
                                status=True, slide=False, gmapurl="b", is_restricted=True, building=building)

        print (" --->  SetUp of RecoderTestCase : OK !")

    """
		test attributs
	"""

    def test_attributs(self):
        record = Recorder.objects.get(id=1)
        self.assertEqual(record.name, "recorder1")
        self.assertEqual(record.image.original_filename, "schema_bdd.jpg")
        self.assertEqual(record.adress_ip, "201.10.20.10")
        self.assertEqual(record.status, True)
        self.assertEqual(record.slide, False)
        self.assertEqual(record.gmapurl, "b")
        self.assertEqual(record.is_restricted, True)
        self.assertEqual(record.building.id, 1)
        self.assertEqual(record.__unicode__(), "%s - %s" %
                         (record.name, record.adress_ip))
        self.assertEqual(record.ipunder(), "201_10_20_10")

        print (
            "   --->  test_attributs of RecoderTestCase : OK !")

    """
        test delete object
    """

    def test_delete_object(self):
        Recorder.objects.get(id=1).delete()
        self.assertEquals(Recorder.objects.all().count(), 0)

        print (
            "   --->  test_delete_object of RecoderTestCase : OK !")
