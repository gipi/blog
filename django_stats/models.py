from django.db import models

"""
TODO: add cron job to schedule clean up of expired session keys.
"""
class StatsSession(models.Model):
    session_key = models.CharField(max_length=40)

    def __unicode__(self):
        return self.session_key

class Stats(models.Model):
    """
    This class counts how many unique visitors for page
    there are. The unique is calculated by the session_key.
    """
    page_path = models.CharField(max_length=100)
    session_keys = models.ManyToManyField(StatsSession)
    counter = models.IntegerField()
