from rest_framework import routers

from . import viewsets

router = routers.SimpleRouter()
router.register(r'', viewsets.ConverterViewSet, basename='converter')

urlpatterns = router.urls
