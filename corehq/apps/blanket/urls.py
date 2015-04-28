from django.conf.urls import *
from .views import BlanketListView, BlanketShowView

urlpatterns = patterns('corehq.apps.blanket.views',
    url(r'^show/(?P<blanket_id>[\w-]+)/$', BlanketShowView.as_view(), name=BlanketShowView.urlname),
    url(r'^$', BlanketListView.as_view(), name=BlanketListView.urlname),
)
