from rest_framework import routers
from core import rest_views
from django.conf.urls import url

router = routers.DefaultRouter()
#router.register(r'userprofiles', rest_views.UserProfileViewSet)
router.register(r'users', rest_views.UserViewSet)
router.register(r'groups', rest_views.GroupViewSet)

urlpatterns = [
        url(r'users/get_user_by_username/$', rest_views.GetUserView.as_view(), name='get_user_by_username'),
        ]
        
urlpatterns += router.urls
