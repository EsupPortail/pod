
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
from filer.fields.image import FilerImageField
from filer.fields.file import FilerFileField
from django.utils.encoding import python_2_unicode_compatible
from ckeditor.fields import RichTextField
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from datetime import datetime
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, post_delete
from django.contrib.sites.shortcuts import get_current_site
from elasticsearch import Elasticsearch
# django-taggit
from taggit.managers import TaggableManager, _TaggableManager, TaggableRel
from django.core.exceptions import ValidationError
from core.models import Video, get_storage_path, EncodingType
import base64
import logging
from django.forms.formsets import ORDERING_FIELD_NAME
logger = logging.getLogger(__name__)
import unicodedata
import json
from pod_project.tasks import task_start_encode

ES_URL = getattr(settings, 'ES_URL', ['http://127.0.0.1:9200/'])
REMOVE_VIDEO_FILE_SOURCE_ON_DELETE = getattr(settings, 'REMOVE_VIDEO_FILE_SOURCE_ON_DELETE', True)


# gloabl function to remove accent, use in tags
def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])


@python_2_unicode_compatible
class Channel(models.Model):
    title = models.CharField(_('Title'), max_length=100, unique=True)
    slug = models.SlugField(
        _('Slug'), unique=True, max_length=100,
        help_text=_(
            u'Used to access this instance, the "slug" is a short label containing only letters, numbers, underscore or dash top.'))
    description = RichTextField(
        _('Description'), config_name='complete', blank=True)
    headband = FilerImageField(
        null=True, blank=True, verbose_name=_('Headband'))
    color = models.CharField(
        _('Background color'), max_length=10, blank=True, null=True)
    style = models.TextField(_('Extra style'), null=True, blank=True)
    owners = models.ManyToManyField(
        User, related_name='owners_channels', verbose_name=_('Owners'),
        blank=True)
    users = models.ManyToManyField(
        User, related_name='users_channels', verbose_name=_('Users'),
        blank=True)
    visible = models.BooleanField(
        verbose_name=_('Visible'),
        help_text=_(
            u'If checked, the channel appear in a list of available channels on the platform.'),
        default=False)

    class Meta:
        ordering = ['title']
        verbose_name = _('Channel')
        verbose_name_plural = _('Channels')

    def __unicode__(self):
        return self.title

    def __str__(self):
        return "%s" % (self.title)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Channel, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('channel', kwargs={'slug_c': self.slug})


@python_2_unicode_compatible
class Theme(models.Model):
    title = models.CharField(_('Title'), max_length=100, unique=True)
    slug = models.SlugField(
        _('Slug'), unique=True, max_length=100,
        help_text=_(
            u'Used to access this instance, the "slug" is a short label containing only letters, numbers, underscore or dash top.'))
    description = models.TextField(null=True, blank=True)
    headband = FilerImageField(
        null=True, blank=True, verbose_name=_('Headband'))
    channel = models.ForeignKey(
        'Channel', related_name='themes', verbose_name=_('Channel'))

    def __unicode__(self):
        return self.title

    def __str__(self):
        return "%s: %s" % (self.channel.title, self.title)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Theme, self).save(*args, **kwargs)

    class Meta:
        ordering = ['title']
        verbose_name = _('Theme')
        verbose_name_plural = _('Themes')

    def __unicode__(self):
        return "%s: %s" % (self.channel.title, self.title)

    def get_absolute_url(self):
        return reverse('theme', kwargs={'slug_c': self.channel.slug, 'slug_t': self.slug})


@python_2_unicode_compatible
class Type(models.Model):
    title = models.CharField(_('Title'), max_length=100, unique=True)
    slug = models.SlugField(
        _('Slug'), unique=True, max_length=100,
        help_text=_(
            u'Used to access this instance, the "slug" is a short label containing only letters, numbers, underscore or dash top.'))
    description = models.TextField(null=True, blank=True)
    headband = FilerImageField(
        null=True, blank=True, verbose_name=_('Headband'))

    def __unicode__(self):
        return self.title

    def __str__(self):
        return "%s" % (self.title)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Type, self).save(*args, **kwargs)

    class Meta:
        ordering = ['title']
        verbose_name = _('Type')
        verbose_name_plural = _('Types')

    def __unicode__(self):
        return "%s" % (self.title)


@python_2_unicode_compatible
class Discipline(models.Model):
    title = models.CharField(_('title'), max_length=100, unique=True)
    slug = models.SlugField(
        _('slug'), unique=True, max_length=100,
        help_text=_(
            u'Used to access this instance, the "slug" is a short label containing only letters, numbers, underscore or dash top.'))
    description = models.TextField(null=True, blank=True)
    headband = FilerImageField(
        null=True, blank=True, verbose_name=_('Headband'))

    def __unicode__(self):
        return self.title

    def __str__(self):
        return "%s" % (self.title)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Discipline, self).save(*args, **kwargs)

    class Meta:
        ordering = ['title']
        verbose_name = _('Discipline')
        verbose_name_plural = _('Disciplines')

    def __unicode__(self):
        return "%s" % (self.title)


