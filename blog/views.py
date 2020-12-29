from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, FormView, TemplateView
from django.urls import reverse
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.core.mail import send_mail
from .forms import EmailPostForm, VisitorForm
from .models import Post, Comment, Visitor

import sys
import os
import os.path

# For adding AJAX 
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET    
# *****

# Debug logging only
import logging
logger = logging.getLogger(__name__)

app_name = 'blog'

def get_avatar_files():
    names = [name for name in os.listdir(settings.MEDIA_AVATAR_FILES)
                    if name.endswith('.png')]
    return names

def refactor_list( list, n ):
    ''' Create list of rows of n objects each. '''
    new_ = []
    while list:
        new_.append( list[:n] )
        del list[:n]
    return new_

# -----------------------------------------------------
    
def session_query(request, **kwargs):
    name = request.session.get('Visitor', False)
    logger.debug(f"session_query: name=({name})")

    if name:
        try:
            visitor = Visitor.objects.get(name= name)
            logger.debug(f"session_query: {name}:{visitor.pin}")

            # Check for any requested updates
            if 'new_avatar' in kwargs:
                visitor.avatar = kwargs['new_avatar']
                visitor.save()

            return (name, visitor.pin, visitor.avatar.url)
        except:
            logger.debug(f"session_query: Exception:'{sys.exc_info()[0]}'")

    return (None, None, None)

# -----------------------------------------------------

class PostDetailView(DetailView):
    template_name = 'blog/post/detail.html'
    model = Post

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        
        post = self.object
        comments = post.comments.filter(active=True)
        others = Post.published.all() \
                    .exclude(id=post.id) \
                    .order_by("-created")[:8]

        # Check for valid name and pin from session
        visitor_name, visitor_pin, visitor_avatar = session_query(request)

        if visitor_name:
            visitor_form = VisitorForm(
                            initial= { 
                                'name': visitor_name, 
                                'pin': visitor_pin, },
                            prefix='visitor')
        else:
            visitor_form = VisitorForm(prefix='visitor')

        context.update({
            'email_form': EmailPostForm,
            'visitor_form': visitor_form,
            'others': others,
            'comments': comments,
            'avatars': refactor_list( get_avatar_files(), 5 ),
            'visitor_avatar': visitor_avatar,
            'valid_visitor': visitor_name,
        })
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        logger.debug(f"POST request={request}")
        post_data = request.POST or None
        logger.debug(f"PostDetailView:post data= {post_data}")
        self.object = self.get_object()
        post = self.object

        if 'comment-button' in request.POST:
            visitor_form = VisitorForm(post_data, prefix='visitor') 
            self.add_comment(request, visitor_form)
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

        return HttpResponseRedirect(request.path)
    
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

# -----------------------------------------------------
    
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
                # Remember valid user name in session
                request.session['Visitor'] = name
                return JsonResponse({'status': 'Match', 'avatar_url': visitor.avatar.url})
            else:
                return JsonResponse({'status': 'Found'})
        except:
            logger.debug(f"Not found name:'{name}'")
            logger.debug(f"Exception:'{sys.exc_info()[0]}'")
            return JsonResponse({'status': 'Avail'})

    return JsonResponse({'status':'Null'})

# -----------------------------------------------------

@require_POST
def avatar_select(request, *args, **kwargs):
    logger.debug(f"avatar_select: {kwargs}")

    # Check for valid name and pin from session
    visitor_name, visitor_pin, visitor_avatar = session_query(
        request,
        new_avatar= kwargs['file'])

    return HttpResponseRedirect( request.META.get('HTTP_REFERER') )

@require_GET
def delete_comment(request, *args, **kwargs):
    logger.debug(f"delete_comment: {kwargs}")

    try:
        comment = Comment.objects.get(pk= kwargs['pk'])
        logger.debug(f"delete_comment: {comment}")
        comment.delete()
    except:
        logger.debug(f"session_query: Exception:'{sys.exc_info()[0]}'")

    return HttpResponseRedirect( request.META.get('HTTP_REFERER') )

# -----------------------------------------------------

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

# -----------------------------------------------------

class PostIndexView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/index.html'

# -----------------------------------------------------

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