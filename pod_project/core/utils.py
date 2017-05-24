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

import commands
import sys
import os
import subprocess
import re
import time
import json
import logging
import traceback
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.mail import EmailMultiAlternatives, send_mail
from core.models import EncodingType, get_media_guard
from pods.models import EncodingPods
from pods.models import Pod

from django.core.files.temp import NamedTemporaryFile
from django.core.files import File
from filer.models.foldermodels import Folder
from filer.models.imagemodels import Image

FFMPEG = getattr(settings, 'FFMPEG', 'ffmpeg')
FFPROBE = getattr(settings, 'FFPROBE', 'ffprobe')
DEFAULT_THUMBNAIL_OUT_SIZE_HEIGHT = 480
VIDEOS_DIR = getattr(settings, 'VIDEOS_DIR', 'videos')
DEFAULT_OVERVIEW_OUT_SIZE_HEIGHT = 64
DEBUG = getattr(settings, 'DEBUG', True)
ENCODE_WEBM = getattr(settings, 'ENCODE_WEBM', True)
ENCODE_WAV = getattr(settings, 'ENCODE_WAV', True)

ENCODE_VIDEO_CMD = getattr(settings, 'ENCODE_VIDEO_CMD',
                           "%(ffprobe)s -v quiet -show_format -show_streams -print_format json -i %(src)s")
ADD_THUMBNAILS_CMD = getattr(settings, 'ADD_THUMBNAILS_CMD',
                             "%(ffmpeg)s -i \"%(src)s\" -vf fps=\"fps=1/%(thumbnail)s,scale=%(scale)s\" -an -vsync 0 -threads 0 -f image2 -y %(out)s_%(num)s.png")
ADD_OVERVIEW_CMD = getattr(settings, 'ADD_OVERVIEW_CMD',
                           "%(ffmpeg)s -i \"%(src)s\" -vf \"thumbnail=%(thumbnail)s,scale=%(scale)s,tile=100x1:nb_frames=100:padding=0:margin=0\" -an -vsync 0 -threads 0 -y %(out)s")
ENCODE_MP4_CMD = getattr(settings, 'ENCODE_MP4_CMD', "%(ffmpeg)s -i %(src)s -codec:v libx264 -profile:v high -pix_fmt yuv420p -preset faster -b:v %(bv)s -maxrate %(bv)s -bufsize %(bufsize)s -vf scale=%(scale)s -force_key_frames \"expr:gte(t,n_forced*1)\" -deinterlace -threads 0 -codec:a aac -strict -2 -ar %(ar)s -ac 2 -b:a %(ba)s -movflags faststart -y %(out)s")
ENCODE_WEBM_CMD = getattr(settings, 'ENCODE_WEBM_CMD',
                          "%(ffmpeg)s -i %(src)s -codec:v libvpx -quality realtime -cpu-used 3 -b:v %(bv)s -maxrate %(bv)s -bufsize %(bufsize)s -qmin 10 -qmax 42 -threads 4 -codec:a libvorbis -y %(out)s")
ENCODE_MP3_CMD = getattr(settings, 'ENCODE_MP3_CMD',
                         "%(ffmpeg)s -i %(src)s -vn -ar %(ar)s -ab %(ab)s -f mp3 -threads 0 -y %(out)s")
ENCODE_WAV_CMD = getattr(settings, 'ENCODE_WAV_CMD',
                         "%(ffmpeg)s -i %(src)s -ar %(ar)s -ab %(ab)s -f wav -threads 0 -y %(out)s")

log = logging.getLogger(__name__)


