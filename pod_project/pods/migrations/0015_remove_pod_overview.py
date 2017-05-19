# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pods', '0014_rssfeed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pod',
            name='overview',
        ),
    ]
