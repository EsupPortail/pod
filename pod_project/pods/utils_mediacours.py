# -*- coding: utf-8 -*-
"""
Copyright (C) 2014 Nicolas Can
Ce programme est un logiciel libre : vous pouvez
le redistribuer et/ou le modifier sous les termes
de la licence GNU Public Licence telle que publiée
par la Free Software Foundation, soit dans la
version 3 de la licence, ou (selon votre choix)
toute version ultérieure. 
Ce programme est distribué avec l'espoir
qu'il sera utile, mais SANS AUCUNE
GARANTIE : sans même les garanties
implicites de VALEUR MARCHANDE ou
D'APPLICABILITÉ À UN BUT PRÉCIS. Voir
la licence GNU General Public License
pour plus de détails.
Vous devriez avoir reçu une copie de la licence
GNU General Public Licence
avec ce programme. Si ce n'est pas le cas,
voir http://www.gnu.org/licenses/
"""
from __future__ import unicode_literals
import datetime
import os
import sys
import zipfile
import traceback
import logging

from xml.dom import minidom

from django.template.defaultfilters import slugify
from django.core.files.base import ContentFile
from django.conf import settings

from filer.models.foldermodels import Folder
from filer.models.imagemodels import Image
from filer.models.filemodels import File as filerFile

from pods.models import Pod, Type, EnrichPods

FTP_ROOT_FOLDER = getattr(settings, "FTP_ROOT_FOLDER", "/audiovideocours/ftp")
DEFAULT_TYPE = getattr(settings, "DEFAULT_TYPE", "autres")
SKIP_FIRST_IMAGE = getattr(settings, "SKIP_FIRST_IMAGE", False)

log = logging.getLogger(__name__)


def process_mediacours(media):
    media.started = True
    media.error = 'Start at %s\n--\n' % datetime.datetime.now()
    media.save()

    if os.path.isfile("%s/%s" % (FTP_ROOT_FOLDER, media.mediapath)):
        mediaerror(media, "file found %s/%s" %
                   (FTP_ROOT_FOLDER, media.mediapath))
        process_mediazipfile(media)
    else:
        mediaerror(media, "Zip File Not Found...")
        media.save()
    mediaerror(media, "End at %s" % datetime.datetime.now())