def encode_video(video_to_encode):
    VIDEO_ID = video_to_encode.id
    start = "Start at : %s" % time.ctime()
    if DEBUG:
        print start
    video_to_encode.encoding_status = "Start encode"
    video_to_encode.infoVideo = "%s" % start
    video_to_encode.save()

    if os.path.exists(video_to_encode.video.path):
        # DELETE PREVIOUS ENCODING
        # EncodingPods.objects.filter(video=video).delete()
        previous_encoding = EncodingPods.objects.filter(video=video_to_encode)
        if len(previous_encoding) > 0:
            if DEBUG:
                print "DELETE PREVIOUS ENCODING"
            video_to_encode.infoVideo += "DELETE PREVIOUS ENCODING"
            previous_encoding.delete()
            video_to_encode.save()

        if DEBUG:
            print "get video data"
        # GET VIDEO DATA
        command = ENCODE_VIDEO_CMD % {  # add -count_frames to get nb_read_frames but it's quite long
            'ffprobe': FFPROBE,
            'src': video_to_encode.video.path,
        }
        if DEBUG:
            print "%s" % command
        ffproberesult = commands.getoutput(command)
        info = json.loads(ffproberesult)
        # print info['streams'][1]['codec_long_name'],
        # info['streams'][1]['duration']
        addInfoVideo(video_to_encode, unicode(json.dumps(
            info, sort_keys=True, indent=4, separators=(',', ': ')), errors='ignore'))
        # DURATION
        video_to_encode.encoding_status = "Get duration"
        video_to_encode.save()
        duration = None
        try:
            duration = float("%s" % info["format"]['duration'])
            video_to_encode.duration = int(duration)
            video_to_encode.save()
        except Exception as e:
            msg = u'\n NO DURATION ***** Unexpected error :%r' % e
            msg += '\n%s' % traceback.format_exc()
            log.error(msg)
            addInfoVideo(video_to_encode, msg)
            send_email(msg, video_to_encode)
            return
        # PARSE STREAMS
        is_video = False
        in_width = 0
        in_height = 0
        in_rotation = 0
        nb_frames = 0
        in_audio_rate = 44100
        in_audio_bitrate = 128
        for stream in info["streams"]:
            if stream.get("codec_type"):
                if stream["codec_type"] == "video":
                    is_video = True
                    # Rotation
                    try:
                        if stream.get("side_data_list"):
                            in_rotation = int(stream.get(
                                "side_data_list")[0]["rotation"])
                            if in_rotation == 270:
                                in_rotation = -90
                    except Exception:
                        pass
                    # Dimensions
                    try:
                        video_to_encode.encoding_status = "GET WIDTH AND HEIGHT"
                        video_to_encode.save()
                        if abs(in_rotation) == 90:
                            in_width = int(stream["height"])
                            in_height = int(stream["width"])
                        else:
                            in_width = int(stream["width"])
                            in_height = int(stream["height"])
                        addInfoVideo(video_to_encode, unicode(
                            "\n Width : %s - Height : %s" % (in_width, in_height), errors='ignore'))
                    except Exception as e:
                        msg = u'\n VIDEO WITHOUT WIDTH AND HEIGHT ***** Unexpected error :%r' % e
                        msg += '\n%s' % traceback.format_exc()
                        log.error(msg)
                        addInfoVideo(video_to_encode, msg)
                        send_email(msg, video_to_encode)
                        return
                    # CALC FRAMES with frame rate and duration
                    try:
                        video_to_encode.encoding_status = "GET NB FRAMES"
                        video_to_encode.save()
                        if stream.get("nb_frames"):
                            nb_frames = int(stream.get("nb_frames"))
                        else:
                            in_frame_rate = eval(stream["r_frame_rate"])
                            nb_frames = int(
                                round(duration * float(in_frame_rate)))
                        addInfoVideo(
                            video_to_encode, unicode("\n Nb frames %s" % (nb_frames), errors='ignore'))
                    except Exception as e:
                        msg = u'\n***** ERROR NB FRAMES Unexpected error :%r' % e
                        msg += '\n%s' % traceback.format_exc()
                        log.error(msg)
                        addInfoVideo(video_to_encode, msg)
                        send_email(msg, video_to_encode)
                        return
                    # SAR sample_aspect_ratio
                    if stream.get("sample_aspect_ratio"):
                        try:
                            video_to_encode.encoding_status = "GET SAR"
                            video_to_encode.save()
                            sar_w, sar_h = [
                                int(__) for __ in stream.get("sample_aspect_ratio").split(':')]
                            sar = 1
                            if sar_w != 0 and sar_h != 0:
                                sar = (1. * sar_w / sar_h)
                            in_width = int(1. * in_width * sar)
                            addInfoVideo(
                                video_to_encode, "\n IN_WIDTH %s" % (in_width))
                        except Exception as e:
                            msg = u'\nERROR CALC SAR ***** Unexpected error :%r' % e
                            msg += '\n%s' % traceback.format_exc()
                            log.error(msg)
                            addInfoVideo(video_to_encode, msg)
                            send_email(msg, video_to_encode)
                            return
                    # Fin stream video
                if stream["codec_type"] == "audio":
                    if stream.get("sample_rate"):
                        video_to_encode.encoding_status = "GET AUDIO SAMPLE RATE"
                        video_to_encode.save()
                        try:
                            in_audio_rate = int(stream.get("sample_rate"))
                        except:
                            video_to_encode.infoVideo += "\n ERROR GET AUDIO SAMPLE RATE"
                            video_to_encode.save()
                    if stream.get("bit_rate"):
                        video_to_encode.encoding_status = "GET AUDIO BIT RATE"
                        video_to_encode.save()
                        try:
                            in_audio_bitrate = int(
                                int(stream.get("bit_rate")) / 1000)
                        except:
                            video_to_encode.infoVideo += "\n ERROR GET AUDIO BIT RATE"
                            video_to_encode.save()
                    # Fin stream audio
            else:
                video_to_encode.encoding_status = "NO CODEC TYPE FOUND"
                video_to_encode.save()
                msg = u'\nNO CODEC TYPE FOUND'
                log.error(msg)
                addInfoVideo(video_to_encode, msg)
                send_email(msg, video_to_encode)
                return
        # FIN PARSE STREAMS
        if DEBUG:
            print "FIN PARSE STREAMS"
        # VIDEO/AUDIO FOLDER
        if DEBUG:
            print "VIDEO/AUDIO FOLDER"
        media_guard_hash = get_media_guard(
            video_to_encode.owner.username, video_to_encode.id)
        if not(
            os.access(
                os.path.join(settings.MEDIA_ROOT, VIDEOS_DIR, video_to_encode.owner.username, media_guard_hash, "%s" % video_to_encode.id), os.F_OK)):
            os.makedirs(os.path.join(settings.MEDIA_ROOT, VIDEOS_DIR,
                                     video_to_encode.owner.username, media_guard_hash, "%s" % video_to_encode.id))
        if DEBUG:
            print "END VIDEO/AUDIO FOLDER"
        # FILER FOLDER
        if DEBUG:
            print "FILER FOLDER"
        rootFolder = Folder.objects.get(
            name=video_to_encode.owner, owner=video_to_encode.owner, level=0)
        folder, created = Folder.objects.get_or_create(
            name=video_to_encode.slug, owner=video_to_encode.owner, parent=rootFolder)
        if DEBUG:
            print "END FILER FOLDER"
        # FOR VIDEO
        if is_video:
            # MAKE THUMBNAILS
            if int(video_to_encode.duration) > 3:
                add_thumbnails(VIDEO_ID, in_width, in_height, folder)
            # MAKE OVERVIEW
            if nb_frames > 100:
                add_overview(VIDEO_ID, in_width, in_height, nb_frames)

            list_encod_video = EncodingType.objects.filter(mediatype='video').order_by(
                'output_height')  # .exclude(output_height=1080).exclude(output_height=720).exclude(output_height=480)
            for encod_video in list_encod_video:
                bufsize = encod_video.bitrate_video
                try:
                    int_bufsize = int(
                        re.search("(\d+)k", bufsize, re.I).groups()[0])
                    bufsize = "%sk" % (int_bufsize * 2)
                except:
                    pass
                if in_height >= encod_video.output_height or encod_video == list_encod_video.first():
                    video = Pod.objects.get(id=VIDEO_ID)
                    media_guard_hash = get_media_guard(
                        video.owner.username, video.id)
                    videofilename = os.path.join(settings.MEDIA_ROOT, VIDEOS_DIR, video.owner.username, media_guard_hash, "%s" % video.id,
                                                 "video_%s_%s.mp4" % (video.id, encod_video.output_height))
                    videourl = os.path.join(VIDEOS_DIR, video.owner.username, media_guard_hash, "%s" % video.id,
                                            "video_%s_%s.mp4" % (video.id, encod_video.output_height))
                    encode_mp4(VIDEO_ID, in_width, in_height, bufsize,
                               in_audio_rate, encod_video, videofilename, videourl)
                    if ENCODE_WEBM and os.access(videofilename, os.F_OK):
                        encode_webm(VIDEO_ID, videofilename,
                                    encod_video, bufsize)
        else:
            list_encod_audio = EncodingType.objects.filter(mediatype='audio')
            for encod_audio in list_encod_audio:
                video = Pod.objects.get(id=VIDEO_ID)
                media_guard_hash = get_media_guard(
                    video.owner.username, video.id)
                audiofilename = os.path.join(settings.MEDIA_ROOT, VIDEOS_DIR, video.owner.username, media_guard_hash, "%s" % video.id,
                                             "audio_%s_%s.mp3" % (video.id, encod_audio.output_height))
                audiourl = os.path.join(VIDEOS_DIR, video.owner.username, media_guard_hash, "%s" % video.id,
                                        "audio_%s_%s.mp3" % (video.id, encod_audio.output_height))
                encode_mp3(
                    VIDEO_ID, audiofilename, audiourl, encod_audio, in_audio_rate)
                if ENCODE_WAV and os.access(audiofilename, os.F_OK):
                    encode_wav(VIDEO_ID, audiofilename,
                               in_audio_rate, encod_audio)
        video = None
        video = Pod.objects.get(id=VIDEO_ID)
        video.encoding_status = "DONE at %s" % time.ctime()
        video.save()

    else:
        video = None
        video = Pod.objects.get(id=VIDEO_ID)
        if video.infoVideo is None:
            video.infoVideo = ""
        video.infoVideo += "\n!!! Video file not found !!!"
        video.save()
        send_email("\n!!! Video file not found !!!", video)

    end = "\nEnd : %s" % time.ctime()
    if DEBUG:
        print end
    video = None
    video = Pod.objects.get(id=VIDEO_ID)
    if video.infoVideo is None:
        video.infoVideo = ""
    video.infoVideo += end
    video.encoding_in_progress = False
    video.save()

    encoding_user_email_data = video_to_encode.get_encoding_user_email_data()
    if encoding_user_email_data and video.encoding_status.startswith("DONE"):
        from django.utils.translation import override
        content_url = "%s/video/%s/" % (
            encoding_user_email_data['root_url'], video.slug)
        list_url = "%s/owner_videos_list/" % encoding_user_email_data['root_url']
        with override(encoding_user_email_data['curr_lang']):
            send_mail(
                "[%s] %s" % (
                    settings.TITLE_SITE,
                    _(u"Encoding #%(content_id)s completed") % {
                        'content_id': VIDEO_ID
                    }
                ),
                "%s\n\n%s\n%s\n%s" % (
                    _(u"The content “%(content_title)s” has been encoded to Web formats, and is now available on %(site_title)s.") % {
                        'content_title': video.title,
                        'site_title': settings.TITLE_SITE
                    },
                    _(u"You will find it here:"),
                    content_url,
                    _(u"and in your content list: %(content_list)s.") % {
                        'content_list': list_url
                    }
                ),
                settings.DEFAULT_FROM_EMAIL,
                [encoding_user_email_data['user_email']],
                html_message='<p>%s</p><p>%s<br><a href="%s"><i>%s</i></a>\
                        <br>%s</p>' % (
                    _(u"The content “%(content_title)s” has been encoded to Web formats, and is now available on %(site_title)s.") % {
                        'content_title': '<b>%s</b>' % video.title,
                        'site_title': settings.TITLE_SITE
                    },
                    _(u"You will find it here:"),
                    content_url,
                    content_url,
                    _(u"and in %(your_content_list)s.") % {
                        'your_content_list': '<a href="%s">%s</a>' % (
                            list_url,
                            _(u"your content list")
                        )
                    }
                )
            )

