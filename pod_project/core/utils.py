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
import sys, os, subprocess, re, time, json
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from core.models import EncodingType
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

def encode_video(video_to_encode):
    VIDEO_ID = video_to_encode.id
    start = "Start at : %s" % time.ctime()
    if DEBUG :
        print start
    video=None
    video = Pod.objects.get(id=VIDEO_ID)
    video.encoding_status = "Start encode"
    video.infoVideo = "%s" %start
    video.save()
    
    
    if os.path.exists(video.video.path):
        #DELETE PREVIOUS ENCODING
        ##### EncodingPods.objects.filter(video=video).delete()
        if DEBUG :
            print "DELETE PREVIOUS ENCODING"
        video=None
        video = Pod.objects.get(id=VIDEO_ID)
        previous_encoding = EncodingPods.objects.filter(video=video)
        if video.infoVideo is None:
            video.infoVideo = ""
        video.infoVideo += "DELETE PREVIOUS ENCODING"
        previous_encoding.delete()
        video.save()
        
        if DEBUG :
            print "get video data"
        #GET VIDEO DATA
        video=None
        video = Pod.objects.get(id=VIDEO_ID)
        command = "%(ffprobe)s -v quiet -show_format -show_streams -print_format json -i %(src)s " %{ # add -count_frames to get nb_read_frames but it's quite long
                        'ffprobe':FFPROBE,
                        'src':video.video.path,
                    }
        
        ffproberesult = commands.getoutput(command)
        info = json.loads(ffproberesult)
        #print info['streams'][1]['codec_long_name'], info['streams'][1]['duration']
        video=None
        video = Pod.objects.get(id=VIDEO_ID)
        if video.infoVideo is None:
            video.infoVideo = ""
        video.infoVideo += unicode(json.dumps(info, sort_keys=True, indent=4, separators=(',', ': ')), errors='ignore')
        video.save()
        #DURATION
        video=None
        video = Pod.objects.get(id=VIDEO_ID)
        video.encoding_status = "Get duration"
        video.save()
        duration = None
        try:
            duration = float("%s" %info["format"]['duration'])
            video=None
            video = Pod.objects.get(id=VIDEO_ID)
            video.duration = int(duration)
            video.save()
        except:
            try:
                msg = u'\n***** Unexpected error :%s - %s' %(sys.exc_info()[0], sys.exc_info()[1])
                video=None
                video = Pod.objects.get(id=VIDEO_ID)
                if video.infoVideo is None:
                    video.infoVideo = ""
                video.infoVideo += unicode(msg, errors='ignore')
                video.encoding_status = ">>>>>> NO DURATION"
                video.save()
                send_email(">>>>>> NO DURATION", video)
            except:
                msg = u'\n***** Unexpected error :%s - %s' %(sys.exc_info()[0], sys.exc_info()[1])
                video = Pod.objects.get(id=VIDEO_ID)
                send_email(msg, video)
            return
        #PARSE STREAMS
        video=None
        video = Pod.objects.get(id=VIDEO_ID)
        if video.infoVideo is None:
            video.infoVideo = ""
        is_video = False
        in_width = 0
        in_height = 0
        nb_frames = 0
        in_audio_rate = 44100
        in_audio_bitrate = 128
        for stream in info["streams"]:
            if stream.get("codec_type") :
                if stream["codec_type"]=="video":
                    is_video = True
                    try:
                        video.encoding_status = "GET WIDTH AND HEIGHT"
                        video.save()
                        in_width = int(stream["width"])
                        in_height = int(stream["height"])
                        video.infoVideo += unicode("\n Width : %s - Height : %s"%(in_width, in_height), errors='ignore')
                        video.save()
                    except:
                        msg = u'\n***** Unexpected error :%s - %s' %(sys.exc_info()[0], sys.exc_info()[1])
                        video.infoVideo += unicode(msg, errors='ignore')
                        video.encoding_status = "VIDEO WITHOUT WIDTH AND HEIGHT"
                        video.save()
                        send_email("VIDEO WITHOUT WIDTH AND HEIGHT", video)
                        return
                    #CALC FRAMES with frame rate and duration
                    try:
                        video.encoding_status = "GET NB FRAMES"
                        video.save()
                        if stream.get("nb_frames"):
                            nb_frames = int(stream.get("nb_frames"))
                        else:
                            video.infoVideo += unicode("\n Calc nb frame ", errors='ignore')
                            in_frame = int(stream["r_frame_rate"].replace("/1",""))
                            nb_frames = int(round(duration * float(in_frame)))
                            
                        video.infoVideo += unicode("\n Nb frames %s"%(nb_frames), errors='ignore')
                        video.save()
                    except:
                        msg = u'\n***** Unexpected error :%s - %s' %(sys.exc_info()[0], sys.exc_info()[1])
                        video.infoVideo += unicode(msg, errors='ignore')
                        video.encoding_status = "ERROR NB FRAMES"
                        video.save()
                        send_email("ERROR NB FRAMES", video)
                        return
                    # SAR sample_aspect_ratio
                    if stream.get("sample_aspect_ratio"):
                        try:
                            video.encoding_status = "GET SAR"
                            video.save()
                            sar_w, sar_h = [int(_) for _ in stream.get("sample_aspect_ratio").split(':')]
                            sar = 1
                            if sar_w != 0 and sar_h != 0:
                                sar = (1.*sar_w/sar_h)
                            in_width = int(1.*in_width*sar)
                            video.infoVideo +=  "\n IN_WIDTH %s" %(in_width)
                            video.save()
                        except:
                            msg = u'\n***** Unexpected error :%s - %s' %(sys.exc_info()[0], sys.exc_info()[1])
                            video.infoVideo += unicode(msg, errors='ignore')
                            video.encoding_status = "ERROR CALC SAR"
                            video.save()
                            send_email("ERROR CALC SAR", video)
                            return
                    #Fin stream video
                if stream["codec_type"]=="audio":
                    if stream.get("sample_rate"):
                        video.encoding_status = "GET AUDIO SAMPLE RATE"
                        video.save()
                        try:
                            in_audio_rate = int(stream.get("sample_rate"))
                        except:
                            video.infoVideo +=  "\n ERROR GET AUDIO SAMPLE RATE"
                            video.save()
                    if stream.get("bit_rate"):
                        video.encoding_status = "GET AUDIO BIT RATE"
                        video.save()
                        try:
                            in_audio_bitrate = int(int(stream.get("bit_rate"))/1000)
                        except:
                            video.infoVideo +=  "\n ERROR GET AUDIO BIT RATE"
                            video.save()
                    #Fin stream audio
            else:
                video.encoding_status = "NO CODEC TYPE FOUND"
                video.save()
                send_email("NO CODEC TYPE FOUND", video)
                return
        #FIN PARSE STREAMS
        if DEBUG :
            print "FIN PARSE STREAMS"
        video=None
        video = Pod.objects.get(id=VIDEO_ID)
        #VIDEO/AUDIO FOLDER
        if not(os.access(os.path.join(settings.MEDIA_ROOT, VIDEOS_DIR , video.owner.username, "%s" %video.id) , os.F_OK)):
            os.makedirs(os.path.join(settings.MEDIA_ROOT, VIDEOS_DIR , video.owner.username, "%s" %video.id))
        if DEBUG :
            print "VIDEO/AUDIO FOLDER"
        # FILER FOLDER
        rootFolder =  Folder.objects.get(name=video.owner,owner=video.owner,level=0)
        folder, created = Folder.objects.get_or_create(name=video.slug, owner=video.owner, parent=rootFolder)
        if DEBUG :
            print "FILER FOLDER"
        video=None
        #FOR VIDEO 
        if is_video:
            #MAKE THUMBNAILS
            video = Pod.objects.get(id=VIDEO_ID)
            if int(video.duration) > 3:
                add_thumbnails(VIDEO_ID, in_width, in_height, folder)
            video=None
            #MAKE OVERVIEW
            if nb_frames > 100:
                add_overview(VIDEO_ID, in_width, in_height, nb_frames)
            
            list_encod_video = EncodingType.objects.filter(mediatype='video').order_by('output_height') #.exclude(output_height=1080)
            for encod_video in list_encod_video:
                bufsize = encod_video.bitrate_video
                try:
                    int_bufsize = int(re.search("(\d+)k", bufsize, re.I).groups()[0])
                    bufsize = "%sk" %(int_bufsize*2)
                except:
                    pass
                if in_height >= encod_video.output_height:
                    video = Pod.objects.get(id=VIDEO_ID)
                    videofilename = os.path.join(settings.MEDIA_ROOT, VIDEOS_DIR , video.owner.username, "%s" %video.id, 
                                    "video_%s_%s.mp4"%(video.id,encod_video.output_height))
                    videourl = os.path.join(VIDEOS_DIR , video.owner.username, "%s" %video.id, 
                                    "video_%s_%s.mp4"%(video.id,encod_video.output_height))
                    encode_mp4(VIDEO_ID, in_width, in_height, bufsize, in_audio_rate, encod_video, videofilename, videourl)
                    if os.access(videofilename, os.F_OK):
                        encode_webm(VIDEO_ID, videofilename, encod_video, bufsize)
        else:
            list_encod_audio = EncodingType.objects.filter(mediatype='audio')
            for encod_audio in list_encod_audio:
                video = Pod.objects.get(id=VIDEO_ID)
                audiofilename = os.path.join(settings.MEDIA_ROOT, VIDEOS_DIR , video.owner.username, "%s" %video.id, 
                                    "audio_%s_%s.mp3"%(video.id,encod_audio.output_height))
                audiourl = os.path.join(VIDEOS_DIR , video.owner.username, "%s" %video.id, 
                                "audio_%s_%s.mp3"%(video.id,encod_audio.output_height))
                encode_mp3(VIDEO_ID, audiofilename, audiourl, encod_audio, in_audio_rate)
                if os.access(audiofilename, os.F_OK):
                    encode_wav(VIDEO_ID, audiofilename, in_audio_rate, encod_audio)
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

    end = "End : %s" % time.ctime()
    print end
    video = None
    video = Pod.objects.get(id=VIDEO_ID)
    if video.infoVideo is None:
        video.infoVideo = ""
    video.infoVideo += "\n %s" %end
    video.encoding_in_progress=False
    video.save()
    
