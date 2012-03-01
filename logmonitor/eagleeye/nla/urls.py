from django.conf.urls.defaults import *

urlpatterns = patterns('nla.views',
    (r'nlafc/add/$', 'add_nlafc'),
    (r'nlafc/$', 'nla_fc'),
    (r'nlafc/data/$', 'nla_fc_data'),
    (r'nlafc/summary/$', 'nla_fc_summary'),

    (r'channelnla/add/$', 'add_channelnla'),
    (r'channelnla/output/count/update/$', 'update_channel_outputcount'),
    (r'channelnla/upload/count/update/$', 'update_channel_uploadcount'),
    (r'channelnla/original/$', 'channel_original'),
    (r'channelnla/$', 'channel_nla'),
    (r'channelnla/summary/$', 'channel_nla_summary'),
    (r'channelnla/(?P<channelId>\d+)/data/$', 'channel_nla_data'),
    
    (r'nlatoplist/$', 'nla_toplist'),
    (r'nlatoplist/processsize/data/$', 'process_size_top'),
    (r'nlatoplist/processspeed/data/$', 'process_speed_top'),

    (r'channeltoplist/$', 'channel_toplist'),
    (r'channeltoplist/fileline/data/$', 'file_line_top'),

    (r'monitor/$', 'nla_monitor'),
    (r'monitor/data/$', 'nla_monitor_data'),
    (r'monitor/(?P<nla>.+)/delete/$', 'nla_monitor_delete'),
    (r'(?P<nla>.+)/performance/$', 'nla_performance'),
    (r'(?P<nla>.+)/performance/data/$', 'nla_performance_data'),
    (r'statistic/$', 'nla_statistic'),
    (r'statistic/systemload/$', 'nla_statistic_systemload'),
    (r'statistic/masterdir/$', 'nla_statistic_masterdir'),
    (r'statistic/speed/$', 'nla_statistic_speed'),
    (r'data/add/$', 'add_nla_data'),

    (r'area/$', 'nla_area'),
    (r'area/noderate/data/$', 'nlafc_node_rate'),
    (r'area/cityrate/data/$', 'nlafc_city_rate'),
    (r'area/isprate/data/$', 'nlafc_isp_rate'),
    (r'area/crosschn/data/$', 'nlafc_crosschn_data'),
    (r'area/crosscnc/data/$', 'nlafc_crosscnc_data'),
    (r'area/node/data/$', 'nlafc_node_data'),
    (r'area/city/data/$', 'nlafc_city_data'),
    (r'area/isp/data/$', 'nlafc_isp_data'),
)