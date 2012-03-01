from django.conf.urls.defaults import *

urlpatterns = patterns('publisher.views',
    (r'daywarning/$', 'day_warning'),
    (r'daywarning/detail/$', 'daywarn_detail'),
    (r'daywarning/chartheight/$', 'get_chartSize'),
    
    (r'total/add/$', 'add_total_logpublish'),
    (r'publishtotal/$', 'publish_total'),
    (r'publishtotal/data/$', 'total_data'),
    (r'publishtotal/multi/data/$', 'multi_total_data'),
    (r'publishyear/data/$', 'publish_year_data'),

    (r'publish/add/$', 'add_logpublish'),
    (r'publishdetail/$', 'publish_detail'),
    (r'publishdetail/data/$', 'publish_detail_data'),

    (r'publishdelay/$', 'publish_delay'),
    (r'publishdelay/summary/$', 'publish_delay_summary'),
    (r'publishdelay/data/$', 'publish_delay_data'),
    (r'publishdelay/add/$', 'add_publish_delay'),

    (r'toplist/$', 'toplist'),
    (r'toplist/user/data/$', 'toplist_user'),
    (r'toplist/channel/data/$', 'toplist_channel'),
)