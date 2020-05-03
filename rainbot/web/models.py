from django.db import models


class RainBot(models.Model):
    access_key = models.CharField(max_length=20)
    name = models.CharField(max_length=20)
    wifi = models.IntegerField()
    battery = models.FloatField()


class RainDrop(models.Model):
    rainbot = models.ForeignKey(RainBot, related_name='drops',
                                on_delete=models.CASCADE)
    time = models.DateTimeField()
    data = models.FloatField()
