# -*- coding: utf-8 -*-

import commands
import csv
import os

from django.core.management.base import NoArgsCommand

import random
import string

from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError



from django.db import IntegrityError
from django.core.mail import send_mail
from random import choice
from string import digits, letters
from core.models import UserProfile

def _pw(length=6):
    s = ''
    for i in range(length):
        s += random.choice(digits + letters)
    return s

class Command(NoArgsCommand):
    
    
    def handle_noargs(self, **options):
        """ Encode all pending streams """
        members = open('import_user.csv', "rU")
        data = csv.reader(members, delimiter=';', quotechar='"')
        #data = csv.DictReader(members)
        
        for row in data:
            #print u'%s' %row
            nom = row[0]
            prenom = row[1]
            email = row[2]
            is_staff = True if row[3]=="1" else False
            detail=""
            try:
                detail = u'%s' %unicode(row[4], errors='ignore')
            except Exception as e:
                print u'\nError in adding info video ***** Unexpected error :%r' % e

            print nom, prenom, email, is_staff, detail
            try:
                validate_email(email)
                tokens = email.split('@')
                username = tokens[0]
                #print "email valide : %s" %username
                add_user(nom, prenom, username, email, is_staff, detail)
            except ValidationError:
                print "email is not valid" 

            
            
def add_user(nom, prenom, username, email, is_staff, detail):
    pwd = ''.join([random.choice(string.digits + string.letters) for i in range(0, 10)])
    message = u'Bonjour,\nUn compte a été créé pour vous sur PodMoot. Voici les informations de connexion : \n - Identifiant : %(id)s\n - Mot de passe : %(mdp)s\n A bientôt sur http://podmoot.univ-lille1.fr.\nCordialement, \n L\'équipe de Pod.' %{"id":username, "mdp":pwd}
    try:
        user = User.objects.create_user(username, email, pwd)
        user.is_staff = is_staff
        user.first_name = prenom
        user.last_name = nom
        user.save()
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.commentaire = u'%s \n- %s' %(detail,message)
        profile.save()
        #send email
        send_mail('Votre compte sur PodMoot', message, 'nicolas.can@univ-lille1.fr',[email], fail_silently=False)
        print "%s - %s => ok" %(username,pwd)
    except IntegrityError:
        print "IntegrityError %s" %username
    
            
