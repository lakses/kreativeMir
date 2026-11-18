from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'avatar', 'first_name', 'last_name', 'email',
            'bio', 'phone', 'contact_method', 'github_url', 'website_url',
            'open_to_collaboration', 'available_for_orders',
            'tags',
        ]
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Расскажите о своем творчестве...'}),
            'github_url': forms.URLInput(attrs={'placeholder': 'https://github.com/...'}),
            'website_url': forms.URLInput(attrs={'placeholder': 'https://...'}),
            # ВАЖНО: SelectMultiple вместо CheckboxSelectMultiple
            'tags': forms.SelectMultiple(attrs={
                'class': 'form-control select2-tags',
                'data-placeholder': 'Начните вводить название тега...',
            }),
        }


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')