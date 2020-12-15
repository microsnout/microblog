from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.conf import settings

class Visitor(models.Model):
    name = models.CharField(max_length=40)
    pin = models.CharField(max_length=6)
    last_visit = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-last_visit',)

    def __str__(self):
        return self.name + ':' + self.pin

