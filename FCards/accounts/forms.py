from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',)

    def clean(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError((_(mark_safe("""An account already exists for this email address. <a href="/accounts/login/" class="email_error">Log in instead?</a> You can also <a href="/accounts/password_reset/" class="email_error">reset your password.</a>"""))))
        return self.cleaned_data
