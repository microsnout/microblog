from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.http import HttpResponse
from django.core.mail import send_mail
from .forms import EmailPostForm, CommentForm
from .models import Post, Comment

# Debug logging only
import logging
logger = logging.getLogger(__name__)

app_name = 'blog'

def add_email_modal(request, post, context):
    if request.method == 'POST' and \
        'send-email' in request.POST:
        # Form was submitted, need to send email
        logger.debug("add_email_modal: POST")
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
            context.update({
                'sent': True,
                'modal': True,
                'modal_data': cd,
            })
    else:
        # GET request
        form = EmailPostForm()
        context.update({
            'form': form
        })

def add_new_comment(request, post, context):
    comment = None
    if request.method == 'POST' and \
        'add-comment' in request.POST:
        logger.debug("add_new_comment: POST")
        form = CommentForm(data=request.POST)
        if form.is_valid():
            # Create Comment obj but don't save to db
            comment = form.save(commit=False)
            # Assign current post to the comment
            comment.post = post
            # Save to db
            comment.save()
    else:
        form = CommentForm()

    context.update({
        'new_comment': comment,
        'comment_form': form
    })

def detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                                   status='published',
                                   publish__year=year,
                                   publish__month=month,
                                   publish__day=day)
    
    # Most recent 6 posts not including the detailed one
    others = Post.published.all() \
                 .exclude(id=post.id) \
                 .order_by("-created")[:6]

    comments = post.comments.filter(active=True)

    nm = "-"
    if 'add-comment' in request.POST:
        nm = "AC"
    if 'send-email' in request.POST:
        nm = "SE"
    logger.debug( f">>>detail: {request.method} name:{nm}" )

    # The detailed post and the others
    context = {
        'post': post,
        'others': others,
        'comments': comments,
    }

    # Include form for email sharing and new Comment form 
    add_email_modal(request, post, context)
    add_new_comment(request, post, context)
        
    return render(request, 'blog/post/detail.html', context)

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