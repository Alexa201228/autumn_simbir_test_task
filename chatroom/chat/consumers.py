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
        """
        Ресивер принимает сообщения на изменение и удаление
        сообщений
        """
        json_data = json.loads(text_data)
        message = json_data.get('message')
        user = json_data.get('user_name')
        room = json_data.get('room_title')
        message_key = json_data.get('message_key')

        if message_key and not user:
            await self.delete_message(message_key)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'delete_chat_message',
                    'message': 'Message deleted',
                    'message_key': message_key,
                }
            )
        else:
            await self.save_message(user, room, message, message_key)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user_name': user,
                    'message_key': message_key,
                }
            )

    @database_sync_to_async
    def save_message(self, username, room, content, message_key):
        Message.objects.create(
            author=username, room=room, message_body=content, message_key=message_key)

    @database_sync_to_async
    def delete_message(self, message_key):
        Message.objects.filter(message_key=message_key).delete()

    async def chat_message(self, event):
        message = event['message']
        user = event['user_name']
        message_key = event['message_key']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': user,
            'message_key': message_key
        }))

    async def delete_chat_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message,

        }))
