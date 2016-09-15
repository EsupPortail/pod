from rest_framework import routers
from pods import rest_views

router = routers.DefaultRouter()
router.register(r'pods', rest_views.PodViewSet)
router.register(r'types', rest_views.TypeViewSet)
