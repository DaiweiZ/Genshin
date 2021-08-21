from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.template import loader
from home.models import Ad, Comment,Fav



def index(request):
    #return HttpResponse("Hello, world. You're at Daiwei's website.")

    template = loader.get_template('home/index.html')
    context = {
        'latest_question_list': 1,
    }

    return HttpResponse(template.render(context, request))


def content_list(request):
    template = loader.get_template('home/content_list.html')
    context = {
        'latest_question_list': 1,
    }

    return HttpResponse(template.render(context, request))


def content_upload(request):
    template = loader.get_template('home/content_manage.html')
    context = {
        'latest_question_list': 1,
    }

    return HttpResponse(template.render(context, request))


def random(request):
    template = loader.get_template('home/random_content.html')
    context = {
        'latest_question_list': 1,
    }

    return HttpResponse(template.render(context, request))

# path('content', views.content_list, name='content'),
# path('upload', views.content_upload, name='upload'),
# path('random', views.random, name='random'),