def get_nextautoincrement(mymodel):
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("SELECT Auto_increment FROM information_schema.tables WHERE table_name='%s';" %
                   mymodel._meta.db_table)
    row = cursor.fetchone()
    cursor.close()
    return row[0]


from taggit.utils import require_instance_manager

#from south.modelsinspector import add_introspection_rules
#add_introspection_rules([], ["^pods\.models\.MyTaggableManager"])

#from south.modelsinspector import add_ignored_fields
# add_ignored_fields(["^pods\.models\.MyTaggableManager"])


class MyTaggableManager(TaggableManager):

    def __get__(self, instance, model):
        if instance is not None and instance.pk is None:
            raise ValueError("%s objects need to have a primary key value "
                             "before you can access their tags." % model.__name__)
        manager = _MyTaggableManager(
            through=self.through,
            model=model,
            instance=instance,
            prefetch_cache_name=self.name
        )
        return manager


class _MyTaggableManager(_TaggableManager):

    def __init__(self, through, model, instance, prefetch_cache_name):
        self.through = through
        self.model = model
        self.instance = instance
        self.prefetch_cache_name = prefetch_cache_name
        self._db = None
        self.force_lowercase = getattr(
            settings, 'TAGGIT_FORCE_LOWERCASE', True)

    @require_instance_manager
    def add(self, *tags):
        if self.force_lowercase:
            lower_tags = []
            for t in tags:
                if not isinstance(t, self.through.tag_model()):
                    t = remove_accents(t.lower())
                lower_tags.append(t)
            tags = lower_tags
        str_tags = set([
            remove_accents(t)
            for t in tags
            if not isinstance(t, self.through.tag_model())
        ])
        tag_objs = set(tags) - str_tags
        # If str_tags has 0 elements Django actually optimizes that to not do a
        # query.  Malcolm is very smart.
        existing = self.through.tag_model().objects.filter(
            name__in=str_tags
        )
        tag_objs.update(existing)

        for new_tag in str_tags - set(t.name for t in existing):
            tag_objs.add(self.through.tag_model().objects.create(name=new_tag))

        for tag in tag_objs:
            self.through.objects.get_or_create(
                tag=tag, **self._lookup_kwargs())


