from django import forms
from .models import Comment, Post

# Debug logging only
import logging
logger = logging.getLogger(__name__)

app_name = 'blog'

class EmailPostForm(forms.Form):
    you = forms.EmailField()
    name = forms.CharField(max_length=25)
    me = forms.EmailField()

class VisitorForm(forms.Form):
    comment = forms.CharField(
            max_length=300,
            widget= forms.Textarea(attrs={
                        'placeholder': "Your comment...",
                        'class': "p-1", }))
    name = forms.CharField(
            max_length=30)
    pin = forms.CharField(
            max_length=6,
            widget=forms.TextInput(attrs={
                        'type': 'text', }))

class PostEditForm(forms.ModelForm):
    status = forms.ChoiceField(choices=Post.STATUS)
    title = forms.CharField(max_length=250,
                    widget=forms.TextInput(attrs={
                        'size':100,
                    }))
    body = forms.CharField(
            widget=forms.Textarea(attrs={
                        'size': 100, 'height': "300px",
                        }))

    class Meta:
        model = Post
        fields = ['status', 'title', 'body', ]
    
    
    
logger.debug("FORMS Hello")
