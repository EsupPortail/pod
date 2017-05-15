from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import RedirectView
from django.contrib import admin
admin.autodiscover()

from pods.utils_itunesfeed import PodcastHdFeed, PodcastSdFeed, AudiocastFeed, MySelectFeed

urlpatterns = [
    url(r'^favicon\.ico$', RedirectView.as_view(
        url=settings.STATIC_URL + 'images/favicon.ico', permanent=True)),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^rest/', include('pod_project.rest_router')),
    url(r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework')),

    # ACCOUNT
    url(r'^accounts/login/$', 'core.views.core_login', name='account_login'),
    url(r'^accounts/logout/$', 'core.views.core_logout',
        name='account_logout'),
    url(r'^accounts/cas/login/$',
        'django_cas_gateway.views.login', name='cas_login'),
    url(r'^accounts/cas/logout/$',
        'django_cas_gateway.views.logout', name='cas_logout'),
    url(r'^user/', 'core.views.user_profile', name='user_profile'),

    # STATUS
    url(r'^status/', 'core.views.status', name='status'),

    url(r'^owner_channels_list/', 'pods.views.owner_channels_list',
        name='owner_channels_list'),
    url(r'^owner_videos_list/', 'pods.views.owner_videos_list',
        name='owner_videos_list'),
    url(r'^favorites_videos_list/', 'pods.views.favorites_videos_list',
        name='favorites_videos_list'),

    # TEXT EDITOR
    url(r'^ckeditor/', include('ckeditor.urls')),
    url(r'^browse/', 'core.views.file_browse', name='ckeditor_browse'),

    # Add-on for non-staff users
    url(r'^my-admin/jsi18n/',
        'django.views.i18n.javascript_catalog',
        {'packages': ('django.conf', 'django.contrib.admin')}),

    url(r'^search/$', 'pods.views.search_videos', name='search_videos'),
    url(r'^contact_us/$', 'core.views.contact_us', name='contact_us'),
    url(r'^captcha/', include('captcha.urls')),

    # MEDIACOURSES
    url(r'^mediacourses_add/$',
        'pods.views.mediacourses', name="mediacourses"),
    url(r'^mediacourses_notify/$',
        'pods.views.mediacourses_notify', name="mediacourses_notify"),
    url(r'^lives/$', 'pods.views.lives', name="lives"),
    # Warning do not modify for the recorder
    url(r'^liveState/$', 'pods.views.liveState', name="liveState"),
    url(r'^liveSlide/$', 'pods.views.liveSlide', name="liveSlide"),
    url(r'^live/(?P<pk>\d+)/$', 'pods.views.live', name="live"),

    # POD VIDEOS
    url(r'^owners/$', 'pods.views.owners', name='owners'),
    url(r'^types/$', 'pods.views.types', name='types'),
    url(r'^disciplines/$', 'pods.views.disciplines', name='disciplines'),
    url(r'^tags/$', 'pods.views.tags', name='tags'),
    url(r'^videos/$', 'pods.views.videos', name='videos'),
    url(r'^video/(?P<slug>[\-\d\w]+)/$', 'pods.views.video', name='video'),
    url(r'^video_edit/$', 'pods.views.video_edit', name='video_edit'),
    url(r'^video_edit/(?P<slug>[\-\d\w]+)/$',
        'pods.views.video_edit', name='video_edit'),
    url(r'^video_delete/(?P<slug>[\-\d\w]+)/$',
        'pods.views.video_delete', name='video_delete'),
    url(r'^video_add_favorite/(?P<slug>[\-\d\w]+)/$',
        'pods.views.video_add_favorite', name='video_add_favorite'),
    url(r'^video_add_report/(?P<slug>[\-\d\w]+)/$',
        'pods.views.video_add_report', name='video_add_report'),
    url(r'^video_completion/(?P<slug>[\-\d\w]+)/$',
        'pods.views.video_completion', name='video_completion'),
    url(r'^video_completion_contributor/(?P<slug>[\-\d\w]+)/$',
        'pods.views.video_completion_contributor',
        name='video_completion_contributor'),
    url(r'^video_completion_subtitle/(?P<slug>[\-\d\w]+)/$',
        'pods.views.video_completion_subtitle',
        name='video_completion_subtitle'),
    url(r'^video_completion_download/(?P<slug>[\-\d\w]+)/$',
        'pods.views.video_completion_download',
        name='video_completion_download'),
    url(r'^video_chapter/(?P<slug>[\-\d\w]+)/$',
        'pods.views.video_chapter', name='video_chapter'),
    url(r'^video_enrich/(?P<slug>[\-\d\w]+)/$',
        'pods.views.video_enrich', name='video_enrich'),
    url(r'^video_notes/(?P<slug>[\-\d\w]+)/$',
        'pods.views.video_notes', name='video_notes'),
    url(r'^get_video_encoding/(?P<slug>[\-\d\w]+)/(?P<csrftoken>[\-\d\w]+)/(?P<size>[\-\d]+)/(?P<type>[\-\d\w]+)/(?P<ext>[\-\d\w]+)/$',
        'pods.views.get_video_encoding',
        name='get_video_encoding'),
]

if settings.H5P_ENABLED:
    urlpatterns += [
        url(r'^video_interactive/(?P<slug>[\-\d\w]+)/$',
        'pods.views.video_interactive', name='video_interactive'),
        url(r'^h5p/', include('h5pp.urls')),
    ]

urlpatterns += [
    # Channel
    url(r'^channels/$', 'pods.views.channels', name='channels'),
    url(r'^(?P<slug_c>[\-\d\w]+)/$', 'pods.views.channel', name='channel'),
    url(r'^(?P<slug_c>[\-\d\w]+)/edit$',
        'pods.views.channel_edit', name='channel_edit'),
    url(r'^(?P<slug_c>[\-\d\w]+)/(?P<slug_t>[\-\d\w]+)/$',
        'pods.views.channel', name='theme'),
    url(r'^(?P<slug_c>[\-\d\w]+)/video/(?P<slug>[\-\d\w]+)/$',
        'pods.views.video', name='video'),
    url(r'^(?P<slug_c>[\-\d\w]+)/(?P<slug_t>[\-\d\w]+)/video/(?P<slug>[\-\d\w]+)/$',
        'pods.views.video', name='video'),
]

##
# Add-on to serve MEDIA files when using django-admin runserver:
#   - django.contrib.staticfiles.views.serve() works only in debug mode, so
#   the two lines below may be removed into production;
#   - note: as we use django.contrib.staticfiles, static files are
#   automatically served by runserver when DEBUG=True.
#
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

#RSS Feed
if settings.RSS_ENABLED:
    urlpatterns += [
        url(r'^rss/select/(?P<qparam>[^\/]+)/$', MySelectFeed(), name = 'rss_select'),
   ] 
#ATOM HD Feed
if settings.ATOM_HD_ENABLED:
    urlpatterns += [
        url(r'^rss/hd/(?P<qparam>[^\/]+)/$', PodcastHdFeed(), name = 'podcast_hd'),
    ]
# ATOM SD Feed
if settings.ATOM_SD_ENABLED:
    urlpatterns += [
        url(r'^rss/sd/(?P<qparam>[^\/]+)/$', PodcastSdFeed(), name = 'podcast_sd'),
    ]
#ATOM Audio Feed
#if settings.ATOM_AUDIO_ENABLED:
#    urlpatterns += [
#        url(r'^rss/audio/(?P<qparam>[^\/]+)/$', AudiocastFeed(), name = 'audiocast'),
#    ]
