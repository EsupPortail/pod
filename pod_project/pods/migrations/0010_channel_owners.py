# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


def move_channel_owners_data(apps, schema_editor):

    Channel = apps.get_model('pods', 'Channel')

    for channel in Channel.objects.all():
        channel.owners.add(channel.owner)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pods', '0009_auto_20160708_1552'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='owners',
            field=models.ManyToManyField(
                related_name='owners_channels',
                verbose_name='Owners',
                to=settings.AUTH_USER_MODEL,
                blank=True
            ),
        ),
        migrations.RunPython(move_channel_owners_data),
        migrations.RemoveField(
            model_name='channel',
            name='owner',
        ),
    ]
