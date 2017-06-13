# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('pods', '0014_rssfeed'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pod',
            options={'ordering': ['-date_added', '-id'], 'get_latest_by': 'date_added', 'verbose_name': 'video', 'verbose_name_plural': 'videos'},
        ),
        migrations.AlterField(
            model_name='mediacourses',
            name='date_added',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='date added', editable=False),
        ),
        migrations.AlterField(
            model_name='reportvideo',
            name='date_added',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date', editable=False),
        ),
    ]
