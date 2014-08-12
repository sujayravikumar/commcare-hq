from django.conf.urls.defaults import *

urlpatterns = patterns('corehq.apps.twilio.views',
    url(r'^sms/(?P<api_key>[\w-]+)/$', 'sms_in_auth', name='twilio_sms_in_auth'),
    url(r'^sms/?$', 'sms_in', name='twilio_sms_in'),
)
