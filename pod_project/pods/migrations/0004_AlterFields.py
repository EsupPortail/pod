# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import filer.fields.file


class Migration(migrations.Migration):

    dependencies = [
        ('pods', '0003_reportvideo'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='encodingpods',
            options={'verbose_name': 'encoding', 'verbose_name_plural': 'encodings'},
        ),
        migrations.AlterField(
            model_name='channel',
            name='visible',
            field=models.BooleanField(default=False, help_text='If checked, the channel appear in a list of available channels on the platform.', verbose_name='Visible'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='chapterpods',
            name='time',
            field=models.PositiveIntegerField(default=0, help_text='Start time of the chapter, in seconds.', verbose_name='Start time'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contributorpods',
            name='role',
            field=models.CharField(default='authors', max_length=200, verbose_name='role', choices=[('author', 'author'), ('director', 'director'), ('editor', 'editor'), ('designer', 'designer'), ('contributor', 'contributor'), ('actor', 'actor'), ('voice-over', 'voice-off'), ('consultant', 'consultant'), ('writer', 'writer'), ('soundman', 'soundman'), ('technician', 'technician')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pod',
            name='encoding_in_progress',
            field=models.BooleanField(default=False, verbose_name='Encoding in progress', editable=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pod',
            name='is_draft',
            field=models.BooleanField(default=True, help_text='If you check this box, the video will be visible and accessible only by you.', verbose_name='Draft'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pod',
            name='view_count',
            field=models.PositiveIntegerField(default=0, verbose_name='View count', editable=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='trackpods',
            name='src',
            field=filer.fields.file.FilerFileField(verbose_name='subtitle file', blank=True, to='filer.File', null=True),
            preserve_default=True,
        ),
    ]
