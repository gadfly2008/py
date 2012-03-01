from django.db import models

class ChannelJob(models.Model):
    user_id = models.CharField(max_length=10)
    user_name = models.CharField(max_length=50)
    channel_id = models.CharField(max_length=10)
    channel_name = models.CharField(max_length=255)
    priority = models.BigIntegerField()
    source_path = models.CharField(max_length=255)
    source_fline = models.BigIntegerField(null=True, blank=True)
    source_fsize = models.BigIntegerField(null=True, blank=True)
    target_path = models.CharField(max_length=255)
    target_fline = models.BigIntegerField(null=True, blank=True)
    target_fsize = models.BigIntegerField(null=True, blank=True)
    job_execute_time = models.BigIntegerField(null=True, blank=True)
    job_id = models.CharField(max_length=50, null=True, blank=True)
    job_name = models.CharField(max_length=100, null=True, blank=True)
    status = models.BigIntegerField()
    job_day  =  models.DateTimeField()
    update_time = models.DateTimeField()
    description = models.CharField(max_length=255, null=True, blank=True)
    pub_mime_filter = models.CharField(max_length=255)
    pub_url_filter = models.CharField(max_length=255)
    pub_way = models.CharField(max_length=20)
    pub_is_filter = models.CharField(max_length=10)
    pub_format_type = models.CharField(max_length=100)
    pub_ftp_ip = models.CharField(max_length=100)
    pub_ftp_port = models.BigIntegerField()
    pub_ftp_dir = models.CharField(max_length=255)
    pub_ftp_user = models.CharField(max_length=50)
    pub_ftp_passwd = models.CharField(max_length=255)
    
    class Meta:
        ordering = ["id"]
        unique_together = ("job_day", "channel_id")

    def __unicode__(self):
        return self.channel_name

class NameNodeInfo(models.Model):
    configured_capacity = models.BigIntegerField()
    present_capacity = models.BigIntegerField()
    dfs_remaining = models.BigIntegerField()
    dfs_used = models.BigIntegerField()
    dfs_usedper = models.FloatField()
    total_datanode = models.BigIntegerField()
    dead_datanode = models.BigIntegerField()
    update_time = models.DateTimeField()

    class Meta:
        ordering = ["id"]

    def __unicode__(self):
        return self.configured_capacity

class DataNodeInfo(models.Model):
    name = models.CharField(max_length=255, unique=True)
    decommission_status = models.CharField(max_length=255)
    configured_capacity = models.BigIntegerField()
    dfs_remaining = models.BigIntegerField()
    dfs_used = models.BigIntegerField()
    dfs_usedper = models.FloatField()
    dfs_remainingper = models.FloatField()
    non_dfs_used = models.BigIntegerField()
    last_contact = models.DateTimeField()
    update_time = models.DateTimeField()

    class Meta:
        ordering = ["id"]

    def __unicode__(self):
        return self.name

class DataNodePerformance(models.Model):
    hostname = models.CharField(max_length=50)
    datetime = models.DateTimeField()
    load_user = models.CharField(max_length=100)
    load_average = models.CharField(max_length=100)
    cpu_us = models.CharField(max_length=100)
    cpu_idle = models.CharField(max_length=100)
    memory_free = models.CharField(max_length=100)
    io_await = models.CharField(max_length=100)
    io_idle = models.CharField(max_length=100)

    class Meta:
        ordering = ["id"]
        unique_together = ("hostname", "datetime")

    def __unicode__(self):
        return self.hostname