from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=100)
    customerId = models.BigIntegerField(unique=True)

    class Meta:
        ordering = ['id']
    
    def __unicode__(self):
        return self.name

class Channel(models.Model):
    customer = models.ForeignKey(Customer)
    name = models.CharField(max_length=255)
    channelId = models.BigIntegerField(unique=True)

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return self.name

class Device(models.Model):
    name = models.CharField(max_length=50)
    sn = models.CharField(max_length=20,unique=True)
    app = models.CharField(max_length=10)

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return self.name