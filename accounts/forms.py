from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import CustomUser

class CustomeUserCreationForm(UserCreationForm):

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput
    )

    password2 = forms.CharField(
            label="Confirm Password",
            widget=forms.PasswordInput
        )
    class Meta:
        model = CustomUser
        fields = ['username','email']