# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pods', '0002_auto_20150622_1423'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportVideo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField(null=True, verbose_name='Comment', blank=True)),
                ('date_added', models.DateTimeField(default=datetime.datetime.now, verbose_name='Date', editable=False)),
                ('user', models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL)),
                ('video', models.ForeignKey(verbose_name='Video', to='pods.Pod')),
            ],
            options={
                'verbose_name': 'Report',
                'verbose_name_plural': 'Reports',
            },
            bases=(models.Model,),
        ),
    ]
