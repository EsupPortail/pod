# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20180222_1101'),
    ]

    operations = [
        migrations.AddField(
            model_name='encodingtype',
            name='support_hls',
            field=models.BooleanField(default=False),
        ),
    ]
