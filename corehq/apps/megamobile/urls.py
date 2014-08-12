from django.conf.urls.defaults import *

urlpatterns = patterns('corehq.apps.megamobile.views',
    url(r'^sms/(?P<api_key>[\w-]+)/$', 'sms_in_auth', name='megamobile_sms_in_auth'),
    url(r'^sms/?$', 'sms_in', name='sms_in'),
)
