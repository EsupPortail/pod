# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from pod_project.ISOLanguageCodes import ALL_LANG_CHOICES, PREF_LANG_CHOICES
from pod_project.cursusCodes import CURSUS_CODES
from pod_project.ckeditor import *

import os

##
# Local settings import
#
from settings_local import *


##
# Installed applications list
#
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
    'djangoformsetjs',
    'captcha',
    'bootstrap3',
    'rest_framework',
    'rest_framework.authtoken',
    # Applications locales
    'pods',
    'core',
    'h5pp',
)


##
# Activated middleware components
#
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


##
# Full Python import path to root URL file
#
ROOT_URLCONF = 'pod_project.urls'


##
# Full Python path of WSGI app object Django’s built-in servers (e.g. runserver) will use
#
WSGI_APPLICATION = 'pod_project.wsgi.application'


##
# Settings for all caches to be used with Django
#
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'cache_host',
    }
}


##
# WEBservices with rest API
#
# curl -X GET http://127.0.0.1:8000/api/example/ -H 'Authorization: Token
# 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b'
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAdminUser',
    )
}


##
# Internationalisation
#
USE_I18N = True
USE_L10N = True
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)


##
# Time zone support is enabled (True) or not (False)
#
USE_TZ = True


##
# URL where requests are redirected for login
#
LOGIN_URL = '/accounts/login/'


##
# Middleware addition if CAS is used
#
if USE_CAS:
    MIDDLEWARE_CLASSES = list(MIDDLEWARE_CLASSES)
    MIDDLEWARE_CLASSES.append('django_cas_gateway.middleware.CASMiddleware')
    MIDDLEWARE_CLASSES = tuple(MIDDLEWARE_CLASSES)


##
# Authentication backend classes to use when attempting to authenticate a user
#
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'core.populatedCASbackend.PopulatedCASBackend'
)


##
# Settings for all template engines to be used
#
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (
            os.path.join(BASE_DIR, 'core', 'theme',
                         TEMPLATE_THEME, 'templates'),
            os.path.join(BASE_DIR, 'core', 'templates'),
            os.path.join(BASE_DIR, 'core', 'templates', 'flatpages'),
        ),
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': (
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                # Local contexts
                'core.context_processors.pages_menu',
                'core.context_processors.context_settings',
                'pods.context_processors.items_menu_header',
            ),
            'debug': DEBUG,
        },
    },
]


##
# Additional static files locations (theme)
#
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'core', 'theme', TEMPLATE_THEME, 'assets'),
)


##
# Overwriting django-bootstrap3 default configuration settings
#
BOOTSTRAP3 = {
    'jquery_url': os.path.join(STATIC_URL, 'js/jquery.min.js'),
    'base_url': os.path.join(STATIC_URL, 'bootstrap/'),
    'css_url': None,
    'theme_url': os.path.join(STATIC_URL, 'css/pod.css'),
    'javascript_url': None,
    'horizontal_label_class': 'col-md-2',
    'horizontal_field_class': 'col-md-4'
}


##
# Django-filer config
#
FILER_ENABLE_PERMISSIONS = True


##
# Taggit config
#
TAGGIT_CASE_INSENSITIVE = True


##
# Easy-thumbnails config (Django-filer)
#
THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters'
)


##
# Captcha config
#
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.math_challenge'
# ('captcha.helpers.noise_arcs','captcha.helpers.noise_dots',)
CAPTCHA_NOISE_FUNCTIONS = ('captcha.helpers.noise_null',)


##
# Accepted video formats
#
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


##
# Settings exposed in templates
#
TEMPLATE_VISIBLE_SETTINGS = (
    'ALLOWED_HOSTS',
    'DC_COVERAGE',
    'DC_RIGHTS',
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
    'TEMPLATE_THEME',
    'TEMPLATE_USE_FOOTER',
    'TEMPLATE_USE_PRE_HEADER',
    'TITLE_ETB',
    'TITLE_SITE',
    'USE_XHR_FORM_UPLOAD',
    'WEBTV'
)
