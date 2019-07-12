from django import forms

# give us base use class
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from .models import Keyword

# User Registration Form
class RegisterForm(forms.ModelForm):

  # username field
  username = forms.CharField(max_length=30, required=True, help_text='Use your Lafayette username.')

  # password field but  hide the password the user inputting
  password = forms.CharField(max_length=30, required=True, help_text='Choose wisely.', widget=forms.PasswordInput)

  # email field
  email = forms.EmailField(max_length=254, required=True, help_text='Use your Lafayette email.')

  # information about our class
  class Meta:
    model = User
    fields = ['username', 'email', 'password']

# Keyword Input Form
class KeywordForm(forms.Form):

    # keyword field
    k_text = forms.CharField(label='Keyword:', max_length=50, required=True, validators=[RegexValidator('^[a-zA-Z]+$')])

    # Method that pulls the input keyword and returns a cleaned copy
    def clean_k_text(self):
      data = self.cleaned_data['k_text']
      return data.lower()

