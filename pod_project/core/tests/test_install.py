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
from django.test import Client
from django.test.client import RequestFactory
import ldap
import urllib3
import shutil
from django.core.files.temp import NamedTemporaryFile
from core.utils import encode_video

class CasTestView(TestCase):

	def setUp(self):
		print "CasTestView"

	def test_cas(self):
		if settings.USE_CAS == True:
			cas_url = settings.CAS_SERVER_URL
			print "cas_url : %s " % cas_url
			http = urllib3.PoolManager()
			r = http.request('GET', cas_url)
			self.assertEqual(r.status, 200)
			print "TEST CAS OK"
		else:
			print "not cas server used USE_CAS is set to False"

"""
class LdapTestView(TestCase):

	def setUp(self):
		print "LdapTestView"

	def test_cas(self):
		if settings.USE_LDAP_TO_POPULATE_USER and settings.AUTH_LDAP_UID_TEST != "":
			try :
				l = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
				l.protocol_version = ldap.VERSION3
				if settings.AUTH_LDAP_BIND_DN != '':
					l.simple_bind_s(
					    settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
				ldap_scope = {
				    'ONELEVEL': ldap.SCOPE_ONELEVEL, 'SUBTREE': ldap.SCOPE_SUBTREE}

				list_value = []
				for val in settings.AUTH_USER_ATTR_MAP.values():
					list_value.append(str(val))
				try:
					r = l.search_s(settings.AUTH_LDAP_USER_SEARCH[0], ldap_scope[
					               settings.AUTH_LDAP_SCOPE], settings.AUTH_LDAP_USER_SEARCH[1] % {"uid": settings.AUTH_LDAP_UID_TEST}, list_value)
					(dn, attrs) = r[0]  # une seule entree par uid
					if settings.AUTH_USER_ATTR_MAP.get('first_name') and attrs.get(settings.AUTH_USER_ATTR_MAP['first_name']):
						# get first value
						print "First name : %s" % attrs[settings.AUTH_USER_ATTR_MAP['first_name']][0]
					if settings.AUTH_USER_ATTR_MAP.get('last_name') and attrs.get(settings.AUTH_USER_ATTR_MAP['last_name']):
					    # get first value
					    print "Last name : %s" % attrs[settings.AUTH_USER_ATTR_MAP['last_name']][0]
					if settings.AUTH_USER_ATTR_MAP.get('email') and attrs.get(settings.AUTH_USER_ATTR_MAP['email']):
					    # get first value
					    print "email : %s" % attrs[settings.AUTH_USER_ATTR_MAP['email']][0]

					if settings.AUTH_USER_ATTR_MAP.get('affiliation') and attrs.get(settings.AUTH_USER_ATTR_MAP['affiliation']):
						try:
							# get first value
							print "Affiliation : %s" % attrs[settings.AUTH_USER_ATTR_MAP['affiliation']][0]
							if user.userprofile.affiliation in settings.AFFILIATION_STAFF:
								print "is staff : True"
							else :
								print "is staff : False"
						except:
							print u'\n*****Unexpected error link :%s - %s' %(sys.exc_info()[0], sys.exc_info()[1])
				except:
					print u'\n*****Unexpected error link :%s - %s' %(sys.exc_info()[0], sys.exc_info()[1])
			except ldap.LDAPError, e:
				print e
		else:
			print "not ldap server used USE_LDAP_TO_POPULATE_USER is set to False or settings.AUTH_LDAP_UID_TEST is none"
"""
class EsTestView(TestCase):
	def setUp(self):
		print "EsTestView"

	def test_es(self):
		es_url = settings.HAYSTACK_CONNECTIONS['default']['URL']
		print "es_url : %s " % es_url
		http = urllib3.PoolManager()
		r = http.request('GET', es_url)
		self.assertEqual(r.status, 200)
		print "TEST ElasticSearch OK : %s" %r.data
		


class EncodingFileTestView(TestCase):
	fixtures = ['initial_data.json',]
	def setUp(self):
		print "EncodingFileTestView"
		#group = Group.objects.create(name='can delete file')
		remi = User.objects.create(username="remi")
		type1 = Type.objects.create(title="Type1")
		
		url = "http://pod.univ-lille1.fr/media/pod.m2p"
		#url = "http://fms.univ-lille1.fr/vod/videos/media/videos/ncan/730/video_730_240.mp4"
		http = urllib3.PoolManager()
		#r = http.request('GET', url)
		tempfile = NamedTemporaryFile(delete=True)
		print " - "
		print tempfile.name
		print " - "
		#print r.getheader("transfer-encoding")
		with http.request('GET', url, preload_content=False) as r, open(tempfile.name, 'wb') as out_file:       
			shutil.copyfileobj(r, out_file)
		pod = Pod.objects.create(type=type1, title="Video", owner=remi, video="-", to_encode=False)
		pod.video.save("pod-test.m2p", File(tempfile))

	def test_encoding(self):
		remi = User.objects.get(username="remi")
		type1 = Type.objects.get(title="Type1")
		pod = Pod.objects.get(id=1)
		print "\n %s" %pod.video
		print "\n ---> lancement Encodage"
		encode_video(pod)
		#self.assertEquals(out.getvalue(), 'Successfully encode video "1"\n')
		print "\n ---> Fin Encodage"
		

