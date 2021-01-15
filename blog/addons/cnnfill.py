from django.conf import settings
from django import forms
from django.views.generic import FormView, TemplateView
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from blog.models import Blog, Post

import sys, os, os.path
import inspect

# For exceptions only - slow - Finds name of calling function
thisfunc = lambda: inspect.stack()[1][3]

# Debug logging only
import logging
logger = logging.getLogger(__name__)

app_name = 'blog'

def get_blog_list():
    list = []
    for blog in Blog.objects.all():
        list += (blog.id, blog.title)
    
    return list


class CnnFillForm(forms.Form):
    blog = forms.ChoiceField(choices=get_blog_list)
    count = forms.IntegerField(min_value=1)
    size = forms.IntegerField(min_value=1)


class CnnFillView(FormView):
    template_name = 'cnnfill.html'
    form_class = CnnFillForm 
    success_url = '' 

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        return super().form_valid(form)


def addon_init():
    logger.debug("addon_init: CNN")


logger.debug("CNN Fill Hello")

from blog.views import register_addon

register_addon('CNN db Fill', '/cnnfill/')