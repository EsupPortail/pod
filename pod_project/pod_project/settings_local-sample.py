# -*- coding: utf-8 -*-

import os


##
# The secret key for your particular Django installation.
#
#   This is used to provide cryptographic signing,
#   and should be set to a unique, unpredictable value.
#
#   Django will not start if this is not set.
#   https://docs.djangoproject.com/en/1.8/ref/settings/#secret-key
#
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''


##
# DEBUG mode activation.
#
#   https://docs.djangoproject.com/en/1.8/ref/settings/#debug
#
# SECURITY WARNING: MUST be set to False when deploying into production.
DEBUG = True


##
# A list of strings representing the host/domain names
#   that this Django site is allowed to serve.
#
#   https://docs.djangoproject.com/en/1.8/ref/settings/#allowed-hosts
#
ALLOWED_HOSTS = ['pod.univ.fr']


##
# Session settings
#
#   https://docs.djangoproject.com/en/1.8/ref/settings/#session-cookie-age
#   https://docs.djangoproject.com/en/1.8/ref/settings/#session-expire-at-browser-close
#
SESSION_COOKIE_AGE = 14400
SESSION_EXPIRE_AT_BROWSER_CLOSE = True


##
# A tuple that lists people who get code error notifications
#   when DEBUG=False and a view raises an exception.
#
#   https://docs.djangoproject.com/en/1.8/ref/settings/#admins
#
ADMINS = (
    ('Name', 'adminmail@univ.fr'),
)


##
# A dictionary containing the settings for all databases
#   to be used with Django.
#
#   https://docs.djangoproject.com/en/1.8/ref/settings/#databases
#
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite',
    }
}
"""
# MySQL settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pod',
        'USER': 'test',
        'PASSWORD': 'test',
        'HOST': '',
        'PORT': '',
        'OPTIONS': {'init_command': 'SET storage_engine=INNODB;'}
    }
}
"""


##
# CAS settings (login)
#
USE_CAS = False
CAS_SERVER_URL = 'https://cas.univ.fr'
CAS_LOGOUT_COMPLETELY = True
CAS_RETRY_LOGIN = True
CAS_VERSION = '3'
USE_LDAP_TO_POPULATE_USER = True


##
# LDAP settings (used by CAS)
#
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


##
# Internationalization and localization.
#
#   https://docs.djangoproject.com/en/1.8/ref/settings/#globalization-i18n-l10n
#
LANGUAGE_CODE = 'fr'
LANGUAGES = (
    ('fr', 'Français'),
    ('en', 'English')
)
MODELTRANSLATION_DEFAULT_LANGUAGE = 'fr'
MODELTRANSLATION_FALLBACK_LANGUAGES = ('fr', 'en')


##
# A string representing the time zone for this installation.
#
#   https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
#
TIME_ZONE = 'Europe/Paris'


##
# Base folder
#
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
# BASE_DIR = os.path.join(os.path.sep, 'absolute_path_to', 'pod', 'pod_project')


##
# The directory to temporarily store data while uploading files.
#
#   If None, the standard temporary directory for the operating system
#   will be used.
#
#   https://docs.djangoproject.com/en/1.8/ref/settings/#file-upload-temp-dir
#
FILE_UPLOAD_TEMP_DIR = os.path.join(os.path.sep, 'var', 'tmp')


##
# Static files (assets: CSS, JavaScript, fonts...)
#
#   https://docs.djangoproject.com/en/1.8/ref/settings/#static-url
#   https://docs.djangoproject.com/en/1.8/ref/settings/#static-root
#
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')


##
# Dynamic files (user managed content: videos, subtitles, documents etc...)
#
#   https://docs.djangoproject.com/en/1.8/ref/settings/#media-url
#   https://docs.djangoproject.com/en/1.8/ref/settings/#media-root
#
# WARNING: this folder must have previously been created.
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


