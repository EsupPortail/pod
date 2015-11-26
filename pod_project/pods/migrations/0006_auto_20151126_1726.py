# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pods', '0005_recorder_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contributorpods',
            name='role',
            field=models.CharField(default='authors', max_length=200, verbose_name='role', choices=[('author', 'author'), ('director', 'director'), ('editor', 'editor'), ('designer', 'designer'), ('contributor', 'contributor'), ('actor', 'actor'), ('voice-over', 'voice-over'), ('consultant', 'consultant'), ('writer', 'writer'), ('soundman', 'soundman'), ('technician', 'technician')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pod',
            name='is_draft',
            field=models.BooleanField(default=True, help_text='If this box is checked, the video will be visible and accessible only by you.', verbose_name='Draft'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pod',
            name='is_restricted',
            field=models.BooleanField(default=False, help_text='If this box is checked, the video will only be accessible to authenticated users.', verbose_name='Restricted access'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pod',
            name='password',
            field=models.CharField(help_text='Viewing this video will not be possible without this password.', max_length=50, null=True, verbose_name='password', blank=True),
            preserve_default=True,
        ),
    ]
