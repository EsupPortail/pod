# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from pod_project.ISOLanguageCodes import ALL_LANG_CHOICES, PREF_LANG_CHOICES
from pod_project.cursusCodes import CURSUS_CODES
from pod_project.ckeditor import *

import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

ADMINS = (
    # ('Nom', 'adminmail@exemple.fr'),
)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'dp7u819^$3u5rdjv62o2(k0nlg5%lg5h+^s6qf2-i2e%gr4a2)'

# Condition d'utilisation du mode DEBUG - Attention à mettre à false lors
# d'une mise en production
DEBUG = True

TEMPLATE_DEBUG = DEBUG

# Mettre url de production
ALLOWED_HOSTS = ['pod.univ.fr']

# Liste des applications
# https://docs.djangoproject.com/en/1.7/topics/migrations/#upgrading-from-south
INSTALLED_APPS = (
    # put it in first !!
    # http://django-modeltranslation.readthedocs.org/en/latest/installation.html#configuration
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Pages statiques
    'django.contrib.sites',
    'django.contrib.flatpages',
    # Applications tierces
    'ckeditor',
    'filer',
    'easy_thumbnails',
    # https://bitbucket.org/cpcc/django-cas -> application modifiée pour ajout
    # gateway et double authentification
    'django_cas_gateway',
    'taggit',
    'taggit_templatetags',
    'jquery',
    'djangoformsetjs',
    'captcha',
    'bootstrap3',
    # Applications locales
    'pods',
    'core'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Pages statiques
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

ROOT_URLCONF = 'pod_project.urls'

WSGI_APPLICATION = 'pod_project.wsgi.application'

# Base de données
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite',
    }
}
"""
#Configuration MySql
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pod',
        'USER': 'test',
        'PASSWORD': 'test',
        'HOST': '',
        'PORT': '',
        'OPTIONS': {'init_command': 'SET storage_engine=INNODB;'}
    }
"""

# Internationalisation

LANGUAGE_CODE = 'fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = (
    ('fr', _('Français')),
    ('en', _('English'))
)
DEFAULT_LANGUAGE = 1

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

MODELTRANSLATION_DEFAULT_LANGUAGE = 'fr'
MODELTRANSLATION_FALLBACK_LANGUAGES = ('fr', 'en')

# Fichiers statiques (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
FILE_UPLOAD_TEMP_DIR = '/var/tmp'

# Fichiers dynamiques (contenu du site)
# Attention, il faut creer le repertoire media
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
CKEDITOR_UPLOAD_PATH = os.path.join(MEDIA_ROOT, 'uploads')

# Paramètres spécifiques au projet
EMAIL_HOST = 'smtp.univ.fr'
EMAIL_PORT = 25
DEFAULT_FROM_EMAIL = 'default.mail@univ.fr'

SITE_ID = 1

FILER_ENABLE_PERMISSIONS = True

#URL FOR ELASTICSEARCH ['host1', 'host2', ...]
ES_URL = ['http://127.0.0.1:9200/']

CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.math_challenge'
CAPTCHA_NOISE_FUNCTIONS = ('captcha.helpers.noise_null',) #('captcha.helpers.noise_arcs','captcha.helpers.noise_dots',)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'cache_host',
    }
}

# Login
LOGIN_URL = '/accounts/login/'
USE_CAS = False
if USE_CAS:
    MIDDLEWARE_CLASSES = list(MIDDLEWARE_CLASSES)
    MIDDLEWARE_CLASSES.append('django_cas_gateway.middleware.CASMiddleware')
    MIDDLEWARE_CLASSES = tuple(MIDDLEWARE_CLASSES)
CAS_SERVER_URL = 'https://cas.univ.fr/'
CAS_LOGOUT_COMPLETELY = True
CAS_RETRY_LOGIN = True
CAS_VERSION = '3'

# LDAP
USE_LDAP_TO_POPULATE_USER = True
AUTH_LDAP_SERVER_URI = 'ldap://ldap.univ.fr'
AUTH_LDAP_BIND_DN = ''
AUTH_LDAP_BIND_PASSWORD = ''
AUTH_LDAP_SCOPE = 'ONELEVEL'
# ('ldap', 'parameters')
AUTH_LDAP_USER_SEARCH = ('ou=people,dc=univ,dc=fr', "(uid=%(uid)s)")
AUTH_LDAP_UID_TEST = ""

AUTH_USER_ATTR_MAP = {
    'first_name': 'givenName',
    'last_name': 'sn',
    'email': 'mailLocalAddress',
    'affiliation': 'eduPersonPrimaryAffiliation'
}
AFFILIATION_STAFF = ('employee', 'faculty')
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'core.populatedCASbackend.PopulatedCASBackend'
)

# Constantes utilisées dans les templates
TITLE_SITE = 'Pod'
TITLE_ETB = 'Université'
DEFAULT_IMG = 'images/default.png'
FILTER_USER_MENU = ('[a-d]', '[e-h]', '[i-l]', '[m-p]', '[q-t]', '[u-z]')
TEMPLATE_THEME = 'LILLE1'

