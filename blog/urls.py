from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('blog/', views.blog, name='blog'),
    path('article/create/', views.article_create, name='article_create'),
    path('article/<slug:slug>/', views.article_detail, name='article_detail'),
    path('article/<slug:slug>/update/', views.article_update, name='article_update'),
    path('article/<slug:slug>/delete/', views.article_delete, name='article_delete'),
    path('article/<slug:slug>/publish/', views.publish_article, name='publish_article'),
    path('article/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('my_article/', views.my_article, name='my_article'),
]
