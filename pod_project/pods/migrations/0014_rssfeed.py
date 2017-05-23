# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pods', '0013_pod_is_360'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rssfeed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200, unique_for_year='date_update')),
                ('description', models.TextField()),
                ('link_rss', models.URLField()),
                ('type_rss', models.CharField(default='A', max_length=1, choices=[('A', 'Audio'), ('V', 'Vid\xe9o')])),
                ('year', models.PositiveSmallIntegerField(default=2017)),
                ('date_update', models.DateTimeField(auto_now=True)),
                ('filters', models.TextField(blank=True)),
                ('limit', models.SmallIntegerField(default=0, help_text='Keep 0 to mean all items', verbose_name='Count items')),
                ('is_up', models.BooleanField(default=True, help_text='If this box is checked, the video will be visible and accessible by anyone.', verbose_name='Visible')),
                ('fil_channel', models.ManyToManyField(to='pods.Channel', verbose_name='Channels', blank=True)),
                ('fil_discipline', models.ManyToManyField(to='pods.Discipline', verbose_name='Disciplines', blank=True)),
                ('fil_theme', models.ManyToManyField(to='pods.Theme', verbose_name='Themes', blank=True)),
                ('fil_type_pod', models.ForeignKey(verbose_name='Type', to='pods.Type')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=1, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'RSS',
                'verbose_name_plural': 'RSS',
            },
        ),
    ]
