# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pods', '0003_reportvideo'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportvideo',
            name='answer',
            field=models.TextField(null=True, verbose_name='Answer', blank=True),
            preserve_default=True,
        ),
    ]