##
# CKEditor media upload folder
#
#   https://github.com/django-ckeditor/django-ckeditor#id3
#
# WARNING: this folder must have previously been created.
CKEDITOR_UPLOAD_PATH = os.path.join(MEDIA_ROOT, 'uploads')


##
# eMail settings
#
#   https://docs.djangoproject.com/en/1.8/ref/settings/#email-host
#   https://docs.djangoproject.com/en/1.8/ref/settings/#email-port
#   https://docs.djangoproject.com/en/1.8/ref/settings/#default-from-email
#
EMAIL_HOST = 'smtp.univ.fr'
EMAIL_PORT = 25
DEFAULT_FROM_EMAIL = 'noreply@univ.fr'


##
# Current site ID in the django_site database table.
#
#   Used by flat pages.
#
#   https://docs.djangoproject.com/en/1.8/ref/settings/#site-id
#
SITE_ID = 1


##
# List of Elasticsearch urls, like ['host1', 'host2', ...].
#
#   http://elasticutils.readthedocs.io/en/latest/django.html#django.conf.settings.ES_URLS
#
ES_URL = ['http://127.0.0.1:9200/']


##
# Template settings
#
TEMPLATE_THEME = 'DEFAULT'
TITLE_SITE = 'Pod'
TITLE_ETB = 'University name'
LOGO_SITE = 'images/logo_compact.png'
LOGO_COMPACT_SITE = 'images/logo_black_compact.png'
LOGO_ETB = 'images/lille1_top-01.png'
LOGO_PLAYER = 'images/logo_white_compact.png'
SERV_LOGO = 'images/semm.png'
DEFAULT_IMG = 'images/default.png'
FILTER_USER_MENU = ('[a-d]', '[e-h]', '[i-l]', '[m-p]', '[q-t]', '[u-z]')
WEBTV = '<a href="http://webtv.univ.fr" id="webtv" class="btn btn-info btn-sm">' \
    'WEBTV<span class="glyphicon glyphicon-link"></span>' \
    '</a>'


##
# Main template elements:
#
#   the « templates » folder of the theme in use, allowing template
#   overloading, also contains the « pre-header » and « footer »
#   main template elements.
#
#   True: insert the (modified) file to main template,
#   False: do not use the file (i.e. no pre-header / no footer).
#
#   Setting both to « True » has the same effect than previous
#   « TEMPLATE_CUSTOM = 'custom' » setting.
#
TEMPLATE_USE_PRE_HEADER = True
TEMPLATE_USE_FOOTER = True


##
# eMail address where contact form sends user messages.
#
HELP_MAIL = 'support@univ.fr'


##
# WebM video encoding activation:
#
#   True: video files will be available in both mp4 and WebM formats,
#   False: video files will only be available in mp4 format.
#
ENCODE_WEBM = True


##
# WAV audio encoding activation:
#
#   True: audio files will be available in both mp3 and WAV formats,
#   False: audio files will only be available in mp3 format.
#
ENCODE_WAV = True


##
# Dublin Core application-wide tags:
#
#   coverage    name, town and country of the institution
#   rights      CC license for public contents
#
DC_COVERAGE = TITLE_ETB + " - Town - Country"
DC_RIGHTS = "CC-By-ND-NC"


##
# Maximum size of uploaded files:
#
#   a string containing a number followed by an unit (Mo ou Go),
#   separated by a space.
#
# WARNING: this value must be lower or equal to the corresponding one
#          defined in your Apache / NGINX config.
#
MAX_UPLOAD_FILE_SIZE = "1 Go"


##
# Maximum number of files uploadable by a user per day:
#
#   - an integer, the 0 value means no limits;
#   - does not apply to superusers.
#
MAX_DAILY_USER_UPLOADS = 0


##
# Asynchronous file upload activation:
#
#   - an integer (activation 1, deactivation 0),
#   - gives upload progression bar when activated.
#
USE_XHR_FORM_UPLOAD = 1