# end encode_video(video):


def get_scale(in_w, in_h, out_h):
    new_width = (1. * in_w * out_h / in_h)
    if int(new_width) % 2 != 0:
        new_width = new_width + 1
    return "%s:%s" % (int(new_width), int(out_h))


def send_email(msg, video):
    admin_emails = [v for k, v in settings.ADMINS]
    email_msg = EmailMultiAlternatives("[" + settings.TITLE_SITE + "] Error Encoding",
                                       "Error Encoding  video id : %s\n%s" % (video.id, msg), settings.DEFAULT_FROM_EMAIL, admin_emails)
    email_msg.attach_alternative(
        "<p>Error Encoding video id : %s</p><p>%s</p>" % (video.id, msg.replace('\n', "<br/>")), "text/html")
    email_msg.send(fail_silently=False)
    return


def addInfoVideo(video, msg):
    try:
        if video.infoVideo is None:
            video.infoVideo = ""
        video.infoVideo += "\n%s" % msg
        video.save()
    except Exception as e:
        msg = u'\nError in adding info video ***** Unexpected error :%r' % e
        msg += '\n%s' % traceback.format_exc()
        log.error(msg)
        addInfoVideo(video, msg)
        send_email(msg, video)


# DEF THUMBNAILS
def add_thumbnails(video_id, in_w, in_h, folder):
    if DEBUG:
        print "ADD THUMBNAILS"
    video = Pod.objects.get(id=video_id)
    video.encoding_status = "ADD THUMBNAILS"
    video.save()
    tempfile = NamedTemporaryFile(dir=settings.FILE_UPLOAD_TEMP_DIR)
    media_guard_hash = get_media_guard(video.owner.username, video.id)
    scale = get_scale(in_w, in_h, DEFAULT_THUMBNAIL_OUT_SIZE_HEIGHT)
    thumbnails = int(video.duration / 3)
    com = ADD_THUMBNAILS_CMD % {
        'ffmpeg': FFMPEG,
        'src': video.video.path,
        'thumbnail': thumbnails,
        'scale': scale,
        'out': tempfile.name,
        'num': "%d"
    }
    if DEBUG:
        print "%s" % com
    thumbresult = commands.getoutput(com)
    output = "\n\nTHUMBNAILS"
    output += 80 * "~"
    output += "\n"
    output += thumbresult
    output += "\n"
    output += 80 * "~"

    f = open(os.path.join(settings.MEDIA_ROOT, VIDEOS_DIR,
                          video.owner.username, media_guard_hash, "%s" % video.id, "encode.log"), 'w')
    f.write(output)
    output = ""
    f.close()

    video = None
    video = Pod.objects.get(id=video_id)
    for i in range(2, 5):
        if os.access("%s_%s.png" % (tempfile.name, i), os.F_OK):
            if DEBUG:
                print "THUMBNAILS %s" % i
            upc_image, created = Image.objects.get_or_create(
                folder=folder, name="%d_%s.png" % (video.id, i))
            upc_image.file.save("%d_%s.png" % (video.id, i), File(
                open("%s_%s.png" % (tempfile.name, i))), save=True)
            upc_image.owner = video.owner
            upc_image.save()
            try:
                os.remove("%s_%s.png" % (tempfile.name, i))
            except:
                pass
            if i == 2:
                video.thumbnail = upc_image
        else:
            msg = "\n [add_thumbnails] error accessing %s_%s.png" % (
                tempfile.name, i)
            log.error(msg)
            addInfoVideo(video, msg)
            send_email(msg, video)
    video.save()
    try:
        os.remove("%s_1.png" % (tempfile.name))
        os.remove("%s_5.png" % (tempfile.name))
    except:
        pass


