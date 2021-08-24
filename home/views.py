from urllib import request

from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.template import loader
from home.models import Ad, Comment, Fav
from home.forms import CreateForm, CommentForm
from home.owner import OwnerListView, OwnerDetailView, OwnerDeleteView
from django.db import connection
from django.db.models import Q
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import NewUserForm
from django.contrib import messages
from django.contrib.auth import login, authenticate
import requests
import re
from bs4 import BeautifulSoup
import urllib
import json

def index(request):
    #return HttpResponse("Hello, world. You're at Daiwei's website.")

    template = loader.get_template('home/index.html')
    context = {
        'latest_question_list': 1,
    }

    return HttpResponse(template.render(context, request))


def content_list(request):
    model = Ad
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
    # list_1 = []
    template = loader.get_template('home/random_content.html')
    # r = requests.get('https://www.youtube.com/c/GenshinImpact/videos')
    # soup = BeautifulSoup(r.text, 'html.parser')
    # print(r.text)
    # html_list = []
    # for i in soup.select('.yt-simple-endpoint .inline-block .style-scope .ytd-thumbnail a'):
    #     print(i['href'])
    #     html_list.append(i['href'])

    video_links = get_all_video_in_channel('UCiS882YPwZt1NfaM0gR0D9Q')
    print(video_links)
    context = {
        'htmls':  json.dumps(video_links),
    }

    return HttpResponse(template.render(context, request))



#https://stackoverflow.com/questions/15512239/python-get-all-youtube-video-urls-of-a-channel
def get_all_video_in_channel(channel_id):
    api_key = 'AIzaSyClUdFrF56ziHPC9WniRtoCDE_wo2KiQzc'

    base_video_url = 'https://www.youtube.com/embed/'
    base_search_url = 'https://www.googleapis.com/youtube/v3/search?'

    first_url = base_search_url+'key={}&channelId={}&part=snippet,id&order=date&maxResults=25'.format(api_key, channel_id)

    video_links = []
    url = first_url
    while True:
        inp = request.urlopen(url)
        resp = json.load(inp)

        for i in resp['items']:
            if i['id']['kind'] == "youtube#video":
                video_links.append(base_video_url + i['id']['videoId'])

        try:
            next_page_token = resp['nextPageToken']
            url = first_url + '&pageToken={}'.format(next_page_token)
        except:
            break
    return video_links

# https://stackoverflow.com/questions/1074212/how-can-i-see-the-raw-sql-queries-django-is-running
def dump_queries() :
    qs = connection.queries
    for q in qs:
        print(q)


class AdListView(OwnerListView):
    model = Ad
    template_name = "home/content_list.html"

    def get(self, request) :
        ad_list = Ad.objects.all()
        favorites = list()
        strval = request.GET.get("search", False)
        if strval :
            # Simple title-only search
            # objects = Post.objects.filter(title__contains=strval).select_related().order_by('-updated_at')[:10]

            # Multi-field search
            # __icontains for case-insensitive search
            query = Q(title__icontains=strval)
            query.add(Q(text__icontains=strval), Q.OR)
            query.add(Q(tags__name__in=[strval]), Q.OR)
            ad_list = Ad.objects.filter(query).select_related().order_by('-updated_at')[:10]
        else :
            ad_list = Ad.objects.all().order_by('-updated_at')[:10]

        # Augment the post_list
        for obj in ad_list:
            obj.natural_updated = naturaltime(obj.updated_at)


        # if request.user.is_authenticated:
        #     # rows = [{'id': 2}, {'id': 4} ... ]  (A list of rows)
        #     rows = request.user.favorite_ads.values('id')
        #     # favorites = [2, 4, ...] using list comprehension
        #     favorites = [ row['id'] for row in rows ]
        ctx = {'ad_list' : ad_list, 'search': strval}

        dump_queries()

        return render(request, self.template_name, ctx)



# class AdDetailView(OwnerDetailView):
#     model = Ad
#     template_name = "ads/ad_detail.html"
#
#     def get(self, request, pk) :
#         x = Ad.objects.get(id=pk)
#         comments = Comment.objects.filter(ad=x).order_by('-updated_at')
#         comment_form = CommentForm()
#         context = { 'ad' : x, 'comments': comments, 'comment_form': comment_form }
#         return render(request, self.template_name, context)
#

class AdCreateView(LoginRequiredMixin, View):
    template_name = 'home/content_manage.html'
    success_url = reverse_lazy('home:content')

    def get(self, request, pk=None):
        form = CreateForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        form = CreateForm(request.POST, request.FILES or None)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        # Add owner to the model before saving
        pic = form.save(commit=False)
        pic.owner = self.request.user
        pic.save()
        return redirect(self.success_url)

#
# class AdUpdateView(LoginRequiredMixin, View):
#     template_name = 'ads/ad_form.html'
#     success_url = reverse_lazy('ads:all')
#
#
#     def get(self, request, pk):
#         pic = get_object_or_404(Ad, id=pk, owner=self.request.user)
#         form = CreateForm(instance=pic)
#         ctx = {'form': form}
#         return render(request, self.template_name, ctx)
#
#     def post(self, request, pk=None):
#         pic = get_object_or_404(Ad, id=pk, owner=self.request.user)
#         form = CreateForm(request.POST, request.FILES or None, instance=pic)
#
#         if not form.is_valid():
#             ctx = {'form': form}
#             return render(request, self.template_name, ctx)
#
#         pic = form.save(commit=False)
#         pic.save()
#
#         return redirect(self.success_url)
#
#     fields = ['title', 'text', 'price', 'tags']
#
# class AdDeleteView(OwnerDeleteView):
#     model = Ad

def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            form.save()
        username = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=raw_password)
        login(request, user)
        messages.success(request, "Registration successful.")
        return redirect("main:homepage")
    messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(request=request, template_name="registration/register.html", context={"register_form": form})


def stream_file(request, pk):
    ad = get_object_or_404(Ad, id=pk)
    response = HttpResponse()
    response['Content-Type'] = ad.content_type
    response['Content-Length'] = len(ad.picture)
    response.write(ad.picture)
    return response


# class CommentCreateView(LoginRequiredMixin, View):
#     def post(self, request, pk) :
#         f = get_object_or_404(Ad, id=pk)
#         comment = Comment(text=request.POST['comment'], owner=request.user, ad=f)
#         comment.save()
#         return redirect(reverse('ads:ad_detail', args=[pk]))
#
# class CommentDeleteView(OwnerDeleteView):
#     model = Comment
#     template_name = "ads/comment_delete.html"
#
#     # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
#     def get_success_url(self):
#         ad = self.object.ad
#         return reverse('ads:ad_detail', args=[ad.id])

# csrf exemption in class based views
# https://stackoverflow.com/questions/16458166/how-to-disable-djangos-csrf-validation
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError

@method_decorator(csrf_exempt, name='dispatch')
class AddFavoriteView(LoginRequiredMixin, View):

    def post(self, request, pk) :
        print("Add PK",pk)
        t = get_object_or_404(Ad, id=pk)
        fav = Fav(user=request.user, ad=t)
        try:
            fav.save()  # In case of duplicate key
        except IntegrityError as e:
            pass
        return HttpResponse()

@method_decorator(csrf_exempt, name='dispatch')
class DeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Delete PK", pk)
        t = get_object_or_404(Ad, id=pk)
        try:
            fav = Fav.objects.get(user=request.user, ad=t).delete()
        except Fav.DoesNotExist as e:
            pass

        return HttpResponse()


