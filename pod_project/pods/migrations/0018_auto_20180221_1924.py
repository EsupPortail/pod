# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pods', '0017_playlist_playlistvideo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='encodingpods',
            name='encodingFormat',
            field=models.CharField(default='video/mp4', max_length=22, verbose_name='Format', choices=[('video/mp4', 'video/mp4'), ('video/webm', 'video/webm'), ('audio/mp3', 'audio/mp3'), ('audio/wav', 'audio/wav'), ('application/x-mpegURL', 'application/x-mpegURL')]),
        ),
    ]