@python_2_unicode_compatible
class Pod(Video):
    tags = MyTaggableManager(
        help_text=_(
            u'Separate tags with spaces, enclose the tags consist of several words in quotation marks.'),
        verbose_name=_('Tags'), blank=True)
    type = models.ForeignKey(Type, verbose_name=_('Type'))
    discipline = models.ManyToManyField(
        Discipline, blank=True, verbose_name=_('Disciplines'))
    channel = models.ManyToManyField(
        Channel, verbose_name=_('Channels'), blank=True)
    theme = models.ManyToManyField(
        Theme, verbose_name=_('Themes'), blank=True)

    #tags = TaggableManager(help_text=_(u'Séparez les tags par des espaces, mettez les tags constituées de plusieurs mots entre guillemets.'), verbose_name=_('Tags'), blank=True)

    is_draft = models.BooleanField(
        verbose_name=_('Draft'),
        help_text=_(
            u'If this box is checked, the video will be visible and accessible only by you.'),
        default=True)
    is_restricted = models.BooleanField(
        verbose_name=_(u'Restricted access'),
        help_text=_(
            u'If this box is checked, the video will only be accessible to authenticated users.'),
        default=False)
    password = models.CharField(
        _('password'),
        help_text=_(
            u'Viewing this video will not be possible without this password.'),
        max_length=50, blank=True, null=True)
    _encoding_user_email_data = None

    class Meta:
        verbose_name = _("Video")
        verbose_name_plural = _("Videos")

    def __unicode__(self):
        return u"Titre:%s - Prop:%s - Date:%s" % (self.title, self.owner, self.date_added)

    def __str__(self):
        return "%s - %s" % ('%04d' % self.id, self.title)

    def get_absolute_url(self):
        return reverse('video', args=[self.slug])

    def get_full_url(self):
        request = None
        full_url = ''.join(
            ['//', get_current_site(request).domain, self.get_absolute_url()])
        return full_url

    def get_thumbnail_url(self):
        request = None
        if not self.thumbnail:
            return ""
        thumbnail_url = ''.join(
            ['//', get_current_site(request).domain, self.thumbnail.url])
        return thumbnail_url

    def save(self, *args, **kwargs):
        newid = -1
        if not self.id:
            try:
                newid = get_nextautoincrement(Pod)
            except:
                try:
                    newid = Pod.objects.latest('id').id
                    newid += 1
                except:
                    newid = 1
        else:
            newid = self.id
        newid = '%04d' % newid
        self.slug = "%s-%s" % (newid, slugify(self.title))
        super(Pod, self).save(*args, **kwargs)

    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in Pod._meta.fields]

    def get_all_encoding_height(self):
        all_encoding_type = self.encodingpods_set.values_list(
            'encodingType__output_height', flat=True).distinct()
        return all_encoding_type

    def get_encoding_240(self):
        encoding_240 = self.encodingpods_set.filter(
            encodingType__output_height=240)
        return encoding_240

    def get_MP4_240_URL(self):
        encoding_240 = EncodingPods.objects.get(
            video=self, encodingType__output_height=240, encodingFormat="video/mp4")
        return encoding_240.encodingFile.url

    def get_MP4_480_URL(self):
        encoding_480 = EncodingPods.objects.get(
            video=self, encodingType__output_height=480, encodingFormat="video/mp4")
        return encoding_480.encodingFile.url

    def get_MP4_720_URL(self):
        encoding_720 = EncodingPods.objects.get(
            video=self, encodingType__output_height=720, encodingFormat="video/mp4")
        return encoding_720.encodingFile.url

    def get_MP4_1080_URL(self):
        encoding_1080 = EncodingPods.objects.get(
            video=self, encodingType__output_height=1080, encodingFormat="video/mp4")
        return encoding_1080.encodingFile.url

    def get_mediatype(self):
        # print "get_mediatype : %s - %s" %(self.id,
        # self.encodingpods_set.values_list("encodingType__mediatype",
        # flat=True).distinct())
        return self.encodingpods_set.values_list("encodingType__mediatype", flat=True).distinct()

    def delete(self):
        if self.overview:
            self.overview.delete()
        # on supprime les encoding pods
        for encoding in self.encodingpods_set.all():
            if encoding.encodingFile:
                encoding.encodingFile.delete()

        # on supprime le fichier source
        if REMOVE_VIDEO_FILE_SOURCE_ON_DELETE:
            self.video.delete()
        super(Pod, self).delete()

    def is_richmedia(self):
        return True if self.enrichpods_set.exclude(type=None) else False

    def get_iframe_admin_integration(self):
        iframe_url = '<iframe src="%s?is_iframe=true&size=240" width="320" height="180" style="padding: 0; margin: 0; border:0" allowfullscreen ></iframe>' % self.get_full_url()
        return iframe_url

    def get_dublin_core(self):
        contributors = []
        for contrib in self.contributorpods_set.values_list('name', 'role'):
            contributors.append(" ".join(contrib))

        data_to_dump = {
            'dc.title': u'%s' % self.title,
            'dc.creator': u'%s' % self.owner.get_full_name(),
            'dc.description': u'%s' % self.description,
            'dc.subject': u'%s' % ', '.join(self.discipline.all().values_list('title', flat=True)),
            'dc.publisher': settings.TITLE_ETB if settings.TITLE_ETB else "",
            'dc.contributor': ", ".join(contributors),
            "dc.date": u'%s' % self.date_added.strftime('%Y/%m/%d') if self.date_added else "",
            "dc.type": self.get_mediatype()[0] if len(self.get_mediatype()) > 0 else "video",
            "dc.identifier": self.get_full_url(),
            "dc.language": u'%s' % self.main_lang,
            'dc.coverage': settings.DC_COVERAGE if settings.DC_COVERAGE else "",
            'dc.rights': settings.DC_RIGHTS if settings.DC_RIGHTS and not self.is_restricted and not self.password else "",
            "dc.format":  "audio/mp3" if len(self.get_mediatype()) > 0 and self.get_mediatype()[0] == "audio" else "video/mp4"
        }
        return data_to_dump

    def get_json_to_index(self):

        data_to_dump = {
            'id': self.id,
            'title': u'%s' % self.title,
            'owner': u'%s' % self.owner.username,
            'owner_full_name': u'%s' % self.owner.get_full_name(),
            "date_added": u'%s' % self.date_added.strftime('%Y-%m-%dT%H:%M:%S') if self.date_added else None,
            "date_evt": u'%s' % self.date_evt.strftime('%Y-%m-%dT%H:%M:%S') if self.date_evt else None,
            "description": u'%s' % self.description,
            "thumbnail": u'%s' % self.get_thumbnail_url(),
            "duration": u'%s' % self.duration,
            "tags": list(self.tags.all().values('name', 'slug')),
            "type": {"title": self.type.title, "slug": self.type.slug},
            "disciplines": list(self.discipline.all().values('title', 'slug')),
            "channels": list(self.channel.all().values('title', 'slug')),
            "themes": list(self.theme.all().values('title', 'slug')),
            "contributors": list(self.contributorpods_set.values_list('name', 'role')),
            "chapters": list(self.chapterpods_set.values('title', 'slug')),
            "enrichments": list(self.enrichpods_set.values('title', 'slug')),
            "full_url": self.get_full_url(),
            "is_restricted": self.is_restricted,
            "password": True if self.password != "" else False,
            "duration_in_time": self.duration_in_time(),
            "mediatype": self.get_mediatype()[0] if len(self.get_mediatype()) > 0 else "video",
            "is_richmedia": self.is_richmedia(),
            "cursus": u'%s' % self.cursus,
            "main_lang": u'%s' % self.main_lang,
        }

        return json.dumps(data_to_dump)

    def set_encoding_user_email_data(self, user_email, curr_lang, root_url):
        self._encoding_user_email_data = {
            'user_email': user_email,
            'curr_lang': curr_lang,
            'root_url': root_url
        }

    def get_encoding_user_email_data(self):
        return self._encoding_user_email_data


