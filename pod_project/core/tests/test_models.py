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
from core.models import FileBrowse
from pods.models import User
from django.test import TestCase

# Create your tests here.


class FileBrowseTestCase(TestCase):

    def setUp(self):
        #todo : add can delete file group
        remi = User.objects.create_user("Remi")
        image = Image.objects.create(owner=remi, original_filename="schema_bdd.jpg", file=File(
            open("schema_bdd.jpg"), "schema_bdd.jpg"))
        FileBrowse.objects.create(document=image)

    def test_attributs(self):
        fileBrowse = FileBrowse.objects.get(id=1)
        self.assertEquals(
            fileBrowse.document.original_filename, "schema_bdd.jpg")
        self.assertEquals(fileBrowse.document.owner.username,  "Remi")
        self.assertEquals(fileBrowse.__str__(), "%s" % fileBrowse.document)
        del(fileBrowse)
        FileBrowse.objects.get(id=1).delete()
        self.assertEquals(FileBrowse.objects.all().count(), 0)
