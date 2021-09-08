from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message
import json


class ChatRoomConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_title = self.scope['url_route']['kwargs']['room_title']
        self.room_group_name = f'chat-{self.room_title}'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        json_data = json.loads(text_data)
        message = json_data['message']
        user = json_data['user_name']
        room = json_data['room_title']

        await self.save_message(user, room, message)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user_name': user,
            }
        )

    @database_sync_to_async
    def save_message(self, username, room, content):
        Message.objects.create(
            author=username, room=room, message_body=content)

    async def chat_message(self, event):
        message = event['message']
        user = event['user_name']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': user,
        }))