def add_overview(video_id, in_w, in_h, frames):
    if DEBUG:
        print "OVERVIEW"
    video = Pod.objects.get(id=video_id)
    thumbnails = int(frames / 100)
    scale = get_scale(in_w, in_h, DEFAULT_OVERVIEW_OUT_SIZE_HEIGHT)
    media_guard_hash = get_media_guard(video.owner.username, video.id)
    overviewfilename = os.path.join(
        settings.MEDIA_ROOT, VIDEOS_DIR, video.owner.username, media_guard_hash, "%s" % video.id, "overview.jpg")
    overviewurl = os.path.join(
        VIDEOS_DIR, video.owner.username, media_guard_hash, "%s" % video.id, "overview.jpg")

    com = ADD_OVERVIEW_CMD % {
        'ffmpeg': FFMPEG,
        'src': video.video.path,
        'thumbnail': thumbnails,
        'scale': scale,
        'out': overviewfilename
    }
    if DEBUG:
        print "%s" % com
    overviewresult = commands.getoutput(com)
    output = "\n\nOVERVIEW"
    output += 80 * "~"
    output += "\n"
    output += overviewresult
    output += "\n"
    output += 80 * "~"

    if os.access(overviewfilename, os.F_OK):  # outfile exists
        # There was a error cause the outfile size is zero
        if (os.stat(overviewfilename).st_size == 0):
            # We remove the file so that it does not cause confusion
            msg = "\n [add_overview] ERROR : Output size is 0"
            output += msg
            log.error(msg)
            video = Pod.objects.get(id=video_id)
            addInfoVideo(video, msg)
            send_email(msg, video)
            os.remove(overviewfilename)
        else:
            # there does not seem to be errors, follow the rest of the
            # procedures
            if DEBUG:
                print "OVERVIEW : %s" % overviewurl
            video = None
            video = Pod.objects.get(id=video_id)
            video.overview = overviewurl
            video.save()

    f = open(os.path.join(settings.MEDIA_ROOT, VIDEOS_DIR,
                          video.owner.username, media_guard_hash, "%s" % video.id, "encode.log"), 'a+b')
    f.write(output)
    output = ""
    f.close()


