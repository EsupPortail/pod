# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import filer.fields.file
import datetime
import core.models
import filer.fields.image
import ckeditor.fields
import pods.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
        ('filer', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(
                    unique=True, max_length=200, verbose_name='name')),
                ('image', filer.fields.image.FilerImageField(related_name='building_image',
                                                             verbose_name='Image', blank=True, to='filer.Image', null=True)),
            ],
            options={
                'verbose_name': 'Building',
                'verbose_name_plural': 'Buildings',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(
                    unique=True, max_length=100, verbose_name='Title')),
                ('title_fr', models.CharField(
                    max_length=100, unique=True, null=True, verbose_name='Title')),
                ('title_en', models.CharField(
                    max_length=100, unique=True, null=True, verbose_name='Title')),
                ('slug', models.SlugField(help_text='Used to access this instance, the "slug" is a short label containing only letters, numbers, underscore or dash top.',
                                          unique=True, max_length=100, verbose_name='Slug')),
                ('description', ckeditor.fields.RichTextField(
                    verbose_name='Description', blank=True)),
                ('color', models.CharField(
                    max_length=10, null=True, verbose_name='Background color', blank=True)),
                ('style', models.TextField(
                    null=True, verbose_name='Extra style', blank=True)),
                ('visible', models.BooleanField(
                    default=False, help_text='If checked, the channel appear in a list of available channels on the platform', verbose_name='Visible')),
                ('headband', filer.fields.image.FilerImageField(
                    verbose_name='Headband', blank=True, to='filer.Image', null=True)),
                ('owner', models.ForeignKey(related_name='owner_channels',
                                            verbose_name='Owner', to=settings.AUTH_USER_MODEL)),
                ('users', models.ManyToManyField(related_name='users_channels', null=True,
                                                 verbose_name='Users', to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'ordering': ['title'],
                'verbose_name': 'Channel',
                'verbose_name_plural': 'Channels',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ChapterPods',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(
                    max_length=100, verbose_name='title')),
                ('slug', models.SlugField(editable=False, max_length=105,
                                          help_text='Used to access this instance, the "slug" is a short label containing only letters, numbers, underscore or dash top.', unique=True, verbose_name='slug')),
                ('time', models.PositiveIntegerField(
                    default=0, help_text='Start time in second of the chapter', verbose_name='Start time')),
            ],
            options={
                'ordering': ['time'],
                'verbose_name': 'Chapter',
                'verbose_name_plural': 'Chapters',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContributorPods',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(
                    max_length=200, verbose_name='lastname / firstname')),
                ('email_address', models.EmailField(
                    default='', max_length=75, null=True, verbose_name='mail', blank=True)),
                ('role', models.CharField(default='authors', choices=[('authors', 'authors'), ('director', 'director'), ('editors', 'editors'), ('designers', 'designers'), ('contributor', 'contributor'), ('actor', 'actor'), (
                    'voice-over', 'voice-off'), ('consultant', 'consultant'), ('writer', 'writer'), ('soundman', 'soundman'), ('technician', 'technician')], max_length=200, blank=True, null=True, verbose_name='role')),
                ('weblink', models.URLField(
                    null=True, verbose_name='Web link', blank=True)),
            ],
            options={
                'verbose_name': 'Contributor Pod',
                'verbose_name_plural': 'Contributors Pod',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Discipline',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(
                    unique=True, max_length=100, verbose_name='title')),
                ('title_fr', models.CharField(
                    max_length=100, unique=True, null=True, verbose_name='title')),
                ('title_en', models.CharField(
                    max_length=100, unique=True, null=True, verbose_name='title')),
                ('slug', models.SlugField(help_text='Used to access this instance, the "slug" is a short label containing only letters, numbers, underscore or dash top.',
                                          unique=True, max_length=100, verbose_name='slug')),
                ('description', models.TextField(null=True, blank=True)),
                ('headband', filer.fields.image.FilerImageField(
                    verbose_name='Headband', blank=True, to='filer.Image', null=True)),
            ],
            options={
                'ordering': ['title'],
                'verbose_name': 'Discipline',
                'verbose_name_plural': 'Disciplines',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DocPods',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('document', filer.fields.file.FilerFileField(
                    verbose_name='Document', blank=True, to='filer.File', null=True)),
            ],
            options={
                'verbose_name': 'Document Pod',
                'verbose_name_plural': 'Documents Pod',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EncodingPods',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('encodingFile', models.FileField(max_length=255, upload_to=core.models.get_storage_path,
                                                  null=True, verbose_name='encodingFile', blank=True)),
                ('encodingFormat', models.CharField(default='video/mp4', max_length=12, verbose_name='Format', choices=[
                 ('video/mp4', 'video/mp4'), ('video/webm', 'video/webm'), ('audio/mp3', 'audio/mp3'), ('audio/wav', 'audio/wav')])),
                ('encodingType', models.ForeignKey(
                    verbose_name='encodingType', to='core.EncodingType')),
            ],
            options={
                'verbose_name': 'Encoding Pod',
                'verbose_name_plural': 'Encodings Pod',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EnrichPods',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(
                    max_length=100, verbose_name='title')),
                ('slug', models.SlugField(editable=False, max_length=105,
                                          help_text='Used to access this instance, the "slug" is a short label containing only letters, numbers, underscore or dash top.', unique=True, verbose_name='slug')),
                ('stop_video', models.BooleanField(
                    default=False, help_text='The video will pause when displaying this enrichment.', verbose_name='Stop video')),
                ('start', models.PositiveIntegerField(
                    default=0, help_text='Start displaying enrichment in second', verbose_name='Start')),
                ('end', models.PositiveIntegerField(
                    default=0, help_text='Stop displaying enrichment in second', verbose_name='Stop')),
                ('type', models.CharField(blank=True, max_length=10, null=True, verbose_name='Type', choices=[
                 ('image', 'image'), ('richtext', 'richtext'), ('weblink', 'weblink'), ('document', 'document'), ('embed', 'embed')])),
                ('richtext', ckeditor.fields.RichTextField(
                    verbose_name='richtext', blank=True)),
                ('weblink', models.URLField(
                    null=True, verbose_name='Web link', blank=True)),
                ('embed', models.TextField(help_text='Integrate an external source',
                                           max_length=300, null=True, verbose_name='Embed', blank=True)),
                ('document', filer.fields.file.FilerFileField(blank=True, to='filer.File',
                                                              help_text='Integrate an document (PDF, text, html)', null=True, verbose_name='Document')),
                ('image', filer.fields.image.FilerImageField(related_name='chapter_image',
                                                             verbose_name='Image', blank=True, to='filer.Image', null=True)),
            ],
            options={
                'ordering': ['start'],
                'verbose_name': 'Enrichment',
                'verbose_name_plural': 'Enrichments',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Favorites',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Favorite',
                'verbose_name_plural': 'Favorites',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Mediacourses',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(
                    max_length=200, verbose_name='title')),
                ('date_added', models.DateTimeField(
                    default=datetime.datetime.now, verbose_name='date added', editable=False)),
                ('mediapath', models.CharField(unique=True, max_length=250)),
                ('started', models.BooleanField(default=0)),
                ('error', models.TextField(null=True, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Mediacourse',
                'verbose_name_plural': 'Mediacourses',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Notes',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('note', models.TextField(
                    null=True, verbose_name='Note', blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Note',
                'verbose_name_plural': 'Notes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Pod',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('video', models.FileField(
                    upload_to=core.models.get_storage_path, max_length=255, verbose_name='Video')),
                ('allow_downloading', models.BooleanField(
                    default=False, verbose_name='allow downloading')),
                ('title', models.CharField(
                    max_length=250, verbose_name='Title')),
                ('slug', models.SlugField(editable=False, max_length=255,
                                          help_text='Used to access this instance, the "slug" is a short label containing only letters, numbers, underscore or dash top.', unique=True, verbose_name='Slug')),
                ('date_added', models.DateField(
                    default=datetime.datetime.now, verbose_name='Creation date')),
                ('date_evt', models.DateField(default=datetime.datetime.now,
                                              null=True, verbose_name='Date of the event', blank=True)),
                ('description', ckeditor.fields.RichTextField(
                    verbose_name='Description', blank=True)),
                ('view_count', models.PositiveIntegerField(
                    default=0, editable=False)),
                ('encoding_in_progress', models.BooleanField(
                    default=False, editable=False)),
                ('encoding_status', models.CharField(verbose_name='Encoding status',
                                                     max_length=250, null=True, editable=False, blank=True)),
                ('to_encode', models.BooleanField(
                    default=False, editable=False)),
                ('overview', models.ImageField(editable=False, upload_to=core.models.get_storage_path,
                                               max_length=255, blank=True, null=True, verbose_name='Overview')),
                ('duration', models.IntegerField(
                    default=0, verbose_name='Duration', max_length=12, editable=False, blank=True)),
                ('infoVideo', models.TextField(
                    null=True, editable=False, blank=True)),
                ('is_draft', models.BooleanField(
                    default=True, help_text='If you check this box, the video will be visible and accessible only by you', verbose_name='Draft')),
                ('is_restricted', models.BooleanField(
                    default=False, help_text='The video is accessible only by those who can authenticate to the site.', verbose_name='Restricted access')),
                ('password', models.CharField(help_text='The video is available with the specified password.',
                                              max_length=50, null=True, verbose_name='password', blank=True)),
                ('channel', models.ManyToManyField(
                    to='pods.Channel', null=True, verbose_name='Channels', blank=True)),
                ('discipline', models.ManyToManyField(
                    to='pods.Discipline', verbose_name='Disciplines', blank=True)),
                ('owner', models.ForeignKey(
                    verbose_name='Owner', to=settings.AUTH_USER_MODEL)),
                ('tags', pods.models.MyTaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True,
                                                       help_text='Separate tags with spaces, enclose the tags consist of several words in quotation marks.', verbose_name='Tags')),
            ],
            options={
                'verbose_name': 'Video',
                'verbose_name_plural': 'Videos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Recorder',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(
                    unique=True, max_length=200, verbose_name='name')),
                ('adress_ip', models.IPAddressField(unique=True)),
                ('status', models.BooleanField(default=0)),
                ('slide', models.BooleanField(default=1)),
                ('gmapurl', models.CharField(
                    max_length=250, null=True, blank=True)),
                ('is_restricted', models.BooleanField(
                    default=False, help_text='Live is accessible only to authenticated users.', verbose_name='Restricted access')),
                ('building', models.ForeignKey(
                    verbose_name='Building', to='pods.Building')),
                ('image', filer.fields.image.FilerImageField(related_name='recorder_image',
                                                             verbose_name='Image', blank=True, to='filer.Image', null=True)),
            ],
            options={
                'verbose_name': 'Recorder',
                'verbose_name_plural': 'Recorders',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(
                    unique=True, max_length=100, verbose_name='Title')),
                ('slug', models.SlugField(help_text='Used to access this instance, the "slug" is a short label containing only letters, numbers, underscore or dash top.',
                                          unique=True, max_length=100, verbose_name='Slug')),
                ('description', models.TextField(null=True, blank=True)),
                ('channel', models.ForeignKey(
                    related_name='themes', verbose_name='Channel', to='pods.Channel')),
                ('headband', filer.fields.image.FilerImageField(
                    verbose_name='Headband', blank=True, to='filer.Image', null=True)),
            ],
            options={
                'ordering': ['title'],
                'verbose_name': 'Theme',
                'verbose_name_plural': 'Themes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrackPods',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('kind', models.CharField(default='subtitles', max_length=10, verbose_name='Kind', choices=[
                 ('subtitles', 'subtitles'), ('captions', 'captions')])),
                ('lang', models.CharField(max_length=2, verbose_name='Language', choices=[('', (('ar', 'Arabic'), ('zh', 'Chinese'), ('en', 'English'), ('fr', 'French'), ('de', 'German'), ('es', 'Spanish'))), ('-----------', (('ab', 'Abkhazian'), ('aa', 'Afar'), ('af', 'Afrikaans'), ('sq', 'Albanian'), ('am', 'Amharic'), ('ar', 'Arabic'), ('an', 'Aragonese'), ('hy', 'Armenian'), ('as', 'Assamese'), ('ay', 'Aymara'), ('az', 'Azerbaijani'), ('ba', 'Bashkir'), ('eu', 'Basque'), ('bn', 'Bengali (Bangla)'), ('dz', 'Bhutani'), ('bh', 'Bihari'), ('bi', 'Bislama'), ('br', 'Breton'), ('bg', 'Bulgarian'), ('my', 'Burmese'), ('be', 'Byelorussian (Belarusian)'), ('km', 'Cambodian'), ('ca', 'Catalan'), ('zh', 'Chinese'), ('co', 'Corsican'), ('hr', 'Croatian'), ('cs', 'Czech'), ('da', 'Danish'), ('nl', 'Dutch'), ('en', 'English'), ('eo', 'Esperanto'), ('et', 'Estonian'), ('fo', 'Faeroese'), ('fa', 'Farsi'), ('fj', 'Fiji'), ('fi', 'Finnish'), ('fr', 'French'), ('fy', 'Frisian'), ('gl', 'Galician'), ('gd', 'Gaelic (Scottish)'), ('gv', 'Gaelic (Manx)'), ('ka', 'Georgian'), ('de', 'German'), ('el', 'Greek'), ('kl', 'Greenlandic'), ('gn', 'Guarani'), ('gu', 'Gujarati'), ('ht', 'Haitian Creole'), ('ha', 'Hausa'), ('he', 'Hebrew'), ('hi', 'Hindi'), ('hu', 'Hungarian'), ('is', 'Icelandic'), ('io', 'Ido'), ('id', 'Indonesian'), ('ia', 'Interlingua'), ('ie', 'Interlingue'), ('iu', 'Inuktitut'), ('ik', 'Inupiak'), ('ga', 'Irish'), ('it', 'Italian'), ('ja', 'Japanese'), ('jv', 'Javanese'), ('kn', 'Kannada'), ('ks', 'Kashmiri'), ('kk', 'Kazakh'), ('rw', 'Kinyarwanda (Ruanda)'), (
                    'ky', 'Kirghiz'), ('rn', 'Kirundi (Rundi)'), ('ko', 'Korean'), ('ku', 'Kurdish'), ('lo', 'Laothian'), ('la', 'Latin'), ('lv', 'Latvian (Lettish)'), ('li', 'Limburgish ( Limburger)'), ('ln', 'Lingala'), ('lt', 'Lithuanian'), ('mk', 'Macedonian'), ('mg', 'Malagasy'), ('ms', 'Malay'), ('ml', 'Malayalam'), ('mt', 'Maltese'), ('mi', 'Maori'), ('mr', 'Marathi'), ('mo', 'Moldavian'), ('mn', 'Mongolian'), ('na', 'Nauru'), ('ne', 'Nepali'), ('no', 'Norwegian'), ('oc', 'Occitan'), ('or', 'Oriya'), ('om', 'Oromo (Afaan Oromo)'), ('ps', 'Pashto (Pushto)'), ('pl', 'Polish'), ('pt', 'Portuguese'), ('pa', 'Punjabi'), ('qu', 'Quechua'), ('rm', 'Rhaeto-Romance'), ('ro', 'Romanian'), ('ru', 'Russian'), ('sm', 'Samoan'), ('sg', 'Sangro'), ('sa', 'Sanskrit'), ('sr', 'Serbian'), ('sh', 'Serbo-Croatian'), ('st', 'Sesotho'), ('tn', 'Setswana'), ('sn', 'Shona'), ('ii', 'Sichuan Yi'), ('sd', 'Sindhi'), ('si', 'Sinhalese'), ('ss', 'Siswati'), ('sk', 'Slovak'), ('sl', 'Slovenian'), ('so', 'Somali'), ('es', 'Spanish'), ('su', 'Sundanese'), ('sw', 'Swahili (Kiswahili)'), ('sv', 'Swedish'), ('tl', 'Tagalog'), ('tg', 'Tajik'), ('ta', 'Tamil'), ('tt', 'Tatar'), ('te', 'Telugu'), ('th', 'Thai'), ('bo', 'Tibetan'), ('ti', 'Tigrinya'), ('to', 'Tonga'), ('ts', 'Tsonga'), ('tr', 'Turkish'), ('tk', 'Turkmen'), ('tw', 'Twi'), ('ug', 'Uighur'), ('uk', 'Ukrainian'), ('ur', 'Urdu'), ('uz', 'Uzbek'), ('vi', 'Vietnamese'), ('vo', 'Volap\xfck'), ('wa', 'Wallon'), ('cy', 'Welsh'), ('wo', 'Wolof'), ('xh', 'Xhosa'), ('yi', 'Yiddish'), ('yo', 'Yoruba'), ('zu', 'Zulu')))])),
                ('src', filer.fields.file.FilerFileField(
                    verbose_name='sub-heading file', blank=True, to='filer.File', null=True)),
                ('video', models.ForeignKey(
                    verbose_name='video', to='pods.Pod')),
            ],
            options={
                'verbose_name': 'Track Pod',
                'verbose_name_plural': 'Tracks Pod',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(
                    unique=True, max_length=100, verbose_name='Title')),
                ('title_fr', models.CharField(
                    max_length=100, unique=True, null=True, verbose_name='Title')),
                ('title_en', models.CharField(
                    max_length=100, unique=True, null=True, verbose_name='Title')),
                ('slug', models.SlugField(help_text='Used to access this instance, the "slug" is a short label containing only letters, numbers, underscore or dash top.',
                                          unique=True, max_length=100, verbose_name='Slug')),
                ('description', models.TextField(null=True, blank=True)),
                ('headband', filer.fields.image.FilerImageField(
                    verbose_name='Headband', blank=True, to='filer.Image', null=True)),
            ],
            options={
                'ordering': ['title'],
                'verbose_name': 'Type',
                'verbose_name_plural': 'Types',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='pod',
            name='theme',
            field=models.ManyToManyField(
                to='pods.Theme', null=True, verbose_name='Themes', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pod',
            name='thumbnail',
            field=filer.fields.image.FilerImageField(
                verbose_name='Thumbnail', blank=True, to='filer.Image', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pod',
            name='type',
            field=models.ForeignKey(verbose_name='Type', to='pods.Type'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notes',
            name='video',
            field=models.ForeignKey(to='pods.Pod'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='favorites',
            name='video',
            field=models.ForeignKey(to='pods.Pod'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='enrichpods',
            name='video',
            field=models.ForeignKey(verbose_name='video', to='pods.Pod'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='encodingpods',
            name='video',
            field=models.ForeignKey(verbose_name='Video', to='pods.Pod'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='docpods',
            name='video',
            field=models.ForeignKey(verbose_name='Video', to='pods.Pod'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contributorpods',
            name='video',
            field=models.ForeignKey(verbose_name='video', to='pods.Pod'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='chapterpods',
            name='video',
            field=models.ForeignKey(verbose_name='video', to='pods.Pod'),
            preserve_default=True,
        ),
    ]
