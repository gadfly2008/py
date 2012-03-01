from django.db import models

class NLAFc(models.Model):
    nlasn = models.CharField(max_length=20)
    fcsn = models.CharField(max_length=20)
    datetime = models.DateTimeField()
    fcount = models.BigIntegerField()
    fsize = models.BigIntegerField()

    class Meta:
        ordering = ["id"]
        unique_together = ("nlasn", "fcsn", "datetime")

    def __unicode__(self):
        return self.nlasn

class ChannelNla(models.Model):
    channelId = models.BigIntegerField()
    userId = models.BigIntegerField()
    nlasn = models.CharField(max_length=20)
    datetime = models.DateTimeField()
    size = models.BigIntegerField()
    output_count = models.BigIntegerField(null=True, blank=True)
    upload_count = models.BigIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["id"]
        unique_together = ("channelId", "nlasn", "datetime")

    def __unicode__(self):
        return "%s" %(self.channelId, )

class Directory(models.Model):
    hostname = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    count = models.BigIntegerField()
    size = models.BigIntegerField()
    datetime = models.DateTimeField()
    vsftp = models.CharField(max_length=20)
    level = models.BigIntegerField()
    health = models.BigIntegerField()

    class Meta:
        ordering = ["id"]
        unique_together = ("hostname", "vsftp")

    def __unicode__(self):
        return self.hostname

class Block(models.Model):
    hostname = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    used = models.BigIntegerField()
    level = models.BigIntegerField()

    class Meta:
        ordering = ["id"]

    def __unicode__(self):
        return self.hostname

class Performance(models.Model):
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