#end encode_video(video):


def get_scale(in_w, in_h, out_h):
    if in_w > in_h:
        new_height = out_h
        new_width = (1.*in_w * new_height / in_h)
        if int(new_width)%2 != 0:
            new_width = new_width +1
    else:
        new_width = out_h
        new_height = (1.*in_h * new_width / in_w)
        if int(new_height)%2 != 0:
            new_height = new_height +1
    return "%s:%s" %(int(new_width), int(new_height))
    
def send_email(msg, video):
    admin_emails = [v for k,v in settings.ADMINS]
    msg = EmailMultiAlternatives("["+settings.TITLE_SITE+"] Error Encoding", "Error Encoding  video id : %s\n%s" %(video.id, msg), settings.DEFAULT_FROM_EMAIL, admin_emails)
    msg.attach_alternative("<p>Error Encoding video id : %s</p><p>%s</p>" %(video.id, msg), "text/html")
    msg.send(fail_silently=False)
    return


#DEF THUMBNAILS
def add_thumbnails(video_id, in_w, in_h, folder):
    if DEBUG :
        print "ADD THUMBNAILS"
    video = Pod.objects.get(id=video_id)
    video.encoding_status = "ADD THUMBNAILS"
    video.save()
    tempfile = NamedTemporaryFile()
    scale = get_scale(in_w, in_h, DEFAULT_THUMBNAIL_OUT_SIZE_HEIGHT)
    thumbnails = int(video.duration/3)
    #com = "%s -i \"%s\" -vf \"thumbnail=%s,scale=%s\" -an -vsync 0 -threads 0 -y %s_%s.jpg" %(FFMPEG, video.video.path, thumbnails, scale, tempfile.name, "%d")
    com = "%s -i \"%s\" -vf fps=\"fps=1/%s,scale=%s\" -an -vsync 0 -threads 0 -f image2 -y %s_%s.png" %(FFMPEG, video.video.path, thumbnails, scale, tempfile.name, "%d")
    thumbresult = commands.getoutput(com)
    output = "\n\nTHUMBNAILS"
    output += 80*"~"
    output += "\n"
    output += thumbresult
    output += "\n"
    output += 80*"~"
    
    f = open(os.path.join(settings.MEDIA_ROOT, VIDEOS_DIR , video.owner.username, "%s" %video.id, "encode.log"), 'w')
    f.write(output)
    output = ""
    f.close()
    
    video=None
    video = Pod.objects.get(id=video_id)
    for i in range(2,5):
        if os.access("%s_%s.png"%(tempfile.name, i), os.F_OK):
            if DEBUG :
                print "THUMBNAILS %s" %i
            upc_image, created = Image.objects.get_or_create(folder=folder, name="%s_%s.png"%(video.slug,i))
            upc_image.file.save("%s_%s.png"%(video.slug,i), File(open("%s_%s.png"%(tempfile.name, i))), save=True)
            upc_image.owner=video.owner
            upc_image.save()
            try:
                os.remove("%s_%s.png"%(tempfile.name, i))
            except:
                pass
            if i == 2:
                video.thumbnail = upc_image
        else:
            if video.infoVideo is None:
                video.infoVideo = ""
            video.infoVideo += "\n [add_thumbnails] error accessing %s_%s.png" %(tempfile.name, i)
    video.save()
    try:
        os.remove("%s_1.png"%(tempfile.name))
        os.remove("%s_5.png"%(tempfile.name))
    except:
        pass

