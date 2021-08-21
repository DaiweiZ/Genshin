from django.urls import path, reverse_lazy

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home/content', views.content_list, name='content'),
    path('home/upload', views.content_upload, name='upload'),
    path('home/random', views.random, name='random'),
]