# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from pods.models import Building, Recorder

# LIVES

def lives(request):  # affichage des directs
    buildings = Building.objects.all()
    return render_to_response("mediacourses/lives.html",
                              {'buildings': buildings},
                              context_instance=RequestContext(request))

def live(request, pk):  # affichage des directs
    recorder = get_object_or_404(Recorder, pk=pk)
    if recorder.is_restricted and not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('account_login') + '?next=%s' % request.get_full_path())

    c = RequestContext(request, {'recorder': recorder})
    return render_to_response('mediacourses/live.html', c)

def liveState(request):  # affichage des directs
    if request.GET.get("recordingPlace") and request.GET.get("status"):
        recorder = get_object_or_404(
            Recorder, adress_ip=request.GET.get("recordingPlace").replace("_", "."))
        if request.GET.get("status") == "begin":
            recorder.status = 1
        else:
            recorder.status = 0
        recorder.save()
    return HttpResponse("ok")

def liveSlide(request):  # affichage des slides en direct
    c = RequestContext(request, {'filename': request.GET.get("ip")})
    return render_to_response('mediacourses/liveSlide.html', c)
    """
    if request.GET.get("ip"):
        filename = "/audiovideocours/ftp/live/%s.jpg" %request.GET.get("ip").replace(".", "_") #Select your file here.
        if not os.path.isfile(filename):
            return HttpResponse("pas de fichier")
        wrapper = FileWrapper(file(filename))
        mt = mimetypes.guess_type(filename)[0]
        response = HttpResponse(wrapper, content_type=mt)
        response['Content-Length'] = os.path.getsize(filename)
        return response
    else:
        return HttpResponse("pas de fichier")
    """