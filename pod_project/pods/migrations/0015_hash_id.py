# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.template.defaultfilters import slugify
import base64

def create_hash_if_exist(apps, schema_editor):
    from pods.models import *
    # Videos = Pod.objects.filter(pod__is_draft=True)
    Videos = Pod.objects.filter(is_draft=True)
    # Check if we have videos before this migration
    if len(Videos) > 0:
        # Create hash_id
        for video in Videos:
            if video.is_draft:
                newid = video.id
                newid = '%04d' % newid
                idToEncode = ''.join([str(newid), video.title])
                encodeId = base64.b64encode(idToEncode.encode('utf-8'))
                video.hash_id = slugify(encodeId)
                video.save()

class Migration(migrations.Migration):

    dependencies = [
        ('pods', '0014_rssfeed'),
    ]

    operations = [
        migrations.AddField(
            model_name='pod',
            name='hash_id',
            field=models.CharField(default=None, max_length=100, blank=True, help_text='Hashcode to retrieve the video', null=True, verbose_name='hash_id'),
        ),
        migrations.RunPython(create_hash_if_exist),
    ]
