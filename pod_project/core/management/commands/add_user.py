# -*- coding: utf-8 -*-
"""
Ce programme est un logiciel libre : vous pouvez le redistribuer
et/ou le modifier sous les termes de la licence GNU Public Licence
telle que publiée par la Free Software Foundation, soit dans la version 3
de la licence, ou (selon votre choix) toute version ultérieure.
Ce programme est distribué avec l'espoir qu'il sera utile, mais SANS AUCUNE
GARANTIE : sans même les garanties implicites de VALEUR MARCHANDE ou
D'APPLICABILITÉ À UN BUT PRÉCIS. Voir la licence GNU General Public License
pour plus de détails. Vous devriez avoir reçu une copie de la licence
GNU General Public Licence avec ce programme. Si ce n'est pas le cas, voir
http://www.gnu.org/licenses/
"""
import commands
import csv
import os

from django.core.management.base import NoArgsCommand

import random
import string

from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from django.db import IntegrityError
from django.core.mail import send_mail
from random import choice
from string import digits, letters
from core.models import UserProfile
import time


class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        """ Encode all pending streams """
        members = open('import_user.csv', "r")
        data = csv.reader(members, delimiter=';', quotechar='"')
        # data = csv.DictReader(members)
        i = 0
        for row in data:
            i = i + 1
            if i % 10 == 0:
                print "----- i : %s" % i
                time.sleep(480)
            # print u'%s' %row
            prenom = unicode(row[0], "utf8")
            nom = unicode(row[1], "utf8")
            email = unicode(row[2], "utf8")
            is_staff = True if row[3] == "1" else False
            detail = unicode(row[4], "utf8")
            print nom, prenom, email, is_staff, detail
            try:
                validate_email(email)
                tokens = email.split('@')
                username = tokens[0]
                print "email valide : %s" % username
                add_user(nom, prenom, username, email, is_staff, detail)
            except ValidationError:
                print "%s %s => invalid email" % (nom, prenom)

        members.close()


def add_user(nom, prenom, username, email, is_staff, detail):
    pwd = ''.join([random.choice(string.digits + string.letters)
                   for i in range(10)])
    message = u'Bonjour %(name)s,\n\n\nun compte a été créé pour vous sur %(pod)s.\n\nVoici les informations de connexion :\n- nom d\'utilisateur : %(id)s\n- mot de passe : %(mdp)s\n\nÀ bientôt sur http://%(url)s/.\n\nP.S. : pour vous connecter utilisez le bouton « Connexion » en haut à droite, puis choisissez « Authentification locale ».' % {
        "name": prenom, "pod": settings.TITLE_SITE, "id": username, "mdp": pwd, "url": settings.ALLOWED_HOSTS[0]}
    try:
        user = User.objects.create_user(username, email, pwd)
        user.is_staff = is_staff
        user.first_name = prenom
        user.last_name = nom
        user.save()
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.commentaire = u'%s\n\n( %s / %s )' % (detail, username, pwd)
        profile.save()
        send_mail('Votre compte sur %s' % settings.TITLE_SITE, message,
                  settings.HELP_MAIL, [email], fail_silently=False)
        print "%s / %s => ok" % (username, pwd)
    except IntegrityError:
        print "IntegrityError %s" % username
