from django.http.response import HttpResponseRedirect
from .forms import EnterRoomForm
from django.shortcuts import redirect, render
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse
from .models import ChatRoom, Message


def main_page(request):
    if request.user:
        logout(request)
    if request.method == 'POST':
        form = EnterRoomForm(request.POST)
        if form.is_valid():
            User.objects.get_or_create(
                username=form.cleaned_data['username'])
            user = authenticate(username=form.cleaned_data['username'])
            login(request, user)
            return HttpResponseRedirect(reverse(
                'chat:chat_selection'
            ))
    else:
        form = EnterRoomForm()
        return render(
            request,
            'homepage.html',
            {
                'form': form
            }
        )


@login_required(redirect_field_name=None, login_url='/login-chat')
def room(request, room_title):
    try:
        room = ChatRoom.objects.get(slug=room_title)
        messages = Message.objects.filter(room=room.id)
        return render(
            request,
            'chatroom.html',
            {
                'room': room,
                'messages': messages
            })
    except ChatRoom.DoesNotExist as e:
        return render(
            request,
            'exception.html',
            {
                'error': e
            }
        )

    except Exception:
        return render(
            request,
            'exception.html',
            {}
        )


@login_required(redirect_field_name=None, login_url='/login-chat')
def chat_selection(request):
    rooms = ChatRoom.objects.all()
    return render(
        request,
        'enterRoom.html',
        {
            'rooms': rooms
        }
    )


def login_chat(request):
    return render(
        request,
        'login.html',
        {}
    )
