from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from django.contrib.auth import authenticate
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


#removed option to clear pfp
class UserProfileUpdateForm(forms.ModelForm):
    picture = forms.ImageField(
        required=False,
        widget=forms.FileInput()
    )

    class Meta:
        model = UserProfile
        fields = ('picture',)


class DeleteAccountForm(forms.Form):
    password = forms.CharField(
        label="Confirm your password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'})
    )
    confirm_text = forms.CharField(
        label='Type DELETE to confirm',
        widget=forms.TextInput(attrs={'placeholder': 'Type DELETE'})
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        user = authenticate(username=self.user.username, password=password)
        if user is None:
            raise forms.ValidationError("Incorrect password.")
        return password

    def clean_confirm_text(self):
        confirm_text = self.cleaned_data.get('confirm_text')
        if confirm_text != 'DELETE':
            raise forms.ValidationError('You must type DELETE exactly.')
        return confirm_text