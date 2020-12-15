from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, FormView, TemplateView
from django.views import View
from django.urls import reverse
from django.views.generic.edit import ModelFormMixin
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponse, HttpResponseForbidden
from django.core.mail import send_mail
from .forms import EmailPostForm, CommentForm
from .models import Post, Comment

# *****
class ChildModelFormMixin(ModelFormMixin): 
    ''' extends ModelFormMixin with the ability to include ChildModelForm '''
    child_model = ""
    child_fields = ()
    child_form_class = None

    def get_child_model(self):
        return self.child_model

    def get_child_fields(self):
        return self.child_fields

    def get_child_form(self):
        if not self.child_form_class:
            self.child_form_class = model_forms.modelform_factory(self.get_child_model(), fields=self.get_child_fields())
        return self.child_form_class(**self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        if 'child_form' not in kwargs:
            kwargs['child_form'] = self.get_child_form()
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        child_form = self.get_child_form()

        # check if both forms are valid
        form_valid = form.is_valid()
        child_form_valid = child_form.is_valid()

        if form_valid and child_form_valid:
            return self.form_valid(form, child_form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, child_form):
        self.object = form.save()
        save_child_form = child_form.save(commit=False)
        save_child_form.course_key = self.object
        save_child_form.save()

        return HttpResponseRedirect(self.get_success_url())

# *****

# Debug logging only
import logging
logger = logging.getLogger(__name__)

app_name = 'blog'

# *****
class PostDisplayView(DetailView):
    template_name = 'blog/post/post_detail.html'
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        others = Post.published.all() \
                    .exclude(id=post.id) \
                    .order_by("-created")[:6]
        comments = post.comments.filter(active=True)

        # Check if logged user has commented on this post
        user_commented = False
        if self.request.user.is_authenticated:
            user_commented = comments.filter(author=self.request.user).exists()

        context.update({
            'email_form': EmailPostForm,
            'comment_form': CommentForm,
            'others': others,
            'comments': comments,
            'user_commented': user_commented,
        })
        return context
    
class PostFormView(SingleObjectMixin, TemplateView):
    template_name = 'blog/post/post_detail.html'
    form_class = EmailPostForm
    model = Post

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        post = self.object

        if 'add-comment' in request.POST:
            form = CommentForm(data=request.POST)
            form.instance.author = request.user
            if form.is_valid():
                # Create Comment obj but don't save to db
                comment = form.save(commit=False)
                # Assign current post to the comment
                comment.post = post
                # Save to db
                comment.save()
                logger.debug(f"Comment added to: {post}")
        elif 'send-email' in request.POST:
            form = EmailPostForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                post_url = request.build_absolute_uri(
                                post.get_absolute_url())
                subject = f"{cd['name']} recommends: " \
                        f"{post.title}"
                message = f"{cd['name']} ({cd['me']}) thinks you may like:\n\n" \
                        f"{post.title}\n" \
                        f"{post_url}\n" 
                #send_mail(subject, message, 'microsnout@bell.net', [cd['you']])
                logger.debug(f"Send mail: {subject}")

        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:detail', kwargs=self.kwargs)

class PostDetailView(View):

    def get(self, request, *args, **kwargs):
        view = PostDisplayView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = PostFormView.as_view()
        return view(request, *args, **kwargs)

# *****

def add_email_modal(request, post, context):
    if request.method == 'POST' and \
        'send-email' in request.POST:
        # Form was submitted, need to send email
        logger.debug("add_email_modal: POST")
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                            post.get_absolute_url())
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

def detail(request, year, month, day, post):
    logger.debug("HELLO HELLO HELLO HELLO")
    post = get_object_or_404(Post, slug=post,
                                   status='published',
                                   publish__year=year,
                                   publish__month=month,
                                   publish__day=day)
    
    # Most recent 6 posts not including the detailed one
    others = Post.published.all() \
                 .exclude(id=post.id) \
                 .order_by("-created")[:6]

    # All active comments on this post
    comments = post.comments.filter(active=True)

    # Check if logged user has commented on this post
    if request.user.is_authenticated:
        user_commented = comments.filter(author=request.user).exists()
        user_authenticated = True
    else:
        user_commented = False
        user_authenticated = False

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
        'user_commented': user_commented,
        'user_authenticated': user_authenticated,
    }

    # Include form for email sharing and new Comment form 
    add_email_modal(request, post, context)

    comment = None
    if request.method == 'POST' and \
        'add-comment' in request.POST:
        form = CommentForm(data=request.POST)
        form.instance.author = request.user
        if form.is_valid():
            # Create Comment obj but don't save to db
            comment = form.save(commit=False)
            # Assign current post to the comment
            comment.post = post
            # Save to db
            comment.save()
            return redirect(post)
    else:
        form = CommentForm()

    context.update({
        'new_comment': comment,
        'comment_form': form
    })
        
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
                            post.get_absolute_url())
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