def add_overview(video_id, in_w, in_h, frames):
    if DEBUG :
        print "OVERVIEW"
    video = Pod.objects.get(id=video_id)
    thumbnails = int(frames/100)
    scale = get_scale(in_w, in_h, DEFAULT_OVERVIEW_OUT_SIZE_HEIGHT)
    
    overviewfilename = os.path.join(settings.MEDIA_ROOT, VIDEOS_DIR , video.owner.username, "%s" %video.id, "overview.jpg")
    overviewurl = os.path.join(VIDEOS_DIR , video.owner.username, "%s" %video.id, "overview.jpg")
    
    com = "%s -i \"%s\" -vf \"thumbnail=%s,scale=%s,tile=100x1:nb_frames=100:padding=0:margin=0\" -an -vsync 0 -threads 0 -y %s" %(FFMPEG, video.video.path, thumbnails, scale, overviewfilename)
    overviewresult = commands.getoutput(com)
    output = "\n\nOVERVIEW"
    output += 80*"~"
    output += "\n"
    output += overviewresult
    output += "\n"
    output += 80*"~"
    
    if os.access(overviewfilename, os.F_OK): # outfile exists
        # There was a error cause the outfile size is zero
        if (os.stat(overviewfilename).st_size==0): 
            # We remove the file so that it does not cause confusion
            output += "\nERROR : Output size is 0\n"
            os.remove(overviewfilename)
        else:
            # there does not seem to be errors, follow the rest of the procedures
            if DEBUG :
                print "OVERVIEW : %s" %overviewurl
            video = None
            video = Pod.objects.get(id=video_id)
            video.overview = overviewurl
            video.save()
    
    f = open(os.path.join(settings.MEDIA_ROOT, VIDEOS_DIR , video.owner.username, "%s" %video.id, "encode.log"), 'a+b')
    f.write(output)
    output = ""
    f.close()

