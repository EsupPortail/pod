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
from django.db.models.signals import post_save, pre_save
# django-taggit
from taggit.managers import TaggableManager, _TaggableManager, TaggableRel
from django.core.exceptions import ValidationError
from core.models import Video, get_storage_path, EncodingType
import base64
import logging
logger = logging.getLogger(__name__)
import unicodedata

# gloabl function to remove accent, use in tags


def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])


@python_2_unicode_compatible
class Channel(models.Model):
    title = models.CharField(_('Title'), max_length=100, unique=True)
    slug = models.SlugField(_('Slug'), unique=True, max_length=100,
                            help_text=_('Used to access this instance, the "slug" is a short label containing only letters, numbers, underscore or dash top.'))

    description = RichTextField(
        _('Description'), config_name='complete', blank=True)
    headband = FilerImageField(
        null=True, blank=True, verbose_name=_('Headband'))
    color = models.CharField(
        _('Background color'), max_length=10, blank=True, null=True)

    style = models.TextField(_('Extra style'), null=True, blank=True)

    owner = models.ForeignKey(
        User, related_name='owner_channels', verbose_name=_('Owner'))

    users = models.ManyToManyField(User, related_name='users_channels', verbose_name=_('Users'),
                                   null=True, blank=True)
    visible = models.BooleanField(verbose_name=_('Visible'),
                                  help_text=_(
                                      u'If checked, the channel appear in a list of available channels on the platform'),
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

    def video_count(self):
        return self.pod_set.filter(is_draft=False, encodingpods__gt=0).distinct().count()
        # return Video.objects.filter(categories__in=self.categories.all()).filter(is_draft=False).count()
        # return self.video_set.all().count()
    video_count.short_description = _('count')


@python_2_unicode_compatible
class Theme(models.Model):
    title = models.CharField(_('Title'), max_length=100, unique=True)
    slug = models.SlugField(_('Slug'), unique=True, max_length=100,
                            help_text=_('Used to access this instance, the "slug" is a short label containing only letters, numbers, underscore or dash top.'))
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

    def video_count(self):
        return self.pod_set.filter(is_draft=False, encodingpods__gt=0).distinct().count()
        # return Video.objects.filter(categories__in=self.categories.all()).filter(is_draft=False).count()
        # return self.video_set.all().count()
    video_count.short_description = _('count')


@python_2_unicode_compatible
class Type(models.Model):
    title = models.CharField(_('Title'), max_length=100, unique=True)
    slug = models.SlugField(_('Slug'), unique=True, max_length=100,
                            help_text=_('Used to access this instance, the "slug" is a short label containing only letters, numbers, underscore or dash top.'))
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

    def video_count(self):
        return self.pod_set.filter(is_draft=False, encodingpods__gt=0).distinct().count()
        # return Video.objects.filter(categories__in=self.categories.all()).filter(is_draft=False).count()
        # return self.video_set.all().count()
    video_count.short_description = _('count')


@python_2_unicode_compatible
class Discipline(models.Model):
    title = models.CharField(_('title'), max_length=100, unique=True)
    slug = models.SlugField(_('slug'), unique=True, max_length=100,
                            help_text=_('Used to access this instance, the "slug" is a short label containing only letters, numbers, underscore or dash top.'))
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

    def video_count(self):
        return self.pod_set.filter(is_draft=False, encodingpods__gt=0).distinct().count()
        # return Video.objects.filter(categories__in=self.categories.all()).filter(is_draft=False).count()
        # return self.video_set.all().count()
    video_count.short_description = _('count')


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
        Channel, blank=True, null=True, verbose_name=_('Channels'))
    theme = models.ManyToManyField(
        Theme, blank=True, null=True, verbose_name=_('Themes'))

    #tags = TaggableManager(help_text=_(u'Séparez les tags par des espaces, mettez les tags constituées de plusieurs mots entre guillemets.'), verbose_name=_('Tags'), blank=True)

    is_draft = models.BooleanField(verbose_name=_('Draft'), help_text=_(
        u'If you check this box, the video will be visible and accessible only by you'), default=True)
    is_restricted = models.BooleanField(verbose_name=_(u'Restricted access'), help_text=_(
        u'The video is accessible only by those who can authenticate to the site.'), default=False)
    password = models.CharField(_('password'), help_text=_(
        u'The video is available with the specified password.'), max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = _("Video")
        verbose_name_plural = _("Videos")

    def __unicode__(self):
        return u"Titre:%s - Prop:%s - Date:%s" % (self.title, self.owner, self.date_added)

    def __str__(self):
        return "%s - %s" % ('%04d' % self.id, self.title)

    def get_absolute_url(self):
        return reverse('video', args=[self.slug])

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
        super(Pod, self).delete()

    def is_richmedia(self):
        return self.enrichpods_set.exclude(type=None)


@receiver(post_save, sender=Pod)
def launch_encode(sender, instance, created, **kwargs):
    """
    if created:
        instance.to_encode=False
        instance.encoding_in_progress=True
        instance.save()
        start_encode(instance)
    else:
    """
    if instance.to_encode == True and instance.encoding_in_progress == False:
        instance.to_encode = False
        instance.encoding_in_progress = True
        instance.save()
        start_encode(instance)


def start_encode(video):
    print "START ENCODE VIDEO ID %s" % video.id
    import threading
    from core.utils import encode_video
    t = threading.Thread(target=encode_video,
                         args=[video])
    t.setDaemon(True)
    t.start()


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

    class Meta:
        verbose_name = _("Encoding Pod")
        verbose_name_plural = _("Encodings Pod")

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
        (_("authors"), _("authors")),
        (_("director"), _("director")),
        (_("editors"), _("editors")),
        (_("designers"), _("designers")),
        (_("contributor"), _("contributor")),
        (_("actor"), _("actor")),
        (_("voice-over"), _("voice-off")),
        (_("consultant"), _("consultant")),
        (_("writer"), _("writer")),
        (_("soundman"), _("soundman")),
        (_("technician"), _("technician"))
    )
    role = models.CharField(_(u'role'), max_length=200, null=True,
                            blank=True, choices=ROLE_CHOICES, default=_("authors"))
    weblink = models.URLField(
        _(u'Web link'), max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = _("Contributor Pod")
        verbose_name_plural = _("Contributors Pod")

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
        null=True, blank=True, verbose_name=_("Video track file"))

    class Meta:
        verbose_name = _("Track Pod")
        verbose_name_plural = _("Tracks Pod")

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

    def icon(self):
        return self.document.name.split('.')[-1]


