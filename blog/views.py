from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.http import HttpResponse
from .forms import EmailPostForm
from django.core.mail import send_mail

from .models import Post

app_name = 'blog'

#def detail(request, year, month, day, post):
#    post = get_object_or_404(Post, slug=post,
#                                   status='published',
#                                   publish__year=year,
#                                   publish__month=month,
#                                   publish__day=day)
#    others = Post.published.all() \
#                 .exclude(id=post.id)
#    return render(request,
#                  'blog/post/detail.html',
#                  {'post': post,
#                   'others': others})

def detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                                   status='published',
                                   publish__year=year,
                                   publish__month=month,
                                   publish__day=day)
    others = Post.published.all() \
                 .exclude(id=post.id)
    sent = False
    modal = False
    cd = []
    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                            post.get_abs_blog_url())
            subject = f"{cd['name']} recommends: " \
                      f"{post.title}"
            message = f"{cd['name']} ({cd['me']}) thinks you may like:\n\n" \
                      f"{post.title}\n" \
                      f"{post_url}\n" 
            #send_mail(subject, message, 'microsnout@bell.net', [cd['you']])
            sent = True
            modal = True
    else:
        form = EmailPostForm()
    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                   'others': others,
                   'sent': sent,
                   'form': form,
                   'modal': modal,
                   'modal_data': cd})

class PostIndexView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/index.html'

def share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                            post.get_abs_blog_url())
            subject = f"{cd['name']} recommends: " \
                      f"{post.title}"
            message = f"{cd['name']} ({cd['me']}) thinks you may like:\n\n" \
                      f"{post.title}\n" \
                      f"{post_url}\n" 
            send_mail(subject, message, 'microsnout@bell.net', [cd['you']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html',
                  {'post': post,
                   'form': form,
                   'sent': sent})