def encode_mp4(video_id, in_w, in_h, bufsize, in_ar, encod_video, videofilename, videourl):
    if DEBUG:
        print "ENCODING MP4 %s" % encod_video.output_height

    scale = get_scale(in_w, in_h, encod_video.output_height)

    video = None
    video = Pod.objects.get(id=video_id)
    video.encoding_status = "ENCODING MP4 %s" % encod_video.output_height
    addInfoVideo(video, "\nSTART ENCOD_VIDEO MP4 %s - %s - %s - %s" %
                 (encod_video.output_height, bufsize, scale, time.ctime()))
    video.save()
    #video.infoVideo +=  "\nSTART ENCOD_VIDEO MP4 %s - %s - %s - %s" %(encod_video.output_height, bufsize, scale, time.ctime())

    com = ENCODE_MP4_CMD % {
        'ffmpeg': FFMPEG,
        'src': video.video.path,
        'bv': encod_video.bitrate_video,
        'bufsize': bufsize,
        'scale': scale,
        'ar': in_ar,
        'ba': encod_video.bitrate_audio,
        'out': videofilename
    }
    if DEBUG:
        print "%s" % com
    ffmpegresult = commands.getoutput(com)
    video = None
    video = Pod.objects.get(id=video_id)
    media_guard_hash = get_media_guard(video.owner.username, video.id)
    addInfoVideo(video, "\n END ENCOD_VIDEO MP4 %s %s" %
                 (encod_video.output_height, time.ctime()))

    output = "\n\n ENCOD_VIDEO MP4 %s \n" % encod_video.output_height
    output += 80 * "~"
    output += "\n"
    output += ffmpegresult

    if DEBUG:
        print "END ENCOD_VIDEO MP4 %s %s" % (encod_video.output_height, time.ctime())

    if os.access(videofilename, os.F_OK):  # outfile exists
        # There was a error cause the outfile size is zero
        if (os.stat(videofilename).st_size == 0):
            # We remove the file so that it does not cause confusion
            os.remove(videofilename)
            msg = "ERROR ENCODING MP4 %s Output size is 0" % encod_video.output_height
            output += msg
            log.error(msg)
            addInfoVideo(video, msg)
            send_email(msg, video)
        else:
            # there does not seem to be errors, follow the rest of the
            # procedures
            video = None
            video = Pod.objects.get(id=video_id)
            ep, created = EncodingPods.objects.get_or_create(
                video=video, encodingType=encod_video, encodingFormat="video/mp4")
            ep.encodingFile = videourl
            ep.save()
            video.save()

    f = open(os.path.join(settings.MEDIA_ROOT, VIDEOS_DIR,
                          video.owner.username, media_guard_hash, "%s" % video.id, "encode.log"), 'a+b')
    f.write(output)
    output = ""
    f.close()


