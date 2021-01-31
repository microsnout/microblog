from django.conf import settings
from django.forms.models import BaseModelFormSet
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from extra_views import ModelFormSetView
from django.contrib.auth.mixins import LoginRequiredMixin

# Local stuff
from common.decorators import ajax_required
from .models import Blog

# Python system stuff
import sys, os
import inspect

# For exceptions only - slow - Finds name of calling function
thisfunc = lambda: inspect.stack()[1][3]

# Debug logging only
import logging
logger = logging.getLogger(__name__)

app_name = 'blog'


class BaseBlogFormSet(BaseModelFormSet):

    def clean(self):
        """ Checks that no two articles have the same title """
        logger.debug(f"BaseBlogFormSet:clean can_delete={self.can_delete}")
        logger.debug(f"BaseBlogFormSet:clean class={type(self)}")
        if any(self.errors):
            logger.debug(f"BaseBlogFormSet:clean errors={self.errors}")
            # Don't bother validating the formset unless each form is valid on its own
            return

        titles = []
        for form in self.forms:
            logger.debug(f"BaseBlogFormSet:clean data={self.cleaned_data}")
            if self.can_delete and self._should_delete_form(form):
                continue
            title = form.cleaned_data.get('title')
            if title in titles:
                raise ValidationError("Articles in a set must have distinct titles.")
            titles.append(title)


# Custom formset with validation 
BlogFormSet = modelformset_factory(Blog, fields=('title', 'description'), formset=BaseBlogFormSet, can_delete=True)

class BlogListView(LoginRequiredMixin, ModelFormSetView):
    template_name = 'blog/blog/formset.html'
    model = Blog
    formset_class = BlogFormSet
    logger.debug(f"BlogListView formset_class={formset_class.can_delete}")
    #fields = ('title', 'slug', 'description', 'status', 'one_comment')
    exclude = []
    login_url = 'blog:home'

    def get_context_data (self, ** kwargs):
        logger.debug(f"BlogListView:get_context_data kwargs={kwargs}")
        context = super(ModelFormSetView, self).get_context_data(** kwargs)
        try:
            context ['blogs'] = Blog.objects.all()
        except:
            logger.debug(f"{thisfunc()}: Exception:'{sys.exc_info()[0]}'")
        return context