@python_2_unicode_compatible
class EnrichPods(models.Model):
    video = models.ForeignKey(Pod, verbose_name=_('video'))
    title = models.CharField(_('title'), max_length=100)
    slug = models.SlugField(_('slug'), unique=True, max_length=105,
                            help_text=_(
                                'Used to access this instance, the "slug" is a short label containing only letters, numbers, underscore or dash top.'),
                            editable=False)

    #is_chapter = models.BooleanField(_('Is chapter ?'), default=False, help_text=_('Is chapter ?'))
    stop_video = models.BooleanField(_('Stop video'), default=False, help_text=_(
        'The video will pause when displaying this enrichment'))
    start = models.PositiveIntegerField(
        _('Start'), default=0, help_text=_('Start displaying enrichment in second'))
    end = models.PositiveIntegerField(
        _('Stop'), default=1, help_text=_('Stop displaying enrichment in second'))

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
    document = FilerFileField(null=True, blank=True, verbose_name="Document", help_text=_(
        'Integrate an document (PDF, text, html)'))
    embed = models.TextField(_('Embed'), max_length=300, null=True, blank=True, help_text=_(
        'Integrate an external source'))

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
        msg = self.verify_end_start_item() + self.verify_all_fields() + self.overlap()
        if(len(msg) > 0):
            raise ValidationError(msg)

    def verify_all_fields(self):
        msg = []
        if (not self.title or (self.title == "") or (len(self.title) < 2) or (len(self.title) > 100)):
            msg.append(_('Please enter a title form 2 to 100 caracteres '))

        if ((self.start == "") or (self.start < 0) or (self.start >= self.video.duration)):
            msg.append(_('Please enter a correct start field between 0 and %(duration)s') % {
                       "duration": self.video.duration - 1})

        if (not self.end or (self.end == "") or (self.end <= 0) or (self.end > self.video.duration)):
            msg.append(_('Please enter a correct end field between 1 and %(duration)s') % {
                       "duration": self.video.duration})

        if (self.type == "image"):
            if(not self.image):
                msg.append(_('Please enter a correct image '))

        elif (self.type == "richtext"):
            if(not self.richtext):
                msg.append(_('Please enter a correct richtext '))

        elif (self.type == "weblink"):
            if(not self.weblink):
                msg.append(_('Please enter a correct weblink '))

        elif (self.type == "document"):
            if(not self.document):
                msg.append(_('Please enter a correct document '))

        elif (self.type == "embed"):
            if(not self.embed):
                msg.append(_('Please enter a correct embed '))
        else:
            msg.append(_('Please enter a type in index field'))

        if (len(msg) > 0):
            return msg
        else:
            return []

    def verify_end_start_item(self):
        msg = []
        video = Pod.objects.get(id=self.video.id)
        if(self.start > self.end):
            msg.append(
                _('the value of the start field is greater than the value of end field '))
        elif(self.end > video.duration):
            msg.append(
                _('the value of end field is greater than the video duration'))
        elif (self.start == self.end):
            msg.append(_('end field and start field can\'t be equal'))

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
                    msg.append(_("There is a overlap with the " + element.title +
                                 " enrich, please change end field and start field "))
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
    slug = models.SlugField(_('slug'), unique=True, max_length=105,
                            help_text=_(
                                'Used to access this instance, the "slug" is a short label containing only letters, numbers, underscore or dash top.'),
                            editable=False)

    time = models.PositiveIntegerField(
        _('Start time'), default=0, help_text=_('Start time in second of the chapter'))

    class Meta:
        verbose_name = _("Chapter")
        verbose_name_plural = _("Chapters")
        ordering = ['time']
        #unique_together = ("video", "start")

    def __unicode__(self):
        return u"Chapter : %s - video: %s" % (self.title, self.video)

    def __str__(self):
        return u"Chapter : %s - video: %s" % (self.title, self.video)

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
        null=True, blank=True, verbose_name="Image", related_name="building_image")

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
    image = FilerImageField(
        null=True, blank=True, verbose_name="Image", related_name="recorder_image")
    adress_ip = models.IPAddressField(unique=True)
    status = models.BooleanField(default=0)
    slide = models.BooleanField(default=1)
    gmapurl = models.CharField(max_length=250, blank=True, null=True)
    is_restricted = models.BooleanField(verbose_name=_(u'Restricted access'), help_text=_(
        u'Live is accessible only by those who can authenticate on the website.'), default=False)
    building = models.ForeignKey('Building', verbose_name=_('Building'))

    def __unicode__(self):
        return "%s - %s" % (self.name, self.adress_ip)

    def __str__(self):
        return "%s - %s" % (self.name, self.adress_ip)

    def ipunder(self):
        return self.adress_ip.replace(".", "_")

    class Meta:
        verbose_name = _("Recorder")
        verbose_name_plural = _("Recorders")