@receiver(post_save, sender=Pod)
def launch_encode(sender, instance, created, **kwargs):
    if instance.to_encode == True and instance.encoding_in_progress == False:
        instance.to_encode = False
        instance.encoding_in_progress = True
        instance.save()
        if settings.CELERY_TO_ENCODE:
            task_start_encode.delay(instance)
        else:
            start_encode(instance)


def start_encode(video):
    print "START ENCODE VIDEO ID %s" % video.id
    import threading
    from core.utils import encode_video
    t = threading.Thread(target=encode_video,
                         args=[video])
    t.setDaemon(True)
    t.start()


@receiver(post_save)  # instead of @receiver(post_save, sender=Rebel)
def update_video_index(sender, instance=None, created=False, **kwargs):
    list_of_models = ('ChapterPods', 'EnrichPods', 'ContributorPods', 'Pod')
    if sender.__name__ in list_of_models:  # this is the dynamic part you want
        pod = None
        if sender.__name__ == "Pod":
            pod = instance
        else:
            pod = instance.video
        es = Elasticsearch(ES_URL)
        if pod.is_draft == False and pod.encodingpods_set.all().count() > 0:
            res = es.index(index="pod", doc_type='pod', id=pod.id,
                           body=pod.get_json_to_index(), refresh=True)
        else:
            delete = es.delete(
                index="pod", doc_type='pod', id=pod.id, refresh=True, ignore=[400, 404])

@receiver(post_delete)  # instead of @receiver(post_save, sender=Rebel)
def update_es_index(sender, instance=None, created=False, **kwargs):
    print "POST DELETE"
    list_of_models = ('ChapterPods', 'EnrichPods', 'ContributorPods', 'Pod')
    if sender.__name__ in list_of_models:  # this is the dynamic part you want
        pod = None
        es = Elasticsearch(ES_URL)
        if sender.__name__ == "Pod":
            pod = instance
            delete = es.delete(
                index="pod", doc_type='pod', id=pod.id, refresh=True, ignore=[400, 404])
        else:
            pod = instance.video
            res = es.index(index="pod", doc_type='pod', id=pod.id,
                           body=pod.get_json_to_index(), refresh=True)


@python_2_unicode_compatible
class EncodingPods(models.Model):
    video = models.ForeignKey(Pod, verbose_name=_('Video'))
    encodingType = models.ForeignKey(
        EncodingType, verbose_name=_('encodingType'))
    encodingFile = models.FileField(
        _('encodingFile'), null=True, upload_to=get_storage_path, blank=True, max_length=255)
    FORMAT_CHOICES = (
        ("video/mp4", 'video/mp4'),
        ("video/webm", 'video/webm'),
        ("audio/mp3", "audio/mp3"),
        ("audio/wav", "audio/wav")
    )
    encodingFormat = models.CharField(
        _('Format'), max_length=12, choices=FORMAT_CHOICES, default="video/mp4")

    @property
    def owner(self):
        """ return video owner """
        return self.video.owner

    class Meta:
        verbose_name = _("encoding")
        verbose_name_plural = _("encodings")

    def __unicode__(self):
        return u"Video:%s - EncodingType:%s - EncodingFile:%s" % (self.video, self.encodingType, self.encodingFile)

    def __str__(self):
        return u"Video:%s - EncodingType:%s - EncodingFile:%s" % (self.video, self.encodingType, self.encodingFile)

    def delete(self):
        if self.encodingFile:
            self.encodingFile.delete()

        super(EncodingPods, self).delete()


