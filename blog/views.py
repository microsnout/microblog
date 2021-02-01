from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, FormView, TemplateView, UpdateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.core.mail import send_mail
from django.db.models import Count
from .forms import EmailPostForm, VisitorForm, PostEditForm
from .models import Blog, Post, Comment, Visitor
from common.decorators import ajax_required


import sys, os, os.path
import inspect
import markdown

# For exceptions only - slow - Finds name of calling function
thisfunc = lambda: inspect.stack()[1][3]

# For adding AJAX 
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET    

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
    ''' Look for last visitor name in session data and lookup in db '''
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

            return (visitor, name, visitor.pin, visitor.avatar.url)
        except:
            logger.debug(f"session_query: Exception:'{sys.exc_info()[0]}'")

    return (None, None, None, None)

# -----------------------------------------------------
from django.db.models import Q

class PostDetailView(DetailView):
    ''' Detailed view of single post along with comments and recent post sidebar '''
    template_name = 'blog/post/detail.html'
    model = Post

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        
        # Check for valid name and pin from session
        visitor, visitor_name, visitor_pin, visitor_avatar = session_query(request)

        post = self.object
        blog = post.blog
        if request.user.is_authenticated:
            # Include all comments for the blog author
            comments = post.comments.filter() \
                        .annotate(count=Count('fans')) \
                        .order_by('-count')
        else:
            # Show all approved comments and my unapproved comments
            comments = post.comments.filter( Q(approved=True) | Q(visitor=visitor) ) \
                        .annotate(count=Count('fans')) \
                        .order_by('-count')
        others = Post.published.all() \
                    .filter(blog=blog) \
                    .exclude(id=post.id) \
                    .order_by("-created")[:8]
        blogs = Blog.objects.all() \
                    .exclude(id=blog.id)

        # Validated user has already commented?
        deja_commente = comments.filter(visitor=visitor).exists()

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
            'avatars': refactor_list( get_avatar_files(), 8 ),
            'visitor_avatar': visitor_avatar,
            'valid_visitor': visitor_name,
            'visitor': visitor,
            'blogs': blogs,
            'blog': blog,
            'has_commented': deja_commente,
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
            
            post = self.object
            try:
                new_comment = Comment(
                                post= post,
                                visitor= visitor,
                                approved= not post.blog.moderated,
                                body= cd['comment'])
                new_comment.save()
            except:
                logger.debug(f"AddComment Exception:'{sys.exc_info()[0]}'")
        else:
            logger.debug("HomeView: visitor form NOT valid")

# -----------------------------------------------------
from django.utils.safestring import mark_safe
import json

@ajax_required
@require_POST
def like_comment(request):
    ''' Ajax handler - called to like and unlike comments in Post Detail View '''
    status = 'liked'
    comment_id = request.POST.get('comment_id')
    logger.debug(f"like_comment: {comment_id}")

    visitor, visitor_name, visitor_pin, visitor_avatar = session_query(request)

    try:
        comment = Comment.objects.get(id=comment_id)

        if visitor == None:
            return JsonResponse({ 'status': 'None' })
        elif visitor in comment.fans.all():
            logger.debug(f"like_comment: remove")
            comment.fans.remove( visitor )
            liked = False
            return JsonResponse({ 'status': 'unliked' })
        else:
            logger.debug(f"like_comment: add")
            comment.fans.add(visitor)
            liked = True
            return JsonResponse({ 'status': 'liked' })
    except:
        logger.debug(f"{thisfunc()}: Exception:'{sys.exc_info()[0]}'")
        return JsonResponse({'status': 'Error'})



@ajax_required
@require_POST
def get_preview(request):
    ''' Ajax handler - gets html from markdown filter - currently not used '''
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    logger.debug(f"get_preview: {body['body']}")
    body_html = mark_safe(markdown.markdown(body['body']))
    logger.debug(f"get_preview markdown: {body_html}")
    return JsonResponse({'body': body_html})
    
@ajax_required
@require_POST
def visitor_query(request):
    ''' AJAX function called by events for visitor name and pin in Post Detail View '''
    name = request.POST.get('name')
    pin = request.POST.get('pin')
    def_avatar = Visitor.DEF_AVATAR_URL

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
                #del request.session['Visitor']
                return JsonResponse({'status': 'Found', 'avatar_url': def_avatar})
        except:
            logger.debug(f"Not found name:'{name}'")
            logger.debug(f"{thisfunc()}: Exception:'{sys.exc_info()[0]}'")
            #del request.session['Visitor']
            return JsonResponse({'status': 'Avail', 'avatar_url': def_avatar})

    #del request.session['Visitor']
    return JsonResponse({'status':'Null', 'avatar_url': def_avatar})

# -----------------------------------------------------

@require_POST
def avatar_select(request, *args, **kwargs):
    ''' Called by avatar buttons in dropdown menu to choose image - Post Detail View '''
    logger.debug(f"avatar_select: {kwargs}")

    # Check for valid name and pin from session
    visitor, visitor_name, visitor_pin, visitor_avatar = session_query(
        request,
        new_avatar= kwargs['file'])

    return HttpResponseRedirect( request.META.get('HTTP_REFERER') )

