from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify


class ChatRoom(models.Model):
    room_name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150)


class Message(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_messages'
    )
    room = models.ForeignKey(
        ChatRoom, on_delete=models.CASCADE, related_name='chat_messages')
    message_body = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
    message_key = models.CharField(max_length=200)
    changed = models.BooleanField(default=False)

    class Meta:
        ordering = ('date_sent',)
