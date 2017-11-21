from django.core.management.base import NoArgsCommand
from django.conf import settings

import urllib2
import re

class Command(NoArgsCommand):
	help = 'Check the current version of Pod. Prevents if a newer version is available.'

	def handle_noargs(self, **options):
		response = urllib2.urlopen('https://github.com/EsupPortail/pod/releases/latest')
		version = re.search('[^/]+(?=/$|$)', response.geturl())
		if settings.VERSION != version.group():
			print "You don't have the latest version."
			print "Latest version : %s | Your version : %s" % (version.group(), settings.VERSION)
			print "Link to the new version : %s" % response.geturl()
		else:
			print "You have the latest version : %s" % version.group()