LOGO_SITE = 'images/logo_compact.png'
LOGO_COMPACT_SITE = 'images/logo_black_compact.png'
LOGO_ETB = 'images/lille1_top-01.png'
LOGO_PLAYER = 'images/logo_white_compact.png'
SERV_LOGO = 'images/semm.png'

HELP_MAIL = 'assistance@univ.fr'
WEBTV = '<a href="http://webtv.univ.fr" id="webtv" class="btn btn-info btn-sm">' \
    'WEBTV<span class="glyphicon glyphicon-link"></span>' \
    '</a>'


##
# Taille maxi fichier téléversable :
#
#   ce paramètre est une chaîne contenant un chiffre suivi d'une unité (Mo ou Go),
#   séparés par une espace.
#
#   ATTENTION : cette valeur doit être inférieure ou égale à celle définie
#               dans votre configuration Apache ou NGINX.
#
MAX_UPLOAD_FILE_SIZE = "1 Go"

##
# Nombre maxi de fichiers téléversables par utilisateur / jour :
#
#   - ce paramètre est un entier, la valeur 0 supprime toute limite ;
#   - ne s'applique pas aux super-utilisateurs.
#
#
MAX_DAILY_USER_UPLOADS = 0


##
# Activation du téléversement asynchrone des fichiers à encoder :
#
#   - ce paramètre est un entier ;
#   - activation = 1, désactivation = 0 ;
#   - permet d'obtenir la barre de progression de téléversement.
#
#
USE_XHR_FORM_UPLOAD = 1


# Paramètres des templates
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'core', 'theme', TEMPLATE_THEME, 'templates'),
    os.path.join(BASE_DIR, 'core', 'templates'),
    os.path.join(BASE_DIR, 'core', 'templates', 'flatpages'),
)
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    # Contexte locaux
    'core.context_processors.pages_menu',
    'core.context_processors.context_settings',
    'pods.context_processors.items_menu_header',
)

# Mettre à '' si non utilise
FMS_LIVE_URL = 'rtmp://fms.univ.fr'
FMS_ROOT_URL = 'http://root.univ.fr'

BOOTSTRAP3 = {
    'jquery_url': os.path.join(STATIC_URL, 'js/jquery.js'),
    'base_url': os.path.join(STATIC_URL, 'bootstrap/'),
    'css_url': None,
    'theme_url': os.path.join(STATIC_URL, 'css/pod.css'),
    'javascript_url': None,
    'horizontal_label_class': 'col-md-2',
    'horizontal_field_class': 'col-md-4'
}

# Nom du dossier contenant les templates personnalisés (header.html et footer.html)
# Mettre à None si vous n'avez pas l'intention d'utiliser ces fichiers
TEMPLATE_CUSTOM = 'custom'  # None

# Constantes utilisables depuis les templates
TEMPLATE_VISIBLE_SETTINGS = (
    'DEFAULT_IMG',
    'FILTER_USER_MENU',
    'FMS_LIVE_URL',
    'HELP_MAIL',
    'LOGO_COMPACT_SITE',
    'LOGO_ETB',
    'LOGO_PLAYER',
    'LOGO_SITE',
    'MAX_UPLOAD_FILE_SIZE',
    'MAX_DAILY_USER_UPLOADS',
    'SERV_LOGO',
    'TEMPLATE_CUSTOM',
    'TEMPLATE_THEME',
    'TITLE_ETB',
    'TITLE_SITE',
    'USE_XHR_FORM_UPLOAD',
    'WEBTV'
)

# Fichiers statiques du theme
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'core', 'theme', TEMPLATE_THEME, 'assets'),
)

# Paramètres session
SESSION_COOKIE_AGE = 14400
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Paramètres des vignettes
THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters'
)

# Paramètres vidéo
FFMPEG = '/usr/local/ffmpeg/ffmpeg'
FFPROBE = '/usr/local/ffmpeg/ffprobe'
VIDEO_EXT_ACCEPT = (
    '.3gp',
    '.avi',
    '.divx',
    '.flv',
    '.m2p',
    '.m4v',
    '.mkv',
    '.mov',
    '.mp4',
    '.mpeg',
    '.mpg',
    '.mts',
    '.wmv',
    '.mp3',
    '.ogg',
    '.wav',
    '.wma'
)
ENCODE_WEBM = True
ENCODE_WAV = True

# AUDIOVIDEOCOURS
SKIP_FIRST_IMAGE = True
# mot de passe pour les enregistreurs multicam system
RECORDER_SALT = "abcdefgh"
# optional settings for test:
# if set it's used to test download and encode video in test
#HTTP_PROXY = 'http://localhost:3128/'

# Signalement des vidéos
SHOW_REPORT = True
REPORT_VIDEO_MAIL_TO = ['alert@univ.fr']
