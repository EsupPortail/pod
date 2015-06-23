# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pods', '0004_reportvideo_answer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contributorpods',
            name='role',
            field=models.CharField(default='authors', choices=[('author', 'author'), ('director', 'director'), ('editor', 'editor'), ('designer', 'designer'), ('contributor', 'contributor'), ('actor', 'actor'), ('voice-over', 'voice-off'), ('consultant', 'consultant'), ('writer', 'writer'), ('soundman', 'soundman'), ('technician', 'technician')], max_length=200, blank=True, null=True, verbose_name='role'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='reportvideo',
            unique_together=set([('video', 'user')]),
        ),
    ]
