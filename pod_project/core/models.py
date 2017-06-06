# -*- coding: utf-8 -*-
"""
Copyright (C) 2014 Nicolas Can
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

from __future__ import unicode_literals

from django.db import models
from filer.fields.file import FilerFileField
from filer.fields.image import FilerImageField
from django.utils.translation import get_language, ugettext_lazy as _
from django.utils.encoding import iri_to_uri, python_2_unicode_compatible
from django.contrib.auth.models import User, Group

from django.dispatch import receiver
from django.db.models.signals import post_save

from django.contrib.sites.models import Site
from django.core.urlresolvers import get_script_prefix

from datetime import datetime
from django.conf import settings
from ckeditor.fields import RichTextField
from django.template.defaultfilters import slugify

from django.contrib.flatpages.models import FlatPage

import sys
import os
import time
import traceback
import hashlib
from filer.models import Folder

import logging
logger = logging.getLogger(__name__)

VIDEOS_DIR = getattr(settings, 'VIDEOS_DIR', 'videos')
MAIN_LANG_CHOICES = (
    ("", settings.PREF_LANG_CHOICES), ("-----------", settings.ALL_LANG_CHOICES))


@python_2_unicode_compatible
class FileBrowse(models.Model):
    document = FilerFileField(
        null=True, blank=True, verbose_name=u'Fichier selectionné')

    def __str__(self):
        return "%s" % self.document


@python_2_unicode_compatible
class PagesMenuBas(models.Model):
    page = models.ForeignKey(FlatPage)
    order = models.PositiveSmallIntegerField(
        _('order'), default=1, blank=True, null=True)

    class Meta:
        ordering = ['order', 'page__title']
        verbose_name = _('page bottom menu')
        verbose_name_plural = _('pages bottom menu')
        #app_label = 'Menus'
        #db_table = 'core_pagesmenubas'

    def __unicode__(self):
        return self.page.title

    def __str__(self):
        return "%s" % (self.page.title)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    image = FilerImageField(null=True, blank=True, verbose_name=_('Avatar'),
                            help_text=_('This field allows you to add a photo ID. The picture will be displayed with your videos.'))
    description = models.TextField(_('Description'), max_length=100, blank=True,
                                   help_text=_('This field allows you to write a few words about yourself. The text will be displayed with your videos.'))
    url = models.URLField(_('Web link'), blank=True,
                          help_text=_('This field allows you to add an url.'))

    auth_type = models.CharField(max_length=20, default="loc.")
    affiliation = models.CharField(max_length=50, default="member")
    commentaire = models.TextField(_('Comment'), blank=True, default="")

    def __str__(self):
        return "%s" % (self.user)

    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')
        ordering = ('user',)

    def is_manager(self):
        return self.user.groups.filter(name='Manager')
    # def get_absolute_url(self):
    #    return reverse('core.views.user')


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # creation du profil
        try:
            UserProfile.objects.create(user=instance)
        except Exception as e:
            msg = u'\n Create user profile ***** Error:%r' % e
            msg += '\n%s' % traceback.format_exc()
            logger.error(msg)
            print msg
        # creation du repertoire pour ses documents
        try:
            Folder.objects.create(owner=instance, name=instance.username)
            if not instance.groups.filter(name='can delete file').exists():
                g = Group.objects.get(name='can delete file')
                g.user_set.add(instance)
        except Exception as e:
            msg = u'\n Create folder and add group to user ***** Error:%r' % e
            msg += '\n%s' % traceback.format_exc()
            logger.error(msg)
            print msg


def get_media_guard(login, pod_id=0):
    """ Get the media guard hash """
    MEDIA_GUARD = getattr(settings, 'MEDIA_GUARD', False)
    MEDIA_GUARD_SALT = getattr(settings, 'MEDIA_GUARD_SALT', None)
    if MEDIA_GUARD and MEDIA_GUARD_SALT and login:
        return hashlib.sha256(MEDIA_GUARD_SALT + login + str(pod_id)).hexdigest()
    else:
        return ""


def get_storage_path(instance, filename):
    """ Get the storage path. Instance needs to implement owner """
    fname, dot, extension = filename.rpartition('.')
    username = instance.owner.username
    pod_id = instance.id if instance.id else 0
    media_guard_hash = get_media_guard(username, pod_id)
    try:
        fname.index("/")
        return os.path.join(VIDEOS_DIR, username, media_guard_hash, '%s/%s.%s' % (os.path.dirname(fname), slugify(os.path.basename(fname)), extension))
    except:
        return os.path.join(VIDEOS_DIR, username, media_guard_hash, '%s.%s' % (slugify(fname), extension))


@python_2_unicode_compatible
class Video(models.Model):
    video = models.FileField(
        _('Video'),  upload_to=get_storage_path, max_length=255)
    allow_downloading = models.BooleanField(
        _('allow downloading'), default=False)
    is_360 = models.BooleanField(_('video 360'), default=False)
    title = models.CharField(_('Title'), max_length=250)
    slug = models.SlugField(_('Slug'), unique=True, max_length=255,
                            help_text=_(
                                'Used to access this instance, the "slug" is a short label containing only letters, numbers, underscore or dash top.'),
                            editable=False)
    owner = models.ForeignKey(User, verbose_name=_('Owner'))

    date_added = models.DateField(_('Date added'), default=datetime.now)
    date_evt = models.DateField(
        _(u'Date of event'), default=datetime.now, blank=True, null=True)

    cursus = models.CharField(
        _('University course'), max_length=1, choices=settings.CURSUS_CODES, default="0")

    main_lang = models.CharField(
        _('Main language'), max_length=2, choices=MAIN_LANG_CHOICES, default=get_language())

    description = RichTextField(
        _('Description'), config_name='complete', blank=True)

    view_count = models.PositiveIntegerField(
        _('View count'), default=0, editable=False)

    encoding_in_progress = models.BooleanField(
        _('Encoding in progress'), default=False, editable=False)
    encoding_status = models.CharField(
        _('Encoding status'), max_length=250, editable=False, blank=True, null=True)

    thumbnail = FilerImageField(
        null=True, blank=True, verbose_name=_('Thumbnail'))

    to_encode = models.BooleanField(default=False, editable=False)

    overview = models.ImageField(
        _('Overview'), null=True, upload_to=get_storage_path, blank=True, max_length=255, editable=False)

    duration = models.IntegerField(
        _('Duration'), default=0, editable=False, blank=True)
    infoVideo = models.TextField(null=True, blank=True, editable=False)

    class Meta:
        ordering = ['-date_added', '-id']
        get_latest_by = 'date_added'
        verbose_name = _("video")
        verbose_name_plural = _("videos")
        abstract = True

    def __unicode__(self):
        return u"Titre:%s - Prop:%s - Date:%s" % (self.title, self.owner, self.date_added)

    def __str__(self):
        return "%s" % (self.title)

    def filename(self):
        return os.path.basename(self.video.name)

    def admin_thumbnail(self):
        try:
            if self.thumbnail is None:
                return ""
            else:
                return "<img src=\"%s\" alt=\"%s\" />" % (self.thumbnail.icons['64'], self.title)
        except:
            return ""
    admin_thumbnail.short_description = _('Thumbnail')
    admin_thumbnail.allow_tags = True

    def duration_in_time(self):
        return time.strftime('%H:%M:%S', time.gmtime(self.duration))

    duration_in_time.short_description = _('Duration')
    duration_in_time.allow_tags = True


class EncodingType(models.Model):

    """
    encoding video in mp4 and Webm
    encoding audio in mp3 and Wav
    """
    name = models.CharField(_('name'), max_length=250)
    bitrate_audio = models.CharField(
        _('bitrate_audio'), max_length=250, help_text="Please use the only format k: i.e.: <em>300k</em> or <em>600k</em> or <em>1000k</em>.")
    bitrate_video = models.CharField(
        _('bitrate_video'), max_length=250, help_text="Please use the only format k. i.e.: <em>300k</em> or <em>600k</em> or <em>1000k</em>.", blank=True)
    HEIGHT_CHOICES = (
        (0, '0'),
        (240, '240'),
        (480, '480'),
        (640, '640'),
        (720, '720'),
        (1080, '1080'),
    )
    output_height = models.IntegerField(
        _('output_height'), choices=HEIGHT_CHOICES, default=240)
    TYPE_CHOICES = (
        ("audio", 'Audio'),
        ("video", 'Video'),
    )
    mediatype = models.CharField(
        _('mediatype'), max_length=5, choices=TYPE_CHOICES, default="video")

    class Meta:
        verbose_name = _("encoding type")
        verbose_name_plural = _("encoding types")

    def __str__(self):
        return "%s %s %s" % (self.mediatype, self.name, self.output_height)

    def __unicode__(self):
        return "%s %s %s" % (self.mediatype, self.name, self.output_height)


@python_2_unicode_compatible
class ContactUs(models.Model):
    name = models.CharField(_('Name'), max_length=250)
    email = models.EmailField(_('Email'), max_length=250)
    subject = models.CharField(_('Subject'), max_length=250)
    message = models.TextField(_('Message'))

    class Meta:
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")

    def __str__(self):
        return "%s %s %s" % (self.name, self.email, self.subject)

    def __unicode__(self):
        return "%s %s %s" % (self.name, self.email, self.subject)