@python_2_unicode_compatible
class ContributorPods(models.Model):
    video = models.ForeignKey(Pod, verbose_name=_('video'))
    name = models.CharField(_('lastname / firstname'), max_length=200)
    email_address = models.EmailField(
        _('mail'), null=True, blank=True, default="")
    ROLE_CHOICES = (
        ("actor", _("actor")),
        ("author", _("author")),
        ("designer", _("designer")),
        ("consultant", _("consultant")),
        ("contributor", _("contributor")),
        ("editor", _("editor")),
        ("speaker", _("speaker")),
        ("soundman", _("soundman")),
        ("director", _("director")),
        ("writer", _("writer")),
        ("technician", _("technician")),
        ("voice-over", _("voice-over"))
    )
    role = models.CharField(
        _(u'role'), max_length=200, choices=ROLE_CHOICES, default="author")
    weblink = models.URLField(
        _(u'Web link'), max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = _("Contributor Pod")
        verbose_name_plural = _("Contributors Pod")

    def clean(self):
        # Don't allow draft entries to have a pub_date.
        msg = []
        msg = self.verify_attributs() + self.verify_not_same_contributor()
        if(len(msg) > 0):
            raise ValidationError(msg)

    def verify_attributs(self):
        msg = []
        if not self.name or self.name == "" or len(self.name) < 2 or len(self.name) > 200:
            msg.append(_('please enter a name from 2 to 200 caracteres.'))
        if self.weblink and len(self.weblink) > 200:
            msg.append(
                _('you cannot enter a weblink with more than 200 caracteres.'))
        if not self.role:
            msg.append(_('please enter a role.'))
        if (len(msg) > 0):
            return msg
        else:
            return []

    def verify_not_same_contributor(self):
        msg = []
        list_contributorpods = ContributorPods.objects.filter(video=self.video)
        if self.id != None:
            list_contributorpods = list_contributorpods.exclude(id=self.id)
        if len(list_contributorpods) > 0:
            for element in list_contributorpods:
                if self.name == element.name and self.role == element.role:
                    msg.append(
                        _("there is already a contributor with the same name and role in the list."))
                    return msg
        return []

    def __unicode__(self):
        return u"Video:%s - Name:%s - Role:%s" % (self.video, self.name, self.role)

    def __str__(self):
        return u"Video:%s - Name:%s - Role:%s" % (self.video, self.name, self.role)

    def get_base_mail(self):
        return u'%s' % base64.b64encode(self.email_address.encode('utf-8'))

    def get_noscript_mail(self):
        return self.email_address.replace("@", "__AT__")


@python_2_unicode_compatible
class TrackPods(models.Model):
    video = models.ForeignKey(Pod, verbose_name=_('video'))
    # kind : subtitles, captions, descriptions, chapters or metadata
    KIND_CHOICES = (
        ("subtitles", _("subtitles")),
        ("captions", _("captions")),
    )
    kind = models.CharField(
        _('Kind'), max_length=10, choices=KIND_CHOICES, default="subtitles")
    LANG_CHOICES = (
        ("", settings.PREF_LANG_CHOICES), ("-----------", settings.ALL_LANG_CHOICES))
    lang = models.CharField(_('Language'), max_length=2, choices=LANG_CHOICES)
    src = FilerFileField(
        null=True, blank=True, verbose_name=_("subtitle file"))

    class Meta:
        verbose_name = _("Track Pod")
        verbose_name_plural = _("Tracks Pod")

    def clean(self):
        # Don't allow draft entries to have a pub_date.
        msg = []
        msg = self.verify_attributs() + self.verify_not_same_trackpod()
        if(len(msg) > 0):
            raise ValidationError(msg)

    def verify_attributs(self):
        msg = []
        if not self.kind or (self.kind != "subtitles" and self.kind != "captions"):
            msg.append(_('please enter a correct kind.'))
        if not self.lang or (self.lang in settings.PREF_LANG_CHOICES or self.lang in settings.ALL_LANG_CHOICES):
            msg.append(_('please enter a correct lang.'))
        if not self.src:
            msg.append(_('please specify a track file.'))
        if not str(self.src).lower().endswith('.vtt'):
            msg.append(_('only “.vtt” format is allowed.'))
        if (len(msg) > 0):
            return msg
        else:
            return []

    def verify_not_same_trackpod(self):
        msg = []
        list_trackpods = TrackPods.objects.filter(video=self.video)
        if self.id != None:
            list_trackpods = list_trackpods.exclude(id=self.id)
        if len(list_trackpods) > 0:
            for element in list_trackpods:
                if self.kind == element.kind and self.lang == element.lang:
                    msg.append(
                        _("there is already a subtitle with the same kind and language in the list."))
                    return msg
        return []

    def __unicode__(self):
        return u"%s - File: %s - Video: %s" % (self.kind, self.src, self.video)

    def __str__(self):
        return u"%s - File: %s - Video: %s" % (self.kind, self.src, self.video)


@python_2_unicode_compatible
class DocPods(models.Model):
    video = models.ForeignKey(Pod, verbose_name=_('Video'))
    document = FilerFileField(null=True, blank=True, verbose_name="Document")

    class Meta:
        verbose_name = _("Document Pod")
        verbose_name_plural = _("Documents Pod")

    def __unicode__(self):
        return u"Document: %s - video: %s" % (self.document, self.video)

    def __str__(self):
        return u"Document: %s - video: %s" % (self.document, self.video)

    def clean(self):
        msg = []
        msg = self.verify_document() + self.verify_not_same_document()
        if(len(msg) > 0):
            raise ValidationError(msg)

    def verify_document(self):
        msg = []
        if not self.document:
            msg.append(_('please enter a document '))

        if (len(msg) > 0):
            return msg
        else:
            return []

    def verify_not_same_document(self):
        msg = []
        list_docpods = DocPods.objects.filter(video=self.video)
        if self.id != None:
            list_docpods = list_docpods.exclude(id=self.id)
        if len(list_docpods) > 0:
            for element in list_docpods:
                if self.document == element.document:
                    msg.append(
                        _("this document is already contained in the list."))
            if len(msg) > 0:
                return msg
        return []

    def icon(self):
        return self.document.name.split('.')[-1]


@python_2_unicode_compatible
class EnrichPods(models.Model):
    video = models.ForeignKey(Pod, verbose_name=_('video'))
    title = models.CharField(_('title'), max_length=100)
    slug = models.SlugField(
        _('slug'), unique=True, max_length=105,
        help_text=_(
            u'Used to access this instance, the "slug" is a short label containing only letters, numbers, underscore or dash top.'),
        editable=False)
    #is_chapter = models.BooleanField(_('Is chapter ?'), default=False, help_text=_('Is chapter ?'))
    stop_video = models.BooleanField(_('Stop video'), default=False, help_text=_(
        'The video will pause when displaying this enrichment.'))
    start = models.PositiveIntegerField(
        _('Start'), default=0,
        help_text=_('Start of enrichment display in seconds'))
    end = models.PositiveIntegerField(
        _('End'), default=1,
        help_text=_('End of enrichment display in seconds'))

    ENRICH_CHOICES = (
        ("image", _("image")),
        ("richtext", _("richtext")),
        ("weblink", _("weblink")),
        ("document", _("document")),
        ("embed", _("embed")),
    )
    type = models.CharField(
        _('Type'), max_length=10, choices=ENRICH_CHOICES, null=True, blank=True)

    image = FilerImageField(
        null=True, blank=True, verbose_name="Image", related_name="chapter_image")
    richtext = RichTextField(_('richtext'), config_name='complete', blank=True)
    weblink = models.URLField(
        _(u'Web link'), max_length=200, null=True, blank=True)
    document = FilerFileField(
        null=True, blank=True, verbose_name="Document",
        help_text=_(
            u'Integrate an document (PDF, text, html)'))
    embed = models.TextField(
        _('Embed'), max_length=300, null=True, blank=True,
        help_text=_(
            u'Integrate an external source'))

    class Meta:
        verbose_name = _("Enrichment")
        verbose_name_plural = _("Enrichments")
        ordering = ['start']
        #unique_together = ("video", "start")

    def __unicode__(self):
        return u"Media : %s - video: %s" % (self.title, self.video)

    def __str__(self):
        return u"Media : %s - video: %s" % (self.title, self.video)

    def clean(self):
        # Don't allow draft entries to have a pub_date.
        msg = []
        msg = self.verify_end_start_item() + self.verify_all_fields() + \
            self.overlap()
        if(len(msg) > 0):
            raise ValidationError(msg)

    def verify_all_fields(self):
        msg = []
        if (not self.title or (self.title == "") or (len(self.title) < 2) or (len(self.title) > 100)):
            msg.append(_('Please enter a title from 2 to 100 characters.'))

        if ((self.start == "") or (self.start < 0) or (self.start >= self.video.duration)):
            msg.append(_('Please enter a correct start field between 0 and %(duration)s.') % {
                       "duration": self.video.duration - 1})

        if (not self.end or (self.end == "") or (self.end <= 0) or (self.end > self.video.duration)):
            msg.append(_('Please enter a correct end field between 1 and %(duration)s.') % {
                       "duration": self.video.duration})
        if (self.type == "image"):
            if(not self.image):
                msg.append(_('Please enter a correct image.'))

        elif (self.type == "richtext"):
            if(not self.richtext):
                msg.append(_('Please enter a correct richtext.'))

        elif (self.type == "weblink"):
            if(not self.weblink):
                msg.append(_('Please enter a correct weblink.'))

        elif (self.type == "document"):
            if(not self.document):
                msg.append(_('Please select a document.'))

        elif (self.type == "embed"):
            if(not self.embed):
                msg.append(_('Please enter a correct embed.'))
        else:
            msg.append(_('Please enter a type in index field.'))

        if (len(msg) > 0):
            return msg
        else:
            return []

    def verify_end_start_item(self):
        msg = []
        video = Pod.objects.get(id=self.video.id)
        if(self.start > self.end):
            msg.append(
                _('The value of the start field is greater than the value of end field.'))
        elif(self.end > video.duration):
            msg.append(
                _('The value of end field is greater than the video duration.'))
        elif (self.start == self.end):
            msg.append(_('End field and start field can\'t be equal.'))

        if (len(msg) > 0):
            return msg
        else:
            return []

    def overlap(self):
        msg = []
        instance = None
        if self.slug:
            instance = EnrichPods.objects.get(slug=self.slug)
        list_enrichment = EnrichPods.objects.filter(video=self.video)
        if instance:
            list_enrichment = list_enrichment.exclude(id=instance.id)
        if len(list_enrichment) > 0:
            for element in list_enrichment:
                if not ((self.start < element.start and self.end <= element.start) or (self.start >= element.end and self.end > element.end)):
                    msg.append(_("There is an overlap with the enrichment " + element.title +
                                 ", please change start and/or end values."))
            if len(msg) > 0:
                return msg
        return []

    def save(self, *args, **kwargs):
        newid = -1
        if not self.id:
            try:
                newid = get_nextautoincrement(EnrichPods)
            except:
                try:
                    newid = EnrichPods.objects.latest('id').id
                    newid += 1
                except:
                    newid = 1
        else:
            newid = self.id
        newid = '%04d' % newid
        self.slug = "%s-%s" % (newid, slugify(self.title))

        super(EnrichPods, self).save(*args, **kwargs)


@python_2_unicode_compatible
class ChapterPods(models.Model):
    video = models.ForeignKey(Pod, verbose_name=_('video'))
    title = models.CharField(_('title'), max_length=100)
    slug = models.SlugField(
        _('slug'), unique=True, max_length=105,
        help_text=_(
            u'Used to access this instance, the "slug" is a short label containing only letters, numbers, underscore or dash top.'),
        editable=False)
    time = models.PositiveIntegerField(
        _('Start time'), default=0,
        help_text=_(u'Start time of the chapter, in seconds.'))

    class Meta:
        verbose_name = _("Chapter")
        verbose_name_plural = _("Chapters")
        ordering = ['time']
        #unique_together = ("video", "start")

    def __unicode__(self):
        return u"Chapter : %s - video: %s" % (self.title, self.video)

    def __str__(self):
        return u"Chapter : %s - video: %s" % (self.title, self.video)

    def clean(self):
        msg = []
        msg = self.verify_start_title_items() + self.verify_overlap()
        if(len(msg) > 0):
            raise ValidationError(msg)

    def verify_start_title_items(self):
        msg = []
        if (not self.title or (self.title == "") or (len(self.title) < 2) or (len(self.title) > 100)):
            msg.append(_('Please enter a title from 2 to 100 characters.'))

        if ((self.time == "") or (self.time < 0) or (self.time >= self.video.duration)):
            msg.append(_('Please enter a correct start field between 0 and %(duration)s.') % {
                       "duration": self.video.duration - 1})
        if len(msg) > 0:
            return msg
        return []

    def verify_overlap(self):
        msg = []
        instance = None
        if self.slug:
            instance = ChapterPods.objects.get(slug=self.slug)
        list_chapter = ChapterPods.objects.filter(video=self.video)
        if instance:
            list_chapter = list_chapter.exclude(id=instance.id)
        if len(list_chapter) > 0:
            for element in list_chapter:
                if self.time == element.time:
                    msg.append(
                        _("There is an overlap with the chapter " + element.title + ", please change start and/or end values."))
            if len(msg) > 0:
                return msg
        return []

    def save(self, *args, **kwargs):
        newid = -1
        if not self.id:
            try:
                newid = get_nextautoincrement(ChapterPods)
            except:
                try:
                    newid = ChapterPods.objects.latest('id').id
                    newid += 1
                except:
                    newid = 1
        else:
            newid = self.id
        newid = '%04d' % newid
        self.slug = "%s-%s" % (newid, slugify(self.title))

        super(ChapterPods, self).save(*args, **kwargs)


@python_2_unicode_compatible
class Favorites(models.Model):
    user = models.ForeignKey(User)
    video = models.ForeignKey(Pod)

    class Meta:
        verbose_name = _("Favorite")
        verbose_name_plural = _("Favorites")

    def __unicode__(self):
        return "%s-%s" % (self.user.username, self.video)

    def __str__(self):
        return "%s-%s" % (self.user.username, self.video)


@python_2_unicode_compatible
class Notes(models.Model):
    user = models.ForeignKey(User)
    video = models.ForeignKey(Pod)
    note = models.TextField(_('Note'), null=True, blank=True)

    class Meta:
        verbose_name = _("Note")
        verbose_name_plural = _("Notes")

    def __unicode__(self):
        return "%s-%s" % (self.user.username, self.video)

    def __str__(self):
        return "%s-%s" % (self.user.username, self.video)

##################################### RECORDER ###########################


@python_2_unicode_compatible
class Mediacourses(models.Model):
    user = models.ForeignKey(User)
    title = models.CharField(_('title'), max_length=200)
    date_added = models.DateTimeField(
        'date added', default=datetime.now, editable=False)
    mediapath = models.CharField(max_length=250, unique=True)
    started = models.BooleanField(default=0)
    error = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = _("Mediacourse")
        verbose_name_plural = _("Mediacourses")

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super(Mediacourses, self).save(*args, **kwargs)
        if self.started == False:
            import threading
            #from gestion_video.utils import process_mediacours
            from pods.utils_mediacours import process_mediacours
            t = threading.Thread(target=process_mediacours,
                                 args=[self])
            t.setDaemon(True)
            t.start()


@python_2_unicode_compatible
class Building(models.Model):
    name = models.CharField(_('name'), max_length=200, unique=True)
    image = FilerImageField(
        null=True, blank=True, verbose_name="Image",
        related_name="building_image")

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Building")
        verbose_name_plural = _("Buildings")


@python_2_unicode_compatible
class Recorder(models.Model):
    name = models.CharField(_('name'), max_length=200, unique=True)
    building = models.ForeignKey('Building', verbose_name=_('Building'))
    description = RichTextField(
        _('description'), config_name='complete', blank=True)
    image = FilerImageField(
        null=True, blank=True, verbose_name="Image",
        related_name="recorder_image")
    adress_ip = models.GenericIPAddressField(unique=True)
    status = models.BooleanField(default=0)
    slide = models.BooleanField(default=1)
    gmapurl = models.CharField(max_length=250, blank=True, null=True)
    is_restricted = models.BooleanField(
        verbose_name=_(u'Restricted access'),
        help_text=_(
            u'Live is accessible only to authenticated users.'),
        default=False)

    def __unicode__(self):
        return "%s - %s" % (self.name, self.adress_ip)

    def __str__(self):
        return "%s - %s" % (self.name, self.adress_ip)

    def ipunder(self):
        return self.adress_ip.replace(".", "_")

    class Meta:
        verbose_name = _("Recorder")
        verbose_name_plural = _("Recorders")

# REPORT VIDEO


@python_2_unicode_compatible
class ReportVideo(models.Model):
    video = models.ForeignKey(Pod, verbose_name=_('Video'))
    user = models.ForeignKey(User, verbose_name=_('User'))
    comment = models.TextField(
        null=True, blank=True, verbose_name=_('Comment'))
    answer = models.TextField(null=True, blank=True, verbose_name=_('Answer'))
    date_added = models.DateTimeField(
        'Date', default=datetime.now, editable=False)

    def __unicode__(self):
        return "%s - %s" % (self.video, self.user)

    def __str__(self):
        return "%s - %s" % (self.video, self.user)

    def get_iframe_url_to_video(self):
        return self.video.get_iframe_admin_integration()

    get_iframe_url_to_video.allow_tags = True

    class Meta:
        verbose_name = _("Report")
        verbose_name_plural = _("Reports")
        unique_together = ('video', 'user',)

@python_2_unicode_compatible
class Rssfeed(models.Model):
    AUDIO = 'A'
    VIDEO = 'V'
    TYPE_CHOICES = (
        (AUDIO, 'Audio'),
        (VIDEO, 'Vidéo'),
    )
    title = models.CharField(max_length=200, blank=False, unique_for_year='date_update')
    description = models.TextField(blank=False)
    link_rss = models.URLField(max_length=200, blank=False)
    type_rss = models.CharField(max_length=1,
                           choices=TYPE_CHOICES,
                           default=AUDIO)
    year = models.PositiveSmallIntegerField(default=2017)
    date_update = models.DateTimeField(auto_now=True)
    # récupérer le user à la création
    owner = models.ForeignKey(User, blank=False, null=False, on_delete=models.PROTECT, default=1)
    filters = models.TextField(blank=True)
    fil_type_pod = models.ForeignKey(Type, verbose_name=_('Type'))
    fil_discipline = models.ManyToManyField(
        Discipline, blank=True, verbose_name=_('Disciplines'))
    fil_channel = models.ManyToManyField(
        Channel, verbose_name=_('Channels'), blank=True)
    fil_theme = models.ManyToManyField(
        Theme, verbose_name=_('Themes'), blank=True)
    limit = models.SmallIntegerField(verbose_name=_('Count items'),
                                     help_text=_(u'Keep 0 to mean all items'),default=0)
    is_up = models.BooleanField(verbose_name=_('Visible'),
        help_text=_(
            u'If this box is checked, the video will be visible and accessible by anyone.'),
        default=True)

    class Meta:
        verbose_name = _("RSS")
        verbose_name_plural = _("RSS")


    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title
