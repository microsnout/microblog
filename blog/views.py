from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.http import HttpResponse

from .models import Post

app_name = 'blog'

def detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                                   status='published',
                                   publish__year=year,
                                   publish__month=month,
                                   publish__day=day)
    others = Post.published.all() \
                 .exclude(id=post.id)
    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                   'others': others})

class PostIndexView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/index.html'