# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pods', '0004_AlterFields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pod',
            name='is_draft',
            field=models.BooleanField(default=True, help_text='If this box is checked, the video will be visible and accessible only by you.', verbose_name='Draft'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pod',
            name='is_restricted',
            field=models.BooleanField(default=False, help_text='If this box is checked, the video will only be accessible to authenticated users.', verbose_name='Restricted access'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pod',
            name='password',
            field=models.CharField(help_text='Viewing this video will not be possible without this password.', max_length=50, null=True, verbose_name='password', blank=True),
            preserve_default=True,
        ),
    ]
