from django.conf.urls.defaults import *

urlpatterns = patterns('rcms.views',
    (r'nla/devices/', 'search_nla_devices'),
    (r'fc/devices/', 'search_fc_devices'),
    (r'customers/', 'search_customers'),
    (r'channels/', 'search_channels'),
)