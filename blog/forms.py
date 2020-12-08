from django import forms

class EmailPostForm(forms.Form):
    you = forms.EmailField()
    name = forms.CharField(max_length=25)
    me = forms.EmailField()