from django import forms
from .models import Post, Comment


class PostCreationForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['post', 'caption', 'tags']


class PostEditionForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['post', 'caption', 'tags']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body', ]
