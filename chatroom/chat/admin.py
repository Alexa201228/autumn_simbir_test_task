from django.contrib import admin
from .models import ChatRoom, Message


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['room_name', 'slug']
    prepopulated_fields = {'slug': ('room_name',)}
