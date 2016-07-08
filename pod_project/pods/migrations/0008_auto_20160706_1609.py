# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('pods', '0007_auto_20151209_1519'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='users',
            field=models.ManyToManyField(related_name='users_channels', verbose_name='Users', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AlterField(
            model_name='contributorpods',
            name='email_address',
            field=models.EmailField(default='', max_length=254, null=True, verbose_name='mail', blank=True),
        ),
        migrations.AlterField(
            model_name='pod',
            name='channel',
            field=models.ManyToManyField(to='pods.Channel', verbose_name='Channels', blank=True),
        ),
        migrations.AlterField(
            model_name='pod',
            name='duration',
            field=models.IntegerField(default=0, verbose_name='Duration', editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='pod',
            name='theme',
            field=models.ManyToManyField(to='pods.Theme', verbose_name='Themes', blank=True),
        ),
        migrations.AlterField(
            model_name='recorder',
            name='adress_ip',
            field=models.GenericIPAddressField(unique=True),
        ),
    ]
