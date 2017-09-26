# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pods', '0015_auto_20170613_1640'),
    ]

    operations = [
        migrations.CreateModel(
            name='OverlayPods',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, verbose_name='title')),
                ('slug', models.SlugField(editable=False, max_length=105, help_text='Used to access this instance, the "slug" is a short label containing only letters, numbers, underscore or dash top.', unique=True, verbose_name='slug')),
                ('time_start', models.PositiveIntegerField(default=0, help_text='Start time of the overlay, in seconds.', verbose_name='Start time')),
                ('time_end', models.PositiveIntegerField(default=1, help_text='End time of the overlay, in seconds.', verbose_name='End time')),
                ('content', models.TextField(help_text='Content of the overlay', max_length=300, verbose_name='Content')),
                ('position', models.CharField(default='bottom-right', choices=[('top-left', 'top-left'), ('top', 'top'), ('top-right', 'top-right'), ('right', 'right'), ('bottom-right', 'bottom-right'), ('bottom', 'bottom'), ('bottom-left', 'bottom-left'), ('left', 'left')], max_length=100, help_text='Position of the overlay', null=True, verbose_name='Position')),
                ('background', models.BooleanField(default=True, help_text='Show the background of the overlay', verbose_name='Show background')),
                ('video', models.ForeignKey(verbose_name='video', to='pods.Pod')),
            ],
            options={
                'ordering': ['time_start'],
                'verbose_name': 'Overlay',
                'verbose_name_plural': 'Overlays',
            },
        ),
    ]
