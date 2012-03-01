from django.db import models

class LogPublish(models.Model):
    customer_id = models.CharField(max_length=10)
    channel_id = models.CharField(max_length=10)
    datetime = models.DateTimeField()
    size = models.BigIntegerField()

    class Meta:
        ordering = ['id']
        unique_together = (("datetime","customer_id"),("datetime", "channel_id"))

    def __unicode__(self):
        return "%s" %(self.channel_id,)

class LogPublishTotal(models.Model):
    datetime = models.DateTimeField()
    size = models.BigIntegerField()
    source = models.CharField(max_length=100)
    
    class Meta:
        ordering = ['id']
        unique_together = ("datetime","source")
        
    def __unicode__(self):
        return self.source

class LogPublishDelay(models.Model):
    datetime = models.DateTimeField()
    size = models.BigIntegerField()
    source = models.CharField(max_length=100)
    user_name = models.CharField(max_length=20)

    class Meta:
        ordering = ["id"]
        unique_together = ("datetime", "user_name", "source")

    def __unicode__(self):
        return self.user_name