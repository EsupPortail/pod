# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pods', '0004_AlterFields'),
    ]

    operations = [
        migrations.AddField(
            model_name='recorder',
            name='description',
            field=ckeditor.fields.RichTextField(verbose_name='description', blank=True),
            preserve_default=True,
        ),
    ]
