from django.conf.urls.defaults import *

urlpatterns = patterns('hadoop.views',
    (r'job/$', 'job_list'),
    (r'job/detail/list/$', 'jobs_detail'),
    (r'job/action/$', 'job_action'),
    (r'job/action/failed/$', 'job_action_failed'),
    
    (r'jobs/$', 'jobs_byDay'),
    (r'job/(?P<dbId>\w+)/$', 'get_job'),
    (r'job/detail/query/$', 'get_job_detail'),
    (r'job/dbid/(?P<dbId>\d+)/update/$', 'updateJob_dbId'),
    (r'job/jobid/(?P<jobId>\w+)/update/$', 'updateJob_jobId'),
    (r'jobs/status/(?P<jobDay>\d+)/$', 'jobs_need_update_status'),

    (r'monitor/$', 'hadoop_monitor'),
    (r'monitor/namenode/add/$', 'add_namenode_info'),
    (r'monitor/datanode/add/$', 'add_datanode_info'),
    (r'monitor/datanode/(?P<nodename>.+)/performance/$', 'datanode_performance'),
    (r'monitor/datanode/(?P<nodename>.+)/performance/data/$', 'datanode_performance_data'),
    (r'monitor/datanode/performance/add/$', 'add_datanode_performance'),

    (r'publish/(?P<channel_id>\d+)/$', 'channel_publish'),
    (r'publish/(?P<channel_id>\d+)/data/$', 'channel_publish_data')
)