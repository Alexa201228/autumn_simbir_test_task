from django.http.response import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from .forms import EnterRoomForm
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse
from .models import ChatRoom, Lobby, Message


def main_page(request):
    if request.user:
        Lobby.objects.filter(users_online=request.user.id).delete()
        logout(request)
    if request.method == 'POST':
        form = EnterRoomForm(request.POST)
        if form.is_valid():
            u = User.objects.get_or_create(
                username=form.cleaned_data['username'])
            if len(Lobby.objects.filter(users_online=u[0])) == 0:
                Lobby.objects.create(users_online=u[0])
                user = authenticate(username=form.cleaned_data['username'])
                login(request, user)
                return HttpResponseRedirect(reverse(
                    'chat:chat_selection'
                ))
            else:
                return HttpResponseRedirect(reverse('chat:login', kwargs={
                    'forbidden': True
                }))
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


def login_chat(request, forbidden=False):
    if forbidden:
        return render(
            request,
            'login.html',
            {'forbidden': True}
        )
    return render(
        request,
        'login.html',
        {}
    )
