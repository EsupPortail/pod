# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_remove_south_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='encodingtype',
            name='output_height',
            field=models.IntegerField(default=360, verbose_name='output_height', choices=[(0, '0'), (240, '240'), (360, '360'), (480, '480'), (720, '720'), (1080, '1080')]),
        ),
    ]
