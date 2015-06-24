# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('pods', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enrichpods',
            name='end',
            field=models.PositiveIntegerField(default=1, help_text='End displaying enrichment in seconds', verbose_name='End'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='enrichpods',
            name='start',
            field=models.PositiveIntegerField(default=0, help_text='Start displaying enrichment in seconds', verbose_name='Start'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pod',
            name='date_added',
            field=models.DateField(default=datetime.datetime.now, verbose_name='Date added'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pod',
            name='date_evt',
            field=models.DateField(default=datetime.datetime.now, null=True, verbose_name='Date of event', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pod',
            name='is_restricted',
            field=models.BooleanField(default=False, help_text='The video is accessible only by those who are enabled to authenticate.', verbose_name='Restricted access'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contributorpods',
            name='role',
            field=models.CharField(default='authors', choices=[('author', 'author'), ('director', 'director'), ('editor', 'editor'), ('designer', 'designer'), ('contributor', 'contributor'), ('actor', 'actor'), ('voice-over', 'voice-off'), ('consultant', 'consultant'), ('writer', 'writer'), ('soundman', 'soundman'), ('technician', 'technician')], max_length=200, blank=True, null=True, verbose_name='role'),
            preserve_default=True,
        ),
    ]
