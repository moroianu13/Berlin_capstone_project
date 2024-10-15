from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        help_text="Please enter a unique username"
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        help_text="Your password must be at least 8 characters long, and it can't be too similar to your personal information."
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput,
        help_text="Please enter the same password for confirmation."
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')