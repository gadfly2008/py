from django.conf.urls.defaults import *

urlpatterns = patterns('fc.views',
    (r'fcoriginal/$', 'fc_original'),
    (r'fcoriginal/data/$', 'fc_original_data'),
    (r'fcoriginal/add/$', 'add_fc_original'),
)