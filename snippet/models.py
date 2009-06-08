from django.db import models

class Entry(models.Model):
    content = models.CharField(max_length=1000)
