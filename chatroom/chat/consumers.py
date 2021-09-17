from types import FunctionType
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.exceptions import RequestAborted
from django.contrib.auth.models import User
from .models import ChatRoom, Message
import json


class ChatRoomConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_title = self.scope['url_route']['kwargs']['room_title']
        self.user = self.scope.get('user', None)
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
        Ресивер принимает сообщения на сохранение,
        изменение и удаление сообщений
        """
        try:
            json_data = json.loads(text_data)
            message = json_data.get('message')
            user = json_data.get('user_name')
            room = json_data.get('room_title')
            message_key = json_data.get('message_key')
            code = json_data.get('code')
            data = {'user': user,
                    'room': room,
                    'message': message,
                    'message_key': message_key}

            await self.operate_with_message_by_code[code](self, **data)
            await self.send_message_by_code(code, **data)
        except KeyError:
            raise KeyError
        except User.DoesNotExist:
            raise User.DoesNotExist
        except Exception:
            raise RequestAborted

    @database_sync_to_async
    def save_message(self, **kwargs):
        user = User.objects.get(username=kwargs['user'])
        room = ChatRoom.objects.get(slug=kwargs['room'])
        Message.objects.create(
            author=user,
            room=room,
            message_body=kwargs['message'],
            message_key=kwargs['message_key'])

    @database_sync_to_async
    def delete_message(self, **kwargs):
        Message.objects.filter(
            message_key=kwargs['message_key'],
            author=User.objects.get(username=kwargs['user'])).delete()

    @database_sync_to_async
    def change_message(self, **kwargs):
        user = User.objects.get(username=kwargs['user'])
        room = ChatRoom.objects.get(slug=kwargs['room'])
        changed_message = Message.objects.get(
            author=user,
            room=room,
            message_key=kwargs['message_key'])
        changed_message.message_body = kwargs['message']
        changed_message.changed = True
        changed_message.save()

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
        message_key = event['message_key']
        message = event['message']

        await self.send(text_data=json.dumps({
            'message_key': message_key,
            'message': message,
            'delete': True
        }))

    async def change_chat_message(self, event):
        message = event['message']
        message_key = event['message_key']

        await self.send(text_data=json.dumps({
            'message': message,
            'message_key': message_key,
            'changed': True
        }))

    async def send_message_by_code(self, code, **kwargs):
        if code == 'delete_message':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'delete_chat_message',
                    'message': 'Сообщение удалено',
                    'message_key': kwargs['message_key'],
                }
            )
        elif code == 'change_message':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'change_chat_message',
                    'message': kwargs['message'],
                    'message_key': kwargs['message_key'],
                }
            )

        else:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': kwargs['message'],
                    'user_name': kwargs['user'],
                    'message_key': kwargs['message_key'],
                }
            )

    """
    Коды для динамической обработки и отправки сообщений
    """
    operate_with_message_by_code: dict[str, FunctionType] = {
        'save_message': save_message,
        'delete_message': delete_message,
        'change_message': change_message,
    }
