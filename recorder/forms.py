from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from recorder.models import Prescription


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


class PatientCreationForm(forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=256)
    date_of_birth = forms.DateField(widget=forms.SelectDateWidget)
    secure_code = forms.CharField(max_length=50)


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = '__all__'


class PatientAccountForm(UserCreationForm):
    # TODO: Make the first name the primary field.
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=256)
    secure_code = forms.CharField(max_length=50)
    date_of_birth = forms.DateField(widget=forms.SelectDateWidget)

    field_order = [
        'first_name',
        'last_name',
        'email',
        'date_of_birth',
        'secure_code',
        'username',
        'password1',
        'password2',
    ]

    def clean(self):
        cleaned_data = super(PatientAccountForm, self).clean()
        secure_code = cleaned_data.get('secure_code')
        new_password = cleaned_data.get('password1')
        if new_password == secure_code:
            raise forms.ValidationError(
                _('Your new password cannot be the same as the secure code.'),
                code='new_password_invalid',
            )

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


class UploadFileForm(forms.Form):
    medication = forms.CharField(max_length=100)