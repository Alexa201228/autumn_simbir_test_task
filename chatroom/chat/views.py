from django.shortcuts import render
from .models import Message


def main_page(request):
    return render(
        request,
        'homepage.html',
        {}
    )


def room(request, room_title):
    messages = Message.objects.filter(room=room_title)

    return render(
        request,
        'chatroom.html',
        {
            'room_title': room_title,
            'messages': messages
        })
