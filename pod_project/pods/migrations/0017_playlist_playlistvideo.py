# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pods', '0016_overlaypods'),
    ]

    operations = [
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(unique=True, max_length=100, verbose_name='Title')),
                ('slug', models.SlugField(help_text='Used to access this instance, the "slug" is a short label containing only letters, numbers, underscore or dash top.', unique=True, max_length=100, verbose_name='Slug')),
                ('description', ckeditor.fields.RichTextField(verbose_name='Description', blank=True)),
                ('visible', models.BooleanField(default=False, help_text="If checked, the playlist page becomes accessible from the user's card", verbose_name='Visible')),
                ('owner', models.ForeignKey(related_name='playlist_owner', verbose_name='Owner', blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['title'],
                'verbose_name': 'Playlist',
                'verbose_name_plural': 'Playlists',
            },
        ),
        migrations.CreateModel(
            name='PlaylistVideo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.PositiveSmallIntegerField(default=0, help_text='Position of the video in a playlist.', verbose_name='Position')),
                ('playlist', models.ForeignKey(verbose_name='playlist', to='pods.Playlist')),
                ('video', models.ForeignKey(verbose_name='video', to='pods.Pod')),
            ],
            options={
                'ordering': ['position'],
            },
        ),
    ]
