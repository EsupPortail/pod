# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import filer.fields.image


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactUs',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250, verbose_name='Name')),
                ('email', models.EmailField(max_length=250, verbose_name='Email')),
                ('subject', models.CharField(max_length=250, verbose_name='Subject')),
                ('message', models.TextField(verbose_name='Message')),
            ],
            options={
                'verbose_name': 'Contact',
                'verbose_name_plural': 'Contacts',
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='encodingtype',
            options={'verbose_name': 'encoding type', 'verbose_name_plural': 'encoding types'},
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='description',
            field=models.TextField(help_text='This field allows you to write a few words about yourself. The text will be displayed with your videos.', max_length=100, verbose_name='Description', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='image',
            field=filer.fields.image.FilerImageField(blank=True, to='filer.Image', help_text='This field allows you to add a photo ID. The picture will be displayed with your videos.', null=True, verbose_name='Avatar'),
            preserve_default=True,
        ),
    ]
