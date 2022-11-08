from django.db import models

class unread_messages(models.Model):
    certificate = models.CharField(max_length=256)
    payload = models.CharField(max_length=2048)
    receiver = models.CharField(max_length=256)


