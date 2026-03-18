from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.core.validators import RegexValidator
from flagd.models import UserProfile

class UserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    #restrict username to letters, numbers, underscores, dashes
    username = forms.CharField(
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z0-9_-]+$',
                message="Username can only contain letters, numbers, underscores, and hyphens."
            )
        ]
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('picture',)



#check if better way
class UserUpdateForm(forms.ModelForm):
    username = forms.CharField(
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z0-9_-]+$',
                message="Username can only contain letters, numbers, underscores, and hyphens."
            )
        ]
    )

    class Meta:
        model = User
        fields = ('username', 'email')


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('picture',)