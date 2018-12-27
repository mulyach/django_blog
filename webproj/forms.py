from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

class UserSignup(UserCreationForm):
    username = forms.CharField(label='Username', min_length=4, max_length=150, help_text = 'Username at least 4 characters of either letters, digits or @/./+/-/_')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, help_text = "Password at least 8 characters")
    password2 = forms.CharField(label='Password Confirmation', widget=forms.PasswordInput)
    email = forms.EmailField(label='Enter email',required=True)

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        r = User.objects.filter(username=username)
        if r.count():
            raise ValidationError(_('Username already exists. Please Request Activation Link instead.'))
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        r = User.objects.filter(email=email,is_active=True)
        if r.count():
            raise ValidationError(_('Email already exists'))
        return email

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name','last_name','email',)

class UserReactivate(forms.Form):
    username = forms.CharField(label='Username', min_length=4, max_length=150, help_text = 'Registered username only')
    email = forms.EmailField(label='Enter email',required=True)

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        r = User.objects.filter(username=username)
        if not r.count():
            raise ValidationError(_('Username is not registered. Please Signup.'))
        return username        

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        r = User.objects.filter(email=email,is_active=True)
        if r.count():
            raise ValidationError(_('Email already exists'))
        return email