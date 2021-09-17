from channels.exceptions import RequestAborted
from django.contrib.auth.models import User, AnonymousUser
from .models import ChatRoom, Message
from django.urls import re_path
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from django.test import Client
from django.test import RequestFactory
from . import views
from django.urls import reverse
from mixer.backend.django import mixer
import pytest
from pytest_django.asserts import assertTemplateUsed

from .consumers import ChatRoomConsumer

"""
Setup for consumer and db
"""
application = URLRouter([
    re_path(r"^testws/(?P<room_title>\w+)/$", ChatRoomConsumer.as_asgi()),
])


@database_sync_to_async
def create_user_and_chatroom(username, room):
    user = get_user_model().objects.create(username=username)
    room = ChatRoom.objects.create(room_name=room)
    return user, room


@database_sync_to_async
def create_message(user, room, content, key):
    message = Message.objects.create(
        author=user,
        room=room,
        message_body=content,
        message_key=key
    )
    return message


"""
ChatConsumer Tests
"""


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_consumer_connected() -> None:
    communicator = WebsocketCommunicator(
        application, '/testws/test_room/')

    connected, _ = await communicator.connect()
    assert connected
    await communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_receiver_with_proper_data() -> None:
    _, _ = await create_user_and_chatroom('user', 'room1')
    communicator = WebsocketCommunicator(
        application, '/testws/test_room/')

    connected, _ = await communicator.connect()
    assert connected
    await communicator.send_json_to({
        'user_name': 'user',
        'room_title': 'room1',
        'message': 'hello',
        'message_key': '1',
        'code': 'save_message'
    })

    await communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_receiver_response() -> None:
    _, _ = await create_user_and_chatroom('user', 'room1')
    communicator = WebsocketCommunicator(
        application, '/testws/test_room/')
    connected, _ = await communicator.connect()
    assert connected
    await communicator.send_json_to({
        'user_name': 'user',
        'room_title': 'room1',
        'message': 'hello',
        'message_key': '1',
        'code': 'save_message'
    })

    response = await communicator.receive_json_from(timeout=5)
    assert response == {
        'message': 'hello',
        'message_key': '1',
        'username': 'user'
    }

    await communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_receiver_throw_request_key_exception() -> None:
    _, _ = await create_user_and_chatroom('user', 'room1')
    communicator = WebsocketCommunicator(
        application, '/testws/test_room/')
    connected, _ = await communicator.connect()
    assert connected
    with pytest.raises(KeyError):
        await communicator.send_json_to({
            'user_name': 'user',
            'room_title': 'room1',
            'message': 'hello',
            'message_key': '1',
        })
        await communicator.wait()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_receiver_throw_request_user_exception() -> None:
    _, _ = await create_user_and_chatroom('user', 'room1')
    communicator = WebsocketCommunicator(
        application, '/testws/test_room/')
    connected, _ = await communicator.connect()
    assert connected
    with pytest.raises(User.DoesNotExist):
        await communicator.send_json_to({
            'user_name': 'Carl',
            'room_title': 'room1',
            'message': 'hello',
            'message_key': '1',
            'code': 'save_message'
        })
        await communicator.wait()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_receiver_throw_request_common_exception() -> None:
    _, _ = await create_user_and_chatroom('user', 'room1')
    communicator = WebsocketCommunicator(
        application, '/testws/test_room/')
    connected, _ = await communicator.connect()
    assert connected
    with pytest.raises(RequestAborted):
        await communicator.send_json_to({
            'user_name': 'user',
            'room_title': 'room2',
            'message': 'hello',
            'message_key': '1',
            'code': 'save_message'
        })
        await communicator.wait()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_receiver_send_proper_data_after_change_message() -> None:
    user, room = await create_user_and_chatroom('user', 'room1')
    _ = await create_message(user, room, 'goodbye', '1')
    communicator = WebsocketCommunicator(
        application, '/testws/test_room/')
    connected, _ = await communicator.connect()
    assert connected

    await communicator.send_json_to({
        'user_name': 'user',
        'room_title': 'room1',
        'message': 'goodbye',
        'message_key': '1',
        'code': 'change_message'
    })
    response = await communicator.receive_json_from(timeout=5)
    assert response == {
        'message': 'goodbye',
        'message_key': '1',
        'changed': True
    }
    await communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_receiver_send_proper_data_after_delete_message() -> None:
    user, room = await create_user_and_chatroom('user', 'room1')
    _ = await create_message(user, room, 'goodbye', '1')
    communicator = WebsocketCommunicator(
        application, '/testws/test_room/')
    connected, _ = await communicator.connect()
    assert connected
    await communicator.send_json_to({
        'user_name': 'user',
        'message_key': '1',
        'code': 'delete_message'
    })
    response = await communicator.receive_json_from(timeout=5)
    assert response == {
        'message': 'Сообщение удалено',
        'message_key': '1',
        'delete': True
    }

    await communicator.disconnect()


"""
Tests for views
"""


@pytest.mark.django_db(transaction=True)
class TestChatViews:
    """
    Access to list of chat rooms if user is authenticated
    """

    def test_chat_list_user_is_authenticated(self):
        path = reverse('chat:chat_selection')
        request = RequestFactory().get(path)
        request.user = mixer.blend(User)
        response = views.chat_selection(request)
        assert response.status_code == 200

    """
    If user is not authenticated should be redirected to homepage
    """

    def test_chat_list_user_is_not_authenticated(self):
        path = reverse('chat:chat_selection')
        request = RequestFactory().get(path)
        request.user = AnonymousUser()
        response = views.chat_selection(request)
        assert '/login-chat' in response.url

    """
    Access to chat room if user is authenticated
    """

    def test_chat_room_user_is_authenticated(self):
        path = reverse('chat:room', kwargs={'room_title': 'room1'})
        request = RequestFactory().get(path)
        request.user = mixer.blend(User)
        response = views.room(request, 'room1')
        assert response.status_code == 200

    """
    If user is not authenticated should be redirected to homepage
    """

    def test_chat_room_user_is_not_authenticated(self):
        path = reverse('chat:room', kwargs={'room_title': 'room1'})
        request = RequestFactory().get(path)
        request.user = AnonymousUser()
        response = views.room(request, 'room1')
        assert '/login-chat' in response.url

    """
    If user tries to access room that does not exist
    """

    def test_chat_room_user_access_not_existed_room(self):
        User.objects.create(username='user')
        c = Client()
        c.login(username='user')
        response = c.get('/chat/rrr/')
        assertTemplateUsed(response, 'exception.html')

    def test_chat_load_homepage(self):
        c = Client()
        response = c.get('/')
        assertTemplateUsed(response, 'homepage.html')

    def test_chat_load_login_for_unauthorized_user(self):
        c = Client()
        response = c.get('/login-chat/')
        assertTemplateUsed(response, 'login.html')


"""
Test chat models
"""


@pytest.mark.django_db(transaction=True)
class TestChatModels:

    def test_chat_room_model_set_slug_on_save(self):
        room = mixer.blend(ChatRoom, room_name='Наука')
        assert str(room) == 'Наука'

    def test_chat_message_model(self):
        message = mixer.blend(
            Message,
            author=mixer.blend(User),
            message_body='hello',
            message_key='1'
        )
        assert message.message_body == 'hello'
        assert message.changed == False
