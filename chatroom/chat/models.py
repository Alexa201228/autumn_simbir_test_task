from django.contrib.auth.models import User
from django.db import models
from unidecode import unidecode


class ChatRoom(models.Model):
    room_name = models.CharField(
        max_length=100, verbose_name='Название комнаты')
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True, verbose_name='Описание комнаты')

    def __str__(self):
        return self.room_name

    def save(self, *args, **kwargs):
        # Если создание комны не из панели админа
        # то присваиваем slug к транслиту кириллицы
        if not self.slug:
            self.slug = unidecode(self.room_name)
        super().save(*args, **kwargs)


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
