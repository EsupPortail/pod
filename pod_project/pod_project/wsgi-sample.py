"""
WSGI config for pod_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import sys
import site

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('~/.virtualenvs/django_pod/local/lib/python2.7/site-packages')

# Add the app's directory to the PYTHONPATH
sys.path.append('/usr/local/django_projects/pod/pod_project')
sys.path.append('/usr/local/django_projects/pod/pod_project/pod_project')

os.environ['DJANGO_SETTINGS_MODULE'] = 'pod_project.settings'

# Activate your virtual env
activate_env=os.path.expanduser("~/.virtualenvs/django_pod/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()


