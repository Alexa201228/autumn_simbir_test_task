from django.urls import path

from . import views

urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('chat/', views.chat_selection, name='chat_selection'),
    path('chat/<str:room_title>/', views.room, name='room'),
    path('login-chat/', views.login_chat, name='login'),
    path(r'login-chat/(?P<forbidden>\w+)/$', views.login_chat, name='login'),
]