def encode_webm(video_id, videofilename, encod_video, bufsize):
    if DEBUG:
        print "ENCODING WEBM %s" % encod_video.output_height
    video = Pod.objects.get(id=video_id)
    video.encoding_status = " ENCODING WEBM %s" % encod_video.output_height
    addInfoVideo(video, "\nSTART ENCOD_VIDEO WEBM %s %s" %
                 (encod_video.output_height, time.ctime()))
    video.save()
    media_guard_hash = get_media_guard(video.owner.username, video.id)
    webmfilename = os.path.join(settings.MEDIA_ROOT, VIDEOS_DIR, video.owner.username, media_guard_hash, "%s" % video.id,
                                "video_%s_%s.webm" % (video.id, encod_video.output_height))
    webmurl = os.path.join(VIDEOS_DIR, video.owner.username, media_guard_hash, "%s" % video.id,
                           "video_%s_%s.webm" % (video.id, encod_video.output_height))

    com = ENCODE_WEBM_CMD % {
        'ffmpeg': FFMPEG,
        'src': videofilename,
        'bv': encod_video.bitrate_video,
        'bufsize': bufsize,
        # 'ba':encod_video.bitrate_audio, #"%sk" %ab,
        'out': webmfilename
    }
    if DEBUG:
        print "%s" % com
    ffmpegresult = commands.getoutput(com)
    video = None
    video = Pod.objects.get(id=video_id)
    addInfoVideo(video, "\nEND ENCOD_VIDEO WEBM %s %s" %
                 (encod_video.output_height, time.ctime()))

    output = "\n\n END ENCOD_VIDEO WEBM %s  \n" % encod_video.output_height
    output += 80 * "~"
    output += "\n"
    output += ffmpegresult
    output += "\n"
    output += 80 * "~"
    if DEBUG:
        print "END ENCOD_VIDEO WEBM %s %s" % (encod_video.output_height, time.ctime())
    if os.access(webmfilename, os.F_OK):  # outfile exists
        # There was a error cause the outfile size is zero
        if (os.stat(webmfilename).st_size == 0):
            # We remove the file so that it does not cause confusion
            os.remove(webmfilename)
            msg = "ERROR ENCODING WEBM %s Output size is 0" % encod_video.output_height
            output += msg
            log.error(msg)
            addInfoVideo(video, msg)
            send_email(msg, video)
        else:
            # there does not seem to be errors, follow the rest of the
            # procedures
            video = None
            video = Pod.objects.get(id=video_id)
            ep, created = EncodingPods.objects.get_or_create(
                video=video, encodingType=encod_video, encodingFormat="video/webm")
            ep.encodingFile = webmurl
            ep.save()
            video.save()

    f = open(os.path.join(settings.MEDIA_ROOT, VIDEOS_DIR,
                          video.owner.username, media_guard_hash, "%s" % video.id, "encode.log"), 'a+b')
    f.write(output)
    output = ""
    f.close()


