from django.shortcuts import render
from .models import Post
# Create your views here.

def index(request):
    posts = Post.objects.all().order_by('-pk')

    return render(
        request,
        'community/index.html',
        {
            'posts' : posts,
        }
    )