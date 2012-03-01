from django.conf.urls.defaults import *

urlpatterns = patterns('lcer.views',
    (r'lcer/summary/$', 'lcer_summary'),
    (r'blockmonitor/$', 'block_monitor'),
    (r'blockmonitor/detail/$', 'block_detail'),
    
    (r'(?P<lc>.+)/dirs/$', 'get_lcDirs'),
    
    (r'data/add/$', 'add_lc_data'),
)