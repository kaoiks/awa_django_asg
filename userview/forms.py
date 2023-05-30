import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms

from userview.models import Movie, Comment, Rating


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    pass


class RatingForm(forms.ModelForm):
    value = forms.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Rating
        fields = ('value',)


class MovieForm(forms.ModelForm):
    name = forms.CharField(label='Name', max_length=1000)
    genres = forms.CharField(label='Genres', max_length=1000, help_text='Enter genres separated by commas')
    image = forms.CharField(label='Image url', max_length=1000, required=False)

    class Meta:
        model = Movie
        fields = ['name', 'genres', 'image']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['date'] = datetime.datetime.now()
        self.initial['user'] = get_user_model().objects.filter(username=kwargs['initial']['user']).first()
