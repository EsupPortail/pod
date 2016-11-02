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
from filer.models.imagemodels import Image
from django.core.files import File
from core.models import FileBrowse, get_storage_path, EncodingType, get_media_guard
from pods.models import Pod, Type, EncodingPods
from django.contrib.auth.models import User, Group
from django.test import TestCase, override_settings
from django.conf import settings
import os

# Create your tests here.

@override_settings(
    MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'media'),
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite',
        }
    },
    LANGUAGE_CODE = 'en'
    )
class FileBrowseTestCase(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        remi = User.objects.create(username="remi")
        image = Image.objects.create(owner=remi, original_filename="schema_bdd.jpg", file=File(
            open("schema_bdd.jpg"), "schema_bdd.jpg"))
        FileBrowse.objects.create(document=image)

    def test_attributs(self):
        fileBrowse = FileBrowse.objects.get(id=1)
        self.assertEquals(
            fileBrowse.document.original_filename, "schema_bdd.jpg")
        self.assertEquals(fileBrowse.document.owner.username,  "remi")
        self.assertEquals(fileBrowse.__str__(), "%s" % fileBrowse.document)
        del(fileBrowse)
        FileBrowse.objects.get(id=1).delete()
        self.assertEquals(FileBrowse.objects.all().count(), 0)


class TestStoragePath(TestCase):
    """ Test the storage path """
    fixtures = ['initial_data.json']

    def setUp(self):
        remi = User.objects.create(username="remi")
        other_type = Type.objects.get(id=1)
        self.path1 = "video1.mp4"
        self.path2 = "myfolder/video2.mp4"
        self.video1 = Pod.objects.create(
            type=other_type,  title="Video1", slug="tralala", owner=remi,
            video=self.path1)
        self.video2 = Pod.objects.create(
            type=other_type,  title="Video1", slug="tralala", owner=remi,
            video=self.path2)
        self.encodingpods1 = EncodingPods.objects.create(
            video=self.video1,
            encodingType=EncodingType.objects.first(),
            encodingFile="video_1_240.mp4"
        )
        self.encodingpods2 = EncodingPods.objects.create(
            video=self.video2,
            encodingType=EncodingType.objects.first(),
            encodingFile="video_2_240.mp4"
        )

    @override_settings(MEDIA_GUARD=False)
    def test_get_storage_path_video(self):
        storage_path_1 = get_storage_path(self.video1, self.path1)
        self.assertEquals(storage_path_1, "videos/remi/"+self.path1)
        storage_path_2 = get_storage_path(self.video2, self.path2)
        self.assertEquals(storage_path_2, "videos/remi/"+self.path2)

    @override_settings(MEDIA_GUARD=False)
    def test_get_storage_path_encodingpods(self):
        storage_path_1 = get_storage_path(self.encodingpods1,
                                          self.path1)
        self.assertEquals(storage_path_1, "videos/remi/"+self.path1)
        storage_path_2 = get_storage_path(self.encodingpods2,
                                          self.path2)
        self.assertEquals(storage_path_2, "videos/remi/"+self.path2)

    @override_settings(MEDIA_GUARD=False, MEDIA_GUARD_SALT="S3CR3T")
    def test_get_media_guard_disabled(self):
        media_guard_hash = get_media_guard("remi", self.video1.id)
        self.assertEqual(media_guard_hash, "")

    @override_settings(MEDIA_GUARD=True, MEDIA_GUARD_SALT="")
    def test_get_media_guard_empty(self):
        media_guard_hash = get_media_guard("remi", self.video1.id)
        self.assertEqual(media_guard_hash, "")

    @override_settings(MEDIA_GUARD=True, MEDIA_GUARD_SALT="S3CR3T")
    def test_get_media_guard(self):
        media_guard_hash = get_media_guard("remi", self.video1.id)
        self.assertEqual(media_guard_hash, "df880ec636fe3a9dd39a33609dc44635a7c19d7b7b46deba33c281cf2edf0ca5")

    @override_settings(MEDIA_GUARD=True, MEDIA_GUARD_SALT="S3CR3T")
    def test_get_storage_path_video_with_media_guard(self):
        storage_path_1 = get_storage_path(self.video1, self.path1)
        self.assertEquals(storage_path_1, "videos/remi/df880ec636fe3a9dd39a33609dc44635a7c19d7b7b46deba33c281cf2edf0ca5/"+self.path1)
        storage_path_2 = get_storage_path(self.video2, self.path2)
        self.assertEquals(storage_path_2, "videos/remi/a1b11067d34f07639d40f411bbf70c2a601a464799699fb1af370f7bf24cb79c/"+self.path2)

    @override_settings(MEDIA_GUARD=True, MEDIA_GUARD_SALT="S3CR3T")
    def test_get_storage_path_encodingpods_with_media_guard(self):
        storage_path_1 = get_storage_path(self.encodingpods1,
                                          self.path1)
        self.assertEquals(storage_path_1, "videos/remi/df880ec636fe3a9dd39a33609dc44635a7c19d7b7b46deba33c281cf2edf0ca5/"+self.path1)
        storage_path_2 = get_storage_path(self.encodingpods2,
                                          self.path2)
        self.assertEquals(storage_path_2, "videos/remi/a1b11067d34f07639d40f411bbf70c2a601a464799699fb1af370f7bf24cb79c/"+self.path2)
