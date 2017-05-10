# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20160706_1609'),
    ]

    operations = [
        migrations.RunSQL("DROP TABLE IF EXISTS south_migrationhistory;")
    ]
