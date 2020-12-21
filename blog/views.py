from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, FormView, TemplateView
from django.urls import reverse
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.core.mail import send_mail
from .forms import EmailPostForm, VisitorForm
from .models import Post, Comment, Visitor

import sys

# For adding AJAX 
from django.http import JsonResponse
from django.views.decorators.http import require_POST    
# *****

# Debug logging only
import logging
logger = logging.getLogger(__name__)

app_name = 'blog'

# *****
    
class PostFormView(SingleObjectMixin, TemplateView):
    template_name = 'blog/post/detail.html'
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

class PostDetailView(DetailView):
    template_name = 'blog/post/detail.html'
    model = Post

    def post(self, request, *args, **kwargs):
        post_data = request.POST or None
        logger.debug(f"PostDetailView:post data= {post_data}")
        self.object = self.get_object()
        post = self.object
        others = Post.published.all() \
                    .exclude(id=post.id) \
                    .order_by("-created")[:6]
        comments = post.comments.filter(active=True)
        context = self.get_context_data(object=self.object)

        if 'comment-button' in request.POST:
            visitor_form = VisitorForm(post_data, prefix='visitor') 
            self.add_comment(request, visitor_form)
            return HttpResponseRedirect(request.path)

        # Check for valid name and pin from session
        visitor_name = request.session.get('Visitor', False)
        logger.debug(f"PostDetailView:post found session name: '{visitor_name}'")
        if visitor_name:
            try:
                visitor = Visitor.objects.get(name= visitor_name)
                visitor_pin = visitor.pin
                logger.debug(f"PostDetailView:post found pin: '{visitor_pin}'")
            except:
                logger.debug(f"PostDetailView:post Exception:'{sys.exc_info()[0]}'")
            finally:
                if visitor_pin:
                    visitor_form = VisitorForm(
                                    initial= { 
                                        'name': visitor_name, 
                                        'pin': visitor_pin, },
                                    prefix='visitor')
                else:
                    visitor_form = VisitorForm(prefix='visitor')
        else:
            visitor_form = VisitorForm(prefix='visitor')
                
        context.update({
            'email_form': EmailPostForm,
            'visitor_form': visitor_form,
            'others': others,
            'comments': comments,
        })
        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        logger.debug(f"GET request={request}")
        return self.post(request, *args, **kwargs)
    
    def add_comment(self, request, form):
        if form.is_valid():
            cd = form.cleaned_data
            logger.debug(f"HomeView: visitor form valid: cd={cd}")
            visitor, new = Visitor.objects.get_or_create(
                            name= cd['name'],
                            pin= cd['pin'])
            if new:
                logger.debug(f"Created visitor: '{visitor}'")
            else:
                logger.debug(f"Using visitor: '{visitor}'")

            # Remember valid user name
            request.session['Visitor'] = cd['name']
            
            try:
                new_comment = Comment(
                                post= self.object,
                                visitor= visitor,
                                body= cd['comment'])
                new_comment.save()
            except:
                logger.debug(f"AddComment Exception:'{sys.exc_info()[0]}'")
        else:
            logger.debug("HomeView: visitor form NOT valid")

    
@require_POST
def visitor_query(request):
    name = request.POST.get('name')
    pin = request.POST.get('pin')

    # Debug output
    logger.debug(f"name='{name}'")
    logger.debug(f"pin='{pin}'")

    if name and len(name) > 1:
        try:
            visitor = Visitor.objects.get(name=name)
            logger.debug(f"Found name:'{name}'")
            pin_match = (pin == visitor.pin)
            logger.debug(f"Pin match: [{pin_match}]")
            if pin_match:
                return JsonResponse({'status': 'Match'})
            else:
                return JsonResponse({'status': 'Found'})
        except:
            logger.debug(f"Not found name:'{name}'")
            logger.debug(f"Exception:'{sys.exc_info()[0]}'")
            return JsonResponse({'status': 'Avail'})

    return JsonResponse({'status':'Null'})

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