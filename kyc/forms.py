from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import UserProfile, KycDocument


class UserSignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'})
    )
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Address'}),
        }


class ProfileCombinedForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=150, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        max_length=150, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )

    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address', 'date_of_birth', 'linkedin_profile', 'github_profile', 'profile_photo', 'nationality', 'language', 'education_level', 'institution', 'graduation_year', 'profession', 'profession_type']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Address'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'linkedin_profile': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'LinkedIn Profile URL'}),
            'github_profile': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'GitHub Profile URL'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nationality'}),
            'language': forms.Select(attrs={'class': 'form-control'}),
            'education_level': forms.Select(attrs={'class': 'form-control'}),
            'institution': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Institution/University'}),
            'graduation_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Graduation Year', 'min': '1900', 'max': '2030'}),
            'profession': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Profession/Job Title'}),
            'profession_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._user = user
        if user is not None:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email

    def save(self, commit=True):
        profile: UserProfile = super().save(commit=False)
        user = getattr(self, '_user', None)
        if user is not None:
            user.first_name = self.cleaned_data.get('first_name', user.first_name)
            user.last_name = self.cleaned_data.get('last_name', user.last_name)
            email_value = self.cleaned_data.get('email')
            if email_value is not None:
                user.email = email_value
            if commit:
                user.save()
                profile.user = user
        if commit:
            profile.save()
        return profile


ALLOWED_CONTENT_TYPES = {
    'application/pdf',
    'image/jpeg',
    'image/png',
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


class KycDocumentForm(forms.ModelForm):
    class Meta:
        model = KycDocument
        fields = [
            'document_file',
            'document_type',
            'document_id',
            'registration_number',
        ]
        widgets = {
            'document_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'document_type': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select Document Type'}),
            'document_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Document ID'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Registration Number'}),
        }

    def clean_document_file(self):
        file = self.cleaned_data.get('document_file')
        if not file:
            return file
        content_type = getattr(file, 'content_type', None)
        if content_type not in ALLOWED_CONTENT_TYPES:
            raise forms.ValidationError('Unsupported file type. Allowed: PDF, JPEG, PNG.')
        if file.size and file.size > MAX_FILE_SIZE:
            raise forms.ValidationError('File too large. Maximum allowed size is 5 MB.')
        return file


