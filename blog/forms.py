from django import forms
from .models import Comment

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
                        'class': "p-1",
            }))
    name = forms.CharField(
            max_length=30)
    pin = forms.CharField(
            max_length=6)
