from django.urls import path, include

app_name = 'v1'

urlpatterns = [
    path('converter/', include(('api.v1.converter.urls', 'converter_v1'))),
]