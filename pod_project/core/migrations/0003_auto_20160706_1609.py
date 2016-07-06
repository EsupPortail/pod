# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_ContactUs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='encodingtype',
            name='output_height',
            field=models.IntegerField(default=240, verbose_name='output_height', choices=[(0, '0'), (240, '240'), (480, '480'), (640, '640'), (720, '720'), (1080, '1080')]),
        ),
    ]
