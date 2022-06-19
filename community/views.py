from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from .models import Post, Category, Comment
from .forms import CommentForm
from django.db.models import Q
# Create your views here.

class PostList(ListView):
    model = Post
    ordering = '-pk'
    paginate_by = 8

    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()

        return context

class PostDetail(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        context['comment_form'] = CommentForm

        return context

class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['category', 'title', 'content', 'head_image', 'file_upload']

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated:
            form.instance.author = current_user
            return super(PostCreate, self).form_valid(form)
        else:
            return redirect('/community/')

class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['category', 'title', 'content', 'head_image', 'file_upload']

    template_name = 'community/post_update_form.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied


def category_page(request, slug):
    if slug == 'no_category':
        page = request.GET.get('page', '1')
        category = '미분류'
        post_list = Post.objects.filter(category=None).order_by('-pk')
        paginator = Paginator(post_list, '8')
        page_obj = paginator.get_page(page)
    else:
        page = request.GET.get('page', '1')
        category = Category.objects.get(slug=slug)
        post_list = Post.objects.filter(category=category).order_by('-pk')
        paginator = Paginator(post_list, '8')
        page_obj = paginator.get_page(page)


    return render(
        request,
        'community/post_list.html',
        {
            'post_list': post_list,
            'page_obj': page_obj,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=category).count(),
            'category': category,
        }
    )

def new_comment(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, pk=pk)

        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect(comment.get_absolute_url())
        else:
            return redirect(post.get_absolute_url())
    else:
        raise


class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(CommentUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post = comment.post
    if request.user.is_authenticated and request.user == comment.author:
        comment.delete()
        return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied

class PostSearch(PostList):
    def get_queryset(self):
        q = self.kwargs['q']
        post_list = Post.objects.filter(Q(title__contains=q)).order_by('-pk')

        return post_list

