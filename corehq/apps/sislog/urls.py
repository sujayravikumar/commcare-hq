from django.conf.urls.defaults import *

urlpatterns = patterns('corehq.apps.sislog.views',
    url(r'^in/(?P<api_key>[\w-]+)/$', 'sms_in_auth', name='sislog_sms_in_auth'),
    url(r'^in/?$', 'sms_in', name='sms_in'),
)