def encode_mp4(video_id, in_w, in_h, bufsize, in_ar, encod_video, videofilename, videourl):
    if DEBUG :
        print "ENCODING MP4 %s" %encod_video.output_height
    video = None
    video = Pod.objects.get(id=video_id)
    video.encoding_status = "ENCODING MP4 %s" %encod_video.output_height
    video.save()
    scale = get_scale(in_w, in_h, encod_video.output_height)
                    
    video.infoVideo +=  "\nSTART ENCOD_VIDEO MP4 %s - %s - %s - %s" %(encod_video.output_height, bufsize, scale, time.ctime())
    
    com = "%(ffmpeg)s -i %(src)s -codec:v libx264 -profile:v high -pix_fmt yuv420p -preset faster -b:v %(bv)s -maxrate %(bv)s -bufsize %(bufsize)s -vf scale=%(scale)s -force_key_frames \"expr:gte(t,n_forced*1)\" -deinterlace -threads 0 -codec:a aac -strict -2 -ar %(ar)s -ac 2 -b:a %(ba)s -movflags faststart -y %(out)s" %{
            'ffmpeg':FFMPEG,
            'src':video.video.path,
            'bv':encod_video.bitrate_video,
            'bufsize':bufsize,
            'scale':scale,
            'ar':in_ar,
            'ba':encod_video.bitrate_audio,
            'out':videofilename
        }
    
    ffmpegresult = commands.getoutput(com)
    video = None
    video = Pod.objects.get(id=video_id)
    if video.infoVideo is None:
        video.infoVideo = ""
    video.infoVideo +=  "\n END ENCOD_VIDEO MP4 %s %s" %(encod_video.output_height, time.ctime())
    video.save()
    output = "\n\n ENCOD_VIDEO MP4 %s \n" %encod_video.output_height
    output += 80*"~"
    output += "\n"
    output += ffmpegresult
    
    if DEBUG :
        print "ENCOD_VIDEO MP4 %s \n" %encod_video.output_height
    
    if os.access(videofilename, os.F_OK): # outfile exists
        # There was a error cause the outfile size is zero
        if (os.stat(videofilename).st_size==0): 
            # We remove the file so that it does not cause confusion
            output += "\nERROR : Output size is 0\n"
            video = None
            video = Pod.objects.get(id=video_id)
            if video.infoVideo is None:
                video.infoVideo = ""
            video.infoVideo +=  "\nERROR : Output size is 0\n"
            video.save()
            os.remove(videofilename)
            send_email("ERROR ENCODING MP4 %s Output size is 0" %encod_video.output_height, video)
        else:
            # there does not seem to be errors, follow the rest of the procedures
            video = None
            video = Pod.objects.get(id=video_id)
            ep, created = EncodingPods.objects.get_or_create(video=video, encodingType=encod_video, encodingFormat="video/mp4")
            ep.encodingFile = videourl
            ep.save()
            video.save()
            
    
    f = open(os.path.join(settings.MEDIA_ROOT, VIDEOS_DIR , video.owner.username, "%s" %video.id, "encode.log"), 'a+b')
    f.write(output)
    output = ""
    f.close()


