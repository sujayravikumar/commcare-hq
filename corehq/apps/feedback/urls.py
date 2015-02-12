from django.conf.urls import patterns, url


urlpatterns = patterns(
    'corehq.apps.feedback.views',
    url(r'^$', 'feedback_home', name='feedback_home'),

)
