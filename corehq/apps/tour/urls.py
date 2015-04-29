from django.conf.urls import *
from corehq.apps.tour.views import *


urlpatterns = patterns('corehq.apps.tour.views',
    url(r'^update/$', TourProgressUpdateView.as_view(),
        name=TourProgressUpdateView.urlname)
)
