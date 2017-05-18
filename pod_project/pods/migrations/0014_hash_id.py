# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pods', '0013_pod_is_360'),
    ]

    operations = [
        migrations.AddField(
            model_name='pod',
            name='hash_id',
            field=models.CharField(default=None, max_length=100, blank=True, help_text='Hashcode to retrieve de video', null=True, verbose_name='hash_id'),
        ),
    ]
