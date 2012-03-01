from django.db import models

class Directory(models.Model):
    hostname = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    count = models.BigIntegerField()
    size = models.BigIntegerField()
    time = models.DateTimeField()

    class Meta:
        ordering = ['id']
        unique_together = ("time", "hostname", "name")
    
    def __unicode__(self):
        return self.hostname

class Block(models.Model):
    hostname = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    used = models.BigIntegerField()
    
    class Meta:
        ordering = ['id']
        
    def __unicode__(self):
        return self.hostname