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
from django.contrib.auth import authenticate


# Create your tests here.


class User_ProfileTestView(TestCase):

    def setUp(self):
        user = User.objects.create(
            username='remi', password='12345', is_active=True)
        user.set_password('hello')
        user.save()

    def test_Profile(self):
        user = User.objects.get(id=1)
        user = authenticate(username='remi', password='hello')
        login = self.client.login(username='remi', password='hello')
        self.assertEqual(login, True)
        response = self.client.get("/user/")
        self.assertEqual(response.status_code, 200)
        response = self.client.post("/user/", {u'url': [u'https://docs.djangoproject.com/fr/1.6/topics/testing/tools/'],
                                               u'csrfmiddlewaretoken': [u'9fTMPin73XA1qRUtYMpT0lx3rB0i3uPq'], u'description': [u'ghd']})
        self.assertEqual(response.status_code, 200)
