from django import forms
from .models import Comment

class EmailPostForm(forms.Form):
    you = forms.EmailField()
    name = forms.CharField(max_length=25)
    me = forms.EmailField()

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)