def process_mediazipfile(media):
    zip = zipfile.ZipFile("%s/%s" % (FTP_ROOT_FOLDER, media.mediapath))
    media_name, ext = os.path.splitext(
        os.path.basename("%s/%s" % (FTP_ROOT_FOLDER, media.mediapath)))
    mediaerror(media, "> media name %s" % media_name)

    try:
        smil = zip.open(media_name + "/cours.smil")
        xmldoc = minidom.parse(smil)
        smil.close()

        # get audio ou video
        video_src = None
        if xmldoc.getElementsByTagName("audio"):
            video_src = xmldoc.getElementsByTagName(
                "audio").item(0).getAttribute("src")
        if xmldoc.getElementsByTagName("video"):
            video_src = xmldoc.getElementsByTagName(
                "video").item(0).getAttribute("src")

        if video_src:
            try:
                mediaerror(media, "> video file %s" % video_src)
                video_data = zip.read(media_name + "/%s" % video_src)
                pod = save_video(media, video_data, video_src)

                # IMG MANAGE
                list_node_img = xmldoc.getElementsByTagName("img")
                mediaerror(media, "> slides found %s" % len(list_node_img))
                if len(list_node_img):

                    # SLIDES FOLDER
                    rootFolder = Folder.objects.get(
                        name=pod.owner, owner=pod.owner, level=0)
                    videoFolder, created = Folder.objects.get_or_create(
                        name=pod.slug, owner=pod.owner, parent=rootFolder)
                    slideFolder, created = Folder.objects.get_or_create(
                        name="slides", owner=pod.owner, parent=videoFolder)

                    # Delete previous enrichment
                    EnrichPods.objects.filter(video=pod).delete()
                    i = 0
                    start_img = 1 if SKIP_FIRST_IMAGE else 0
                    for item in list_node_img[start_img:]:  # skip the first
                        i += 1
                        mediaerror(media, ">> ITEM %s: %s" %
                                   (i, item.getAttribute("src")))
                        filename = media_name + \
                            "/%s" % item.getAttribute("src")
                        timecode = float("%s" % item.getAttribute("begin"))
                        timecode = int(round(timecode))
                        mediaerror(media, ">> timecode %s" % timecode)
                        if timecode >= 0:

                            # Record the enrichment
                            ep, c = EnrichPods.objects.get_or_create(
                                video=pod, title="Record Slide %s" % i, start=timecode, end=timecode + 1)
                            try:
                                data = zip.read(filename)
                                if len(data):

                                    # Save the slide
                                    slide_name, ext = os.path.splitext(
                                        os.path.basename(filename))
                                    mediaerror(
                                        media, ">> slide_name %s" % slide_name)
                                    ext = ext.lower()
                                    upc_file, created = Image.objects.get_or_create(
                                        folder=slideFolder, name=slugify(pod.title + "_" + slide_name) + ext)
                                    upc_file.file.save(
                                        slugify(pod.title + "_" + slide_name) + ext, ContentFile(data), save=True)
                                    upc_file.owner = pod.owner
                                    upc_file.save()

                                    # attach slide to the enrichment
                                    ep.type = "image"
                                    ep.image = upc_file
                                    ep.save()
                                else:
                                    mediaerror(
                                        media, "file %s is empty" % filename)
                            except Exception as e:
                                msg = u'\n enrichment ***** Unexpected error :%r' % e
                                msg += '\n%s' % traceback.format_exc()
                                log.error(msg)
                                mediaerror(
                                    media, "%s\n-->No file found for %s" % (msg, filename))

                    # End for each slide
                    # Update the end time of each enrichment

                    enrich_set = EnrichPods.objects.filter(
                        video=pod).order_by("start")
                    enrich_iterator = enrich_set.iterator()
                    current_enrich = None
                    try:
                        current_enrich = next(enrich_iterator)
                    except StopIteration:
                        # No rows were found, so do nothing.
                        pass

                    while enrich_iterator:
                        try:
                            next_enrich = next(enrich_iterator)
                            if next_enrich.start - 1 > current_enrich.start:
                                current_enrich.end = next_enrich.start - 1
                            if current_enrich.end < current_enrich.start:
                                current_enrich.end = current_enrich.start
                            if pod.duration:
                                if current_enrich.end >= pod.duration:
                                    current_enrich.end = pod.duration - 1
                            current_enrich.save()
                            current_enrich = next_enrich
                        except Exception as e:
                            msg = u'\n iterator ***** Unexpected error :%r' % e
                            msg += '\n%s' % traceback.format_exc()
                            log.error(msg)
                            mediaerror(media, "%s\nBREAK" % (msg))
                            break

                    if pod.duration and pod.duration != 0 and current_enrich != None and current_enrich.start < pod.duration:
                        last_enrich = current_enrich
                        mediaerror(media, "last_enrich title : %s" %
                                   last_enrich.title)
                        last_enrich.end = pod.duration - 1
                        last_enrich.save()

                    # End update enrich end time
            except KeyError:  # end try video_src
                msg = u'\n key error ***** Unexpected error :%r' % e
                msg += '\n%s' % traceback.format_exc()
                log.error(msg)
                mediaerror(media, "%s\nBREAK" % (msg))
        else:
            mediaerror(media, 'No audio or video markup found')
    except Exception as e:
        msg = u'\n key error ***** Unexpected error :%r' % e
        msg += '\n%s' % traceback.format_exc()
        log.error(msg)
        mediaerror(media, "%s\nSmil file not found" % (msg))

    zip.close()
    mediaerror(media, 'End processing zip file')


def mediaerror(media, msg):
    media.error += msg + '\n--\n'
    media.save()


def save_video(media, video_data, video_src):
    pod = Pod()
    pod.owner = media.user
    pod.type = Type.objects.get(slug=DEFAULT_TYPE)
    nom, ext = os.path.splitext(video_src)
    ext = ext.lower()
    pod.video.save(
        "record_" + slugify(media.title) + ext, ContentFile(video_data), save=False)
    
    #on recupere le nom du fichier sur le serveur
    pod.title = media.title
    pod.to_encode = True
    pod.save()
    return pod
