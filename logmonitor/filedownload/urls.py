from django.conf import settings
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT}),
)

urlpatterns += patterns('views',
    url(r'^$', 'index'),
    url(r'^gzip/(?P<pubDate>\d+)/(?P<userId>\d+)/(?P<channelId>\d+)/(?P<ptype>.+)/$', 'response_gzip'),
    url(r'^zip/(?P<pubDate>\d+)/(?P<userId>\d+)/(?P<channelId>\d+)/(?P<ptype>.+)/$', 'response_zip'),
)