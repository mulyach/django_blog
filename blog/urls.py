from django.urls import path
from . import views

app_name = 'blog'
urlpatterns = [
    path('',views.index,name='index'),
    path('article/<int:article_id>/', views.show_article, name='show_article'),
    path('category/<str:category_label>', views.category_list, name='category_list'),
    path('compose/<username>', views.compose, name='compose'),
    path('upload_image/<username>', views.upload_image, name='image'),
    path('my_articles/<username>', views.my_articles_list, name='my_articles'),
    path('signature/', views.signature, name='signature'),
    path('board/', views.board, name='board'),
    path('chat/', views.chat_lobby, name='chat_lobby'),
    path('chat/<room_name>/', views.chat_room, name='chat_room'),
    path('cs_chat_monitor/<username>/', views.cs_chat_monitor, name='cs_chat_monitor'),    
    path('cs_chat/<room_name>/<username>/', views.cs_chat_room, name='cs_chat_room'),
    #path('start_comm', views.start_comm, name='start_comm'),
    path('send_OTP/<message>', views.send_OTP, name='send_OTP'),
    path('enter_OTP/<mobileno>/<message>', views.enter_OTP, name='enter_OTP'),
]