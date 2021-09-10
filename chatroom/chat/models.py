from django.db import models


class Message(models.Model):
    author = models.CharField(max_length=200)
    room = models.CharField(max_length=200)
    message_body = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
    message_key = models.CharField(max_length=200)

    class Meta:
        ordering = ('date_sent',)
