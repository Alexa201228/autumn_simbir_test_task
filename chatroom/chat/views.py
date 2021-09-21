from django.http.response import HttpResponseRedirect
from .forms import EnterRoomForm
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse
from .models import ChatRoom, Message
from django.contrib.sessions.models import Session
from django.utils import timezone


def main_page(request):
    if request.user:
        request.session.flush()
        logout(request)
    if request.method == 'POST':
        form = EnterRoomForm(request.POST)
        if form.is_valid():
            u = User.objects.get_or_create(
                username=form.cleaned_data['username'])
            logged = list(get_all_logged_in_users())
            if not u[0] in logged:
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


def get_all_logged_in_users():
    # Query all non-expired sessions
    # use timezone.now() instead of datetime.now() in latest versions of Django
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    uid_list = []

    # Build a list of user ids from that query
    for session in sessions:
        data = session.get_decoded()
        uid_list.append(data.get('_auth_user_id', None))

    # Query all logged in users based on id list
    return User.objects.filter(id__in=uid_list)