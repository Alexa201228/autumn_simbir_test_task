from django.shortcuts import render


def main_page(request):
    return render(
        request,
        'homepage.html',
        {}
    )


def room(request, room_title):
    return render(
        request,
        'chatroom.html',
        {
            'room_title': room_title
        })
