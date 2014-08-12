from django.conf.urls.defaults import *

urlpatterns = patterns('corehq.apps.unicel.views',
    url(r'^in/$', 'incoming_auth', name="unicel_incoming_auth"),
    url(r'^in/$', 'incoming'),
)

