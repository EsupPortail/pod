from django.contrib.syndication.views import Feed
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from string import replace
from HTMLParser import HTMLParser
from models import * 

unescape = HTMLParser().unescape

VIDEOS = Pod.objects.filter(is_draft=False, encodingpods__gt=0).distinct()


class MySelectFeed(Feed):
    title = "Test de la fonction RSS"
    link = "/rss/"
    description = "Test feed RSS."

# OKKKKKKKKKKKKKKKKKKKKKKKK
    #def get_object(self, request, slug_c):

        #VIDEOS = Pod.objects.filter(is_draft=False, encodingpods__gt=0).distinct()
	
	# channel
	#if slug_c:
	    #print(slug_c)
	    #channel = get_object_or_404(Channel, slug=slug_c.split("=")[1])
	    #VIDEOS = VIDEOS.filter(channel=channel)

        #return channel
    
    #def items(self, obj):
        #VIDEOS = Pod.objects.filter(is_draft=False, encodingpods__gt=0).distinct()
	#print type(obj)
	#VIDEOS = VIDEOS.filter(channel=obj)
	#print(VIDEOS)
	#return VIDEOS

# OKKKKKKKKKKKKKKKKKKKKKKKK

    def get_object(self, request, qparam):

    	#0videos_list = VIDEOS
    	#0is_iframe = request.GET.get('is_iframe', None)

        VIDEOS = Pod.objects.filter(is_draft=False, encodingpods__gt=0).distinct()
        filtres = ""	
	# channel
	if qparam:
	    #print"qparam : " + qparam
	    filtres = qparam.replace("'] ", "']&")

	return filtres

    def items(self, obj):

        VIDEOS = Pod.objects.filter(is_draft=False, encodingpods__gt=0).distinct()
    	
	if obj:
	    obj = obj.encode('utf8')
	    param = obj.split("&")

	    for p in param:
	        print "p : %s" % (p,)
		k,v = p.split('=')
		print "k : %s, v : %s" % (k,v)
		if k == 'channel':
		    channel = get_object_or_404(Channel, slug=v)
		    VIDEOS = VIDEOS.filter(channel=channel)
                    self.title = channel.title
		    self.description = unescape(channel.description.replace("<p>", ""))
		    self.description = self.description.replace("</p>", "")
		    
		if k == 'theme':
		    theme = get_object_or_404(Theme, slug=v)
		    VIDEOS = VIDEOS.filter(theme=theme)
		if k == 'type':
		    for iv in v:
			VIDEOS = VIDEOS.filter(type__slug__in=iv)
		if k == 'discipline':
		    for iv in v:
		        VIDEOS = VIDEOS.filter(discipline__slug__in=iv)
		if k == 'owner':
		    for iv in v:
		        VIDEOS = VIDEOS.filter(owner__username__in=iv)
		if k == 'tag':
		    v = v.encode('utf8')
		    for iv in v:
		        VIDEOS = VIDEOS.filter(tags__slug__in=iv)

	        #print("p : " + p)
	        #clause = str(p.split("="))
		#print ("clause : ") 
		#print(str(p.split("=")))
	        #VIDEOS = VIDEOS.filter(clause[0].tostring()=clause[1])
	        print(VIDEOS)
        
	return VIDEOS

# NOKKKKKKKKKKKKKKKKKKKKKKKKKKK

	#channel = request.GET.get('channel') if request.GET.get('channel') else None
        #videos_list = VIDEOS.filter(channel=channel)
	
	# theme
	#theme = request.GET.getlist('theme') if request.GET.getlist('theme') else None
	#video_list = VIDEOS.filter(theme=theme)

    	# type
    	#type = request.GET.getlist('type') if request.GET.getlist('type') else None
    	#if type:
	#    videos_list = videos_list.filter(type__slug__in=type)

    	# discipline
    	#discipline = request.GET.getlist('discipline') if request.GET.getlist('discipline') else None
    	#if discipline:
	#    videos_list = videos_list.filter(discipline__slug__in=discipline)

    	# owner
    	#owner = request.GET.getlist('owner') if request.GET.getlist('owner') else None
    	#list_owner = None
    	#if owner:


    #def title(self, item):
    	#return obj.title
    	#return item.title
	
    #def description(self, item):
    	#return obj.duration
	#print(self)
    	#return item.duration
	
    # item_link is only needed if NewsItem has no get_absolute_url method.
    #def link(self, item):
    	#return reverse('pods.views.video', args=(item.slug,))
	#return obj.video.get_absolute_url()
    #    return "http://test"

    #def pubdate(self, item):
        #return item.date_added

    #def author_name (self, item):
    	#return obj.owner.username
    	#return item.owner.username


