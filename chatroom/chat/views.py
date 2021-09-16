from django.http.response import HttpResponseRedirect
from .forms import EnterRoomForm
from django.shortcuts import redirect, render
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.urls import reverse
from .models import ChatRoom, Message


def main_page(request):
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


def room(request, room_title):
    room = ChatRoom.objects.get(slug=room_title)
    messages = Message.objects.filter(room=room.id)
    return render(
        request,
        'chatroom.html',
        {
            'room': room,
            'messages': messages
        })


@login_required
def chat_selection(request):
    print(request.user)
    rooms = ChatRoom.objects.all()
    if(request.user == AnonymousUser):
        redirect('/')
    return render(
        request,
        'enterRoom.html',
        {
            'rooms': rooms
        }
    )
