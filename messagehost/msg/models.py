from django.db import models

class unread_messages(models.Model):
    sender = models.CharField(max_length=2048)
    payload = models.CharField(max_length=4096)
    receiver = models.CharField(max_length=64)
    signature = models.CharField(max_length=512)

class public_keys(models.Model):
    username = models.CharField(max_length=64,unique=True)
    public_key = models.CharField(max_length=2048)