@require_GET
def delete_comment(request, *args, **kwargs):
    ''' Comment deletion from Post Detail View '''
    logger.debug(f"delete_comment: {kwargs}")

    try:
        comment = Comment.objects.get(pk= kwargs['pk'])
        logger.debug(f"delete_comment: {comment}")
        comment.delete()
    except:
        logger.debug(f"{thisfunc()}: Exception:'{sys.exc_info()[0]}'")

    return HttpResponseRedirect( request.META.get('HTTP_REFERER') )

@require_GET
def approve_comment(request, *args, **kwargs):
    ''' Comment moderation from Post Detail View '''
    logger.debug(f"approve_comment: {kwargs}")

    try:
        comment = Comment.objects.get(pk= kwargs['pk'])
        logger.debug(f"approve_comment: {comment}")
        comment.approved = True
        comment.save()
    except:
        logger.debug(f"{thisfunc()}: Exception:'{sys.exc_info()[0]}'")

    return HttpResponseRedirect( request.META.get('HTTP_REFERER') )

@require_GET
def move_post_to(request, *args, **kwargs):
    ''' Moving post between blogs - Post Detail View '''
    logger.debug(f"move_post_to: {kwargs}")

    try:
        post = Post.objects.get(pk= kwargs['post_id'])
        blog = Blog.objects.get(pk= kwargs['blog_id'])
        post.blog = blog
        post.save()
        blog.update_last_post()
    except:
        logger.debug(f"{thisfunc()}: Exception:'{sys.exc_info()[0]}'")

    return HttpResponseRedirect( request.META.get('HTTP_REFERER') )

@require_GET
def set_status(request, *args, **kwargs):
    ''' Changing post status in Post Detail View '''
    logger.debug(f"set_status: {kwargs}")

    try:
        post = Post.objects.get(pk= kwargs['post_id'])
        post.status = kwargs['new_status']
        post.save()
    except:
        logger.debug(f"{thisfunc()}: Exception:'{sys.exc_info()[0]}'")

    return HttpResponseRedirect( request.META.get('HTTP_REFERER') )


# -----------------------------------------------------

class PostIndexView(ListView):
    ''' Index/List view of all published posts for one blog '''
    context_object_name = 'posts'
    paginate_by = 5
    template_name = 'blog/post/index.html'
    query_status = 'published'

    def get_context_data (self, ** kwargs):
        context = super(ListView, self).get_context_data(** kwargs)
        try:
            context ['query_status'] = self.query_status
            context ['blog'] = Blog.objects.get(slug=self.kwargs['slug'])
            context ['blogs'] = Blog.objects.all().exclude(id= context['blog'].id )
        except:
            logger.debug(f"{thisfunc()}: Exception:'{sys.exc_info()[0]}'")
        return context

    def get_queryset(self):
        ''' Just published posts belonging to specified blog '''
        return Post.objects.filter(status=self.query_status, blog__slug=self.kwargs['slug'])
    

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
                   
# -----------------------------------------------------

class VisitorDetailView(DetailView):
    template_name = 'blog/visitor/detail.html'
    model = Visitor
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        visitor = self.object

        comments = Comment.objects.filter(visitor=visitor).order_by("-created")
        recent = Visitor.objects.all().exclude(id=visitor.id).order_by("-last_visit")[:8]
        blogs = Blog.objects.all()

        context.update({
            'comments': comments,
            'recent': recent,
            'blogs': blogs,
        })
        return self.render_to_response(context)

class VisitorListView(LoginRequiredMixin, ListView):
    ''' Index/List view of all visitors to all blogs '''
    context_object_name = 'visitors'
    paginate_by = 10
    template_name = 'blog/visitor/index.html'
    login_url = 'blog:home'

    def get_context_data (self, ** kwargs):
        context = super(ListView, self).get_context_data(** kwargs)
        try:
            context ['blogs'] = Blog.objects.all()
            context ['addons'] = addon_list
        except:
            logger.debug(f"{thisfunc()}: Exception:'{sys.exc_info()[0]}'")
        return context

    def get_queryset(self):
        ''' Just published posts belonging to specified blog '''
        return Visitor.objects.all()
    
class PostEditView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostEditForm
    template_name = 'blog/post/edit.html'
    success_url = ""
    login_url = 'blog:home'

    def get_context_data (self, ** kwargs):
        logger.debug(f"PostEditView:get_context_data kwargs={kwargs}")
        context = super(UpdateView, self).get_context_data(** kwargs)
        try:
            context ['blog'] = self.object.blog
            context ['blogs'] = Blog.objects.all()
        except:
            logger.debug(f"{thisfunc()}: Exception:'{sys.exc_info()[0]}'")
        return context

    def get(self, request, *args, **kwargs):
        logger.debug(f"PostEditView:get req:{request} **kwargs:{kwargs}")
        return super(UpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logger.debug(f"PostEditView:post req:{request} **kwargs:{kwargs}")
        return super(UpdateView, self).post(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super(UpdateView, self).get_form(form_class)
        logger.debug(f"PostEditView:get_form errors:{form.errors}")
        return form

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')

class HomeLoginView(LoginView):
    template_name = 'blog/home.html'

    def get_context_data (self, ** kwargs):
        logger.debug(f"HomeLoginView:get_context_data kwargs={kwargs}")
        context = super(LoginView, self).get_context_data(** kwargs)
        try:
            context ['blogs'] = Blog.objects.all()
        except:
            logger.debug(f"{thisfunc()}: Exception:'{sys.exc_info()[0]}'")
        return context