def encode_mp3(video_id, audiofilename, audiourl, encod_audio, in_ar):
    if DEBUG:
        print "ENCODING MP3"
    video = Pod.objects.get(id=video_id)
    video.encoding_status = "Encoding MP3"
    addInfoVideo(video, "\nStart ENCOD_VIDEO MP3 %s" % (time.ctime()))
    video.save()

    com = ENCODE_MP3_CMD % {
        'ffmpeg': FFMPEG,
        'src': video.video.path,
        'ar': in_ar,
        'ab': encod_audio.bitrate_audio,  # "%sk" %ab,
        'out': audiofilename
    }
    if DEBUG:
        print "%s" % com
    ffmpegresult = commands.getoutput(com)
    output = "\n\n ENCOD_AUDIO MP3 \n"
    output += 80 * "~"
    output += "\n"
    output += ffmpegresult
    output += "\n"
    output += 80 * "~"

    video = None
    video = Pod.objects.get(id=video_id)
    addInfoVideo(video, "\nEND ENCOD_VIDEO MP3 %s" % (time.ctime()))
    media_guard_hash = get_media_guard(video.owner.username, video.id)

    if os.access(audiofilename, os.F_OK):  # outfile exists
        # There was a error cause the outfile size is zero
        if (os.stat(audiofilename).st_size == 0):
            # We remove the file so that it does not cause confusion
            os.remove(audiofilename)
            msg = "ERROR ENCODING MP3 Output size is 0"
            output += msg
            log.error(msg)
            addInfoVideo(video, msg)
            send_email(msg, video)

        else:
            # there does not seem to be errors, follow the rest of the
            # procedures
            ep, created = EncodingPods.objects.get_or_create(
                video=video, encodingType=encod_audio, encodingFormat="audio/mp3")
            ep.encodingFile = audiourl
            ep.save()

    f = open(os.path.join(settings.MEDIA_ROOT, VIDEOS_DIR,
                          video.owner.username, media_guard_hash, "%s" % video.id, "encode.log"), 'w')
    f.write(output)
    output = ""
    f.close()


