from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT}),
    (r'^$', 'views.index'),
)

urlpatterns += patterns('',
    (r'^publisher/', include('publisher.urls')),
    (r'^rcms/', include('rcms.urls')),
    (r'^lcer/', include('lcer.urls')),
    (r'^nla/', include('nla.urls')),
    (r'^hadoop/', include('hadoop.urls')),
    (r'^mobile/', include('mobile.urls')),
    (r'^refresh/', include('refresh.urls')),
    (r'^fc/', include('fc.urls')),
)