##
# Enable channel owners to set channel visibility:
#
#   - an integer (activation 1, deactivation 0),
#   - when activated, the « Visible » checkbox appears in
#     channel edition form.
#
ALLOW_VISIBILITY_SETTING_TO_CHANNEL_OWNERS = 1


##
# Content reporting:
#
#   shows a button with a « flag » picto near the video title
#   when viewing a video. If active, a popup allowing the user
#   to send an email to report the content is displayed when
#   the button is clicked.
#
SHOW_REPORT = True
REPORT_VIDEO_MAIL_TO = ['alert@univ.fr']


##
# Media protection:
#
#   if activated, inserts a folder in the storage file system
#   between the username one and the videoID one. The name of
#   this folder is a hash built with the MEDIA_GUARD_SALT value.
#
# WARNING: you MUST redefine MEDIA_GUARD_SALT to use this feature.
MEDIA_GUARD = False
MEDIA_GUARD_SALT = 'a.string.used.as.salt'


##
# Encoding tools path:
#
#   for better app response while encoding, you can affect a
#   lower « nice » level to the task, like this:
#
# FFMPEG = 'nice -19 /usr/local/ffmpeg/ffmpeg'
# FFPROBE = 'nice -19 /usr/local/ffmpeg/ffprobe'
FFMPEG = '/usr/local/ffmpeg/ffmpeg'
FFPROBE = '/usr/local/ffmpeg/ffprobe'


##
# Encoding tools default parameters overriding:
#
# ENCODE_VIDEO_CMD = "%(ffprobe)s -v quiet -show_format -show_streams -print_format json -i %(src)s"
# ADD_THUMBNAILS_CMD = "%(ffmpeg)s -i \"%(src)s\" -vf fps=\"fps=1/%(thumbnail)s,scale=%(scale)s\" -an -vsync 0 -threads 0 -f image2 -y %(out)s_%(num)s.png"
# ADD_OVERVIEW_CMD = "%(ffmpeg)s -i \"%(src)s\" -vf \"thumbnail=%(thumbnail)s,scale=%(scale)s,tile=100x1:nb_frames=100:padding=0:margin=0\" -an -vsync 0 -threads 0 -y %(out)s"
# ENCODE_MP4_CMD = "%(ffmpeg)s -i %(src)s -codec:v libx264 -profile:v high -pix_fmt yuv420p -preset faster -b:v %(bv)s -maxrate %(bv)s -bufsize %(bufsize)s -vf scale=%(scale)s -force_key_frames \"expr:gte(t,n_forced*1)\" -deinterlace -threads 0 -codec:a aac -strict -2 -ar %(ar)s -ac 2 -b:a %(ba)s -movflags faststart -y %(out)s"
# ENCODE_WEBM_CMD = "%(ffmpeg)s -i %(src)s -codec:v libvpx -quality realtime -cpu-used 3 -b:v %(bv)s -maxrate %(bv)s -bufsize %(bufsize)s -qmin 10 -qmax 42 -threads 4 -codec:a libvorbis -y %(out)s"
# ENCODE_MP3_CMD = "%(ffmpeg)s -i %(src)s -vn -ar %(ar)s -ab %(ab)s -f mp3 -threads 0 -y %(out)s"
# ENCODE_WAV_CMD = "%(ffmpeg)s -i %(src)s -ar %(ar)s -ab %(ab)s -f wav -threads 0 -y %(out)s"


##
# Streaming, live diffusion:
#
#   set to '' if not used.
#
FMS_LIVE_URL = 'rtmp://fms.univ.fr'
FMS_ROOT_URL = 'http://root.univ.fr'


##
# AudioVideoCast
#
SKIP_FIRST_IMAGE = True
# Multicam System recorders password
RECORDER_SALT = 'a.string.used.as.salt'
# Optional settings for test:
#   if set it's used for download and encoding test
# HTTP_PROXY = 'http://localhost:3128/'
