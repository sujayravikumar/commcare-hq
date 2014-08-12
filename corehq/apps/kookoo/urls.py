from django.conf.urls.defaults import *

urlpatterns = patterns('corehq.apps.kookoo.views',
    url(r'^ivr/(?P<api_key>[\w-]+)/$', 'ivr_auth', name='kookoo_ivr_auth'),
    url(r'^ivr_finished/(?P<api_key>[\w-]+)/$', 'ivr_finished_auth', name='kookoo_ivr_finished_auth'),
    url(r'^ivr/?$', 'ivr', name='ivr'),
    url(r'^ivr_finished/?$', 'ivr_finished', name='ivr_finished'),
)
