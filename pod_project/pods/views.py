# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pods.viewsdir.categories_views import *
from pods.viewsdir.channel_views import *
from pods.viewsdir.chapters_views import *
from pods.viewsdir.completion_views import *
from pods.viewsdir.enrichment_views import *
from pods.viewsdir.favorites_views import *
from pods.viewsdir.live_views import *
from pods.viewsdir.mediacourses_views import *
from pods.viewsdir.oembed_views import *
from pods.viewsdir.owners_views import *
from pods.viewsdir.search_views import *
from pods.viewsdir.videos_views import *


#def autocomplete(request):
#    suggestions = [entry.object.title for entry in res]
#    # Make sure you return a JSON object, not a bare list.
#    # Otherwise, you could be vulnerable to an XSS attack.
#    the_data = json.dumps({})
#    return HttpResponse(the_data, content_type='application/json')