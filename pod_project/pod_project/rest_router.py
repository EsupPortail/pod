from rest_framework import routers
from core import rest_views as core_views
from pods import rest_views as pods_views
from django.conf.urls import url

router = routers.DefaultRouter()
router.register(r'users', core_views.UserViewSet)
router.register(r'groups', core_views.GroupViewSet)
router.register(r'types', pods_views.TypeViewSet)
router.register(r'pods', pods_views.PodViewSet)
router.register(r'contributors', pods_views.ContributorPodsViewSet)
router.register(r'encodings', pods_views.EncodingPodsViewSet)
router.register(r'chapters', pods_views.ChapterPodsViewSet)

urlpatterns = [
    url(r'get_user_by_username/$', core_views.GetUserView.as_view(),
        name='get_user_by_username'),
    url(r'launch_pod_encode/$', pods_views.EncodePodView.as_view(),
        name='encode video_by_id'),
    url(r'dublincore/$', pods_views.DublinCoreView.as_view(), name='dublincore'),
]

urlpatterns += router.urls
