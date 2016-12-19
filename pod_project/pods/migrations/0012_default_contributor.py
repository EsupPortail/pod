# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pods', '0011_new_contributorpod'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contributorpods',
            name='role',
            field=models.CharField(default='author', max_length=200, verbose_name='role', choices=[('actor', 'actor'), ('author', 'author'), ('designer', 'designer'), ('consultant', 'consultant'), ('contributor', 'contributor'), ('editor', 'editor'), ('speaker', 'speaker'), ('soundman', 'soundman'), ('director', 'director'), ('writer', 'writer'), ('technician', 'technician'), ('voice-over', 'voice-over')]),
        ),
    ]
