from django.conf.urls.defaults import *

urlpatterns = patterns('corehq.apps.tropo.views',
    url(r'^sms/(?P<api_key>[\w-]+)/$', 'sms_in_auth', name='tropo_sms_in_auth'),
    url(r'^ivr/(?P<api_key>[\w-]+)/$', 'ivr_in_auth', name='tropo_ivr_in_auth'),
    url(r'^sms/?$', 'sms_in', name='sms_in'),
    url(r'^ivr/?$', 'ivr_in', name='ivr_in'),
)
