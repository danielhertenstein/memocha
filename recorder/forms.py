from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from recorder.models import Patient


class MyUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=256)

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        ]


class PatientCreationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=256)

    class Meta:
        model = Patient
        fields = [
            'first_name',
            'last_name',
            'email',
            'prescriptions',
        ]
