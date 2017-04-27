# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
from celery import shared_task


@shared_task(bind=True)
def task_start_encode(self, video):
    print "START ENCODE VIDEO ID %s" % video.id
    from core.utils import encode_video
    encode_video(video)
