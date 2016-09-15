from rest_framework import routers
from core import rest_views

router = routers.DefaultRouter()
router.register(r'userprofiles', rest_views.UserProfileViewSet)
router.register(r'users', rest_views.UserViewSet)
router.register(r'groups', rest_views.GroupViewSet)
