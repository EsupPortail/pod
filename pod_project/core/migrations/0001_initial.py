# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import filer.fields.file
import filer.fields.image
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('flatpages', '0002_auto_20150521_1550'),
        ('filer', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='EncodingType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250, verbose_name='name')),
                ('bitrate_audio', models.CharField(help_text='Please use the only format k: i.e.: <em>300k</em> or <em>600k</em> or <em>1000k</em>.', max_length=250, verbose_name='bitrate_audio')),
                ('bitrate_video', models.CharField(help_text='Please use the only format k. i.e.: <em>300k</em> or <em>600k</em> or <em>1000k</em>.', max_length=250, verbose_name='bitrate_video', blank=True)),
                ('output_height', models.IntegerField(default=240, max_length=4, verbose_name='output_height', choices=[(0, '0'), (240, '240'), (480, '480'), (640, '640'), (720, '720'), (1080, '1080')])),
                ('mediatype', models.CharField(default='video', max_length=5, verbose_name='mediatype', choices=[('audio', 'Audio'), ('video', 'Video')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FileBrowse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('document', filer.fields.file.FilerFileField(verbose_name='Fichier selectionn\xe9', blank=True, to='filer.File', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PagesMenuBas',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveSmallIntegerField(default=1, null=True, verbose_name='order', blank=True)),
                ('page', models.ForeignKey(to='flatpages.FlatPage')),
            ],
            options={
                'ordering': ['order', 'page__title'],
                'verbose_name': 'page bottom menu',
                'verbose_name_plural': 'pages bottom menu',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField(help_text='This field allows you to write a few words about yourself. The text will be displayed with yours videos.', max_length=100, verbose_name='Description', blank=True)),
                ('url', models.URLField(help_text='This field allows you to add an url.', verbose_name='Web link', blank=True)),
                ('auth_type', models.CharField(default='loc.', max_length=20)),
                ('affiliation', models.CharField(default='member', max_length=50)),
                ('commentaire', models.TextField(default='', verbose_name='Comment', blank=True)),
                ('image', filer.fields.image.FilerImageField(blank=True, to='filer.Image', help_text='This field allows you to add a photo ID. The picture will be displayed with yours videos.', null=True, verbose_name='Avatar')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('user',),
                'verbose_name': 'Profile',
                'verbose_name_plural': 'Profiles',
            },
            bases=(models.Model,),
        ),
    ]
