from django.contrib.auth.models import User
from django import forms

from .models import Profile


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class UserEditionForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class ProfileEditionForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('photo', 'website', 'bio', 'phone_number', 'gender')


