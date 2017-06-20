from django.conf.urls import url

from . import views

from cap.models import VolumeMetadata


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^events.csv$', views.events, name='events'),
]