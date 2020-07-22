from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .forms import SignUpForm
from .tokens import account_activation_token
from .models import Feedback


@login_required
def index(request):
    return render(request, 'Cards/index.html')


@login_required
def overview(request):
    details = {
        'password_form': PasswordChangeForm(request.user),
        'feedbacks': Feedback.objects.filter(user=request.user).order_by('-created')
    }
    return render(request, 'accounts/overview.html', details)


@login_required
def delete_account(request):
    user = request.user
    user.is_active = False
    user.save()
    return redirect('home')


def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)

            current_site = get_current_site(request)
            mail_subject = 'Confirm your email.'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()

            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/sign_up.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.profile.confirmed = True
        user.profile.save()
        user.save()
        login(request, user)
        return redirect('home')
    else:
        return HttpResponse('Activation link is invalid!')


def send_confirmation(request, response=True):
    user = request.user
    current_site = get_current_site(request)
    mail_subject = 'Confirm your email.'
    message = render_to_string('acc_active_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    to_email = user.email
    email = EmailMessage(
        mail_subject, message, to=[to_email]
    )
    email.send()
    if response:
        return HttpResponse(status=204)


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        details = {
            'password_form': form,
            'email_fail': True,
        }
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('account_overview')
        else:
            messages.error(request, 'Please correct the error below.')
        return render(request, 'accounts/overview.html', details)


def change_email(request):
    if request.method == 'POST':
        new_email = request.POST['new_email']
        user = request.user
        user.email = new_email
        user.profile.confirmed = False
        user.save()
        user.profile.save()
        send_confirmation(request, response=False)
        details = {
            'password_form': PasswordChangeForm(request.user),
        }

        return render(request, 'accounts/overview.html', details)
    # return HttpResponse(status=204)


def change_name(request):
    if request.method == 'POST':
        new_first = request.POST['new_first']
        new_last = request.POST['new_last']
        user = request.user
        user.first_name = new_first
        user.new_last = new_last
        user.save()
        details = {
            'password_form': PasswordChangeForm(request.user),
        }

        return render(request, 'accounts/overview.html', details)


def opinion(request):
    if request.method == 'POST':
        user = request.user
        current_site = request.POST['path'][1:-1]
        if current_site == ":":
            current_site = 'home'
        user_opinion = request.POST['opinion']
        Feedback.objects.create(user=user, creator=user.username, page=current_site, text=user_opinion)
        return redirect(request.META['HTTP_REFERER'])


def change_language(request):
    from django.conf import settings
    response = HttpResponseRedirect('/')
    if request.method == 'POST':
        language = request.POST.get('language')
        current_site = request.POST.get('url')
        languages = ("pl",) # add codes for new translations here
        # as long as there won't be language codes longer than 
        # two letters, it will work 
        if current_site[1:3] in languages:
            current_site = current_site[3:]
        if language:
            if language != settings.LANGUAGE_CODE and [lang for lang in settings.LANGUAGES if lang[0] == language]:
                redirect_path = f'/{language}' + current_site
            elif language == settings.LANGUAGE_CODE:
                redirect_path = current_site
            else:
                return response
            from django.utils import translation
            translation.activate(language)
            response = HttpResponseRedirect(redirect_path)
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
    return response