def encode_webm(video_id, videofilename, encod_video, bufsize):
    if DEBUG :
        print "ENCODING WEBM %s" %encod_video.output_height
    video = Pod.objects.get(id=video_id)
    video.encoding_status = " ENCODING WEBM %s" %encod_video.output_height
    video.save()
    webmfilename = os.path.join(settings.MEDIA_ROOT, VIDEOS_DIR , video.owner.username, "%s" %video.id, 
                    "video_%s_%s.webm"%(video.id,encod_video.output_height))
    webmurl = os.path.join(VIDEOS_DIR , video.owner.username, "%s" %video.id, 
                    "video_%s_%s.webm"%(video.id,encod_video.output_height))
    video = None
    video = Pod.objects.get(id=video_id)
    if video.infoVideo is None:
        video.infoVideo = ""
    video.infoVideo +=  "\nSTART ENCOD_VIDEO WEBM %s %s" %(encod_video.output_height, time.ctime())
    video.save()
    #com = "%(ffmpeg)s -i %(src)s -c:v libvpx -b:v %(bv)s -crf 25 -c:a libvorbis -b:a %(ba)s -threads 0 -y %(out)s"
    com = "%(ffmpeg)s -i %(src)s -codec:v libvpx -quality realtime -cpu-used 3 -b:v %(bv)s -maxrate %(bv)s -bufsize %(bufsize)s -qmin 10 -qmax 42 -threads 4 -codec:a libvorbis -y %(out)s" %{
            'ffmpeg':FFMPEG,
            'src':videofilename,
            'bv':encod_video.bitrate_video,
            'bufsize':bufsize,
            #'ba':encod_video.bitrate_audio, #"%sk" %ab,
            'out':webmfilename
    }
    
    ffmpegresult = commands.getoutput(com)
    video = None
    video = Pod.objects.get(id=video_id)
    if video.infoVideo is None:
        video.infoVideo = ""
    video.infoVideo +=  "\nEND ENCOD_VIDEO WEBM %s %s" %(encod_video.output_height, time.ctime())
    video.save()
    output = "\n\n END ENCOD_VIDEO WEBM %s  \n" %encod_video.output_height
    output += 80*"~"
    output += "\n"
    output += ffmpegresult
    output += "\n"
    output += 80*"~"
    if DEBUG :
        print "END ENCOD_VIDEO WEBM %s %s" %(encod_video.output_height, time.ctime())
    if os.access(webmfilename, os.F_OK): # outfile exists
        # There was a error cause the outfile size is zero
        if (os.stat(webmfilename).st_size==0): 
            # We remove the file so that it does not cause confusion
            output += "\nERROR : Output size is 0\n"
            video = None
            video = Pod.objects.get(id=video_id)
            if video.infoVideo is None:
                video.infoVideo = ""
            video.infoVideo +=  "\nERROR : Output size is 0\n"
            video.save()
            os.remove(webmfilename)
            send_email("ERROR ENCODING WEBM %s Output size is 0" %encod_video.output_height, video)
        else:
            # there does not seem to be errors, follow the rest of the procedures
            video = None
            video = Pod.objects.get(id=video_id)
            ep, created = EncodingPods.objects.get_or_create(video=video, encodingType=encod_video, encodingFormat="video/webm")
            ep.encodingFile = webmurl
            ep.save()
            video.save()
            
    f = open(os.path.join(settings.MEDIA_ROOT, VIDEOS_DIR , video.owner.username, "%s" %video.id, "encode.log"), 'a+b')
    f.write(output)
    output = ""
    f.close()

