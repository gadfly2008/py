from django.conf.urls.defaults import *

urlpatterns = patterns('refresh.views',
    (r'summary/$', 'summary'),
    (r'detail/$', 'detail'),
    (r'detail/url/data/$', 'detail_url_data'),
    (r'detail/url/(?P<urlId>\w+)/devices/$', 'detail_url_devices'),
    (r'detail/url/devices/sort/$', 'detail_url_devices_sort'),
    (r'detail/top/data/$', 'detail_top_data'),
    (r'detail/total/data/$', 'detail_total_data'),
    (r'detail/channeltop/data/$', 'detail_channeltop_data'),
    (r'detail/urltop/data/$', 'detail_urltop_data'),

    (r'statistic/$', 'statistic'),
)