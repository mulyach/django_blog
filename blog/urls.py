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
    path('signature/', views.signature, name='signature')
    #path('test_stream',views.test_stream,name='stream'),
    #path('add comment/<int:article_id>/', views.add_comment, name='add comment')
]