def encode_wav(video_id, audiofilename, in_ar, encod_audio):
    if DEBUG:
        print "ENCODING WAV"
    video = None
    video = Pod.objects.get(id=video_id)
    video.encoding_status = "ENCODING WAV"
    addInfoVideo(video, "\nStart ENCOD_VIDEO WAV %s" % (time.ctime()))
    video.save()
    media_guard_hash = get_media_guard(video.owner.username, video.id)
    wavfilename = os.path.join(settings.MEDIA_ROOT, VIDEOS_DIR, video.owner.username, media_guard_hash, "%s" % video.id,
                               "audio_%s_%s.wav" % (video.id, encod_audio.output_height))
    wavurl = os.path.join(VIDEOS_DIR, video.owner.username, media_guard_hash, "%s" % video.id,
                          "audio_%s_%s.wav" % (video.id, encod_audio.output_height))
    com = ENCODE_WAV_CMD % {
        'ffmpeg': FFMPEG,
        'src': audiofilename,
        'ar': in_ar,
        'ab': encod_audio.bitrate_audio,
        'out': wavfilename
    }
    if DEBUG:
        print "%s" % com
    ffmpegresult = commands.getoutput(com)

    output = "\n\n ENCOD_AUDIO WAV \n"
    output += 80 * "~"
    output += "\n"
    output += ffmpegresult
    output += "\n"
    output += 80 * "~"

    video = None
    video = Pod.objects.get(id=video_id)
    addInfoVideo(video, "\nEND ENCOD_VIDEO WAV %s" % (time.ctime()))

    if os.access(wavfilename, os.F_OK):  # outfile exists
        # There was a error cause the outfile size is zero
        if (os.stat(wavfilename).st_size == 0):
            # We remove the file so that it does not cause confusion
            os.remove(wavfilename)
            msg = "ERROR ENCODING WAV Output size is 0"
            output += msg
            log.error(msg)
            addInfoVideo(video, msg)
            send_email(msg, video)
        else:
            # there does not seem to be errors, follow the rest of the
            # procedures
            ep, created = EncodingPods.objects.get_or_create(
                video=video, encodingType=encod_audio, encodingFormat="audio/wav")
            ep.encodingFile = wavurl
            ep.save()

    f = open(os.path.join(settings.MEDIA_ROOT, VIDEOS_DIR,
                          video.owner.username, media_guard_hash, "%s" % video.id, "encode.log"), 'a+b')
    f.write(output)
    output = ""
    f.close()