def encode_mp3(video_id, audiofilename, audiourl, encod_audio, in_ar):
    video = Pod.objects.get(id=video_id)
    video.encoding_status = "Encoding MP3"
    video.save()
    
    com = "%(ffmpeg)s -i %(src)s -vn -ar %(ar)s -ab %(ab)s -f mp3 -threads 0 -y %(out)s" %{
            'ffmpeg':FFMPEG,
            'src':video.video.path,
            'ar':in_ar,
            'ab': encod_audio.bitrate_audio, #"%sk" %ab,
            'out':audiofilename
        }
    
    ffmpegresult = commands.getoutput(com)
    output = "\n\n ENCOD_AUDIO MP3 \n"
    output += 80*"~"
    output += "\n"
    output += ffmpegresult
    output += "\n"
    output += 80*"~"
    
    if os.access(audiofilename, os.F_OK): # outfile exists
        # There was a error cause the outfile size is zero
        if (os.stat(audiofilename).st_size==0): 
            # We remove the file so that it does not cause confusion
            output += "\nERROR : Output size is 0\n"
            os.remove(audiofilename)
            send_email("ERROR ENCODING MP3 %s Output size is 0" %encod_video.output_height, video)
        else:
            # there does not seem to be errors, follow the rest of the procedures
            ep, created = EncodingPods.objects.get_or_create(video=video, encodingType=encod_audio, encodingFormat="audio/mp3")
            ep.encodingFile = audiourl
            ep.save()
            
    
    f = open(os.path.join(settings.MEDIA_ROOT, VIDEOS_DIR , video.owner.username, "%s" %video.id, "encode.log"), 'w')
    f.write(output)
    output = ""
    f.close()

def encode_wav(video_id, audiofilename, in_ar, encod_audio):
    video = None
    video = Pod.objects.get(id=video_id)
    video.encoding_status = "ENCODING WAV"
    video.save()
    wavfilename = os.path.join(settings.MEDIA_ROOT, VIDEOS_DIR , video.owner.username, "%s" %video.id, 
                    "audio_%s_%s.wav"%(video.id,encod_audio.output_height))
    wavurl = os.path.join(VIDEOS_DIR , video.owner.username, "%s" %video.id, 
                "audio_%s_%s.wav"%(video.id,encod_audio.output_height))
    #ffmpeg -i monMorceau.mp3 monMorceau.wav
    com = "%(ffmpeg)s -i %(src)s -ar %(ar)s -ab %(ab)s -f wav -threads 0 -y %(out)s" %{
        'ffmpeg':FFMPEG,
        'src':audiofilename,
        'ar':in_ar,
        'ab':encod_audio.bitrate_audio,
        'out':wavfilename
    }
    ffmpegresult = commands.getoutput(com)
    
    output = "\n\n ENCOD_AUDIO WAV \n"
    output += 80*"~"
    output += "\n"
    output += ffmpegresult
    output += "\n"
    output += 80*"~"
    
    if os.access(wavfilename, os.F_OK): # outfile exists
        # There was a error cause the outfile size is zero
        if (os.stat(wavfilename).st_size==0): 
            # We remove the file so that it does not cause confusion
            output += "\nERROR : Output size is 0\n"
            os.remove(wavfilename)
            send_email("ERROR ENCODING WAV %s Output size is 0" %encod_video.output_height, video)
        else:
            # there does not seem to be errors, follow the rest of the procedures
            ep, created = EncodingPods.objects.get_or_create(video=video, encodingType=encod_audio, encodingFormat="audio/wav")
            ep.encodingFile = wavurl
            ep.save()
    
    f = open(os.path.join(settings.MEDIA_ROOT, VIDEOS_DIR , video.owner.username, "%s" %video.id, "encode.log"), 'a+b')
    f.write(output)
    output = ""
    f.close()    