from django.shortcuts import render
from .forms import UserSignup,UserReactivate
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from .token import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate

def signup(request):
    if request.method == 'POST':
        form = UserSignup(request.POST)
        if form.is_valid():
            new_user = form.save(commit = False)
            new_user.is_active = False
            new_user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your blog account'
            message = render_to_string('registration/signup_confirm_email.html',{
                'user':new_user,
                'domain':current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(new_user.pk)).decode('utf-8'),
                'token':account_activation_token.make_token(new_user),
                })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
                )
            email.send()
            return render(request,'registration/signup_messages.html',{'messages':['We have sent an email to the address. Please confirm to complete the registration.']})
    else:
        form = UserSignup()
    return render(request,'registration/signup.html',{'form':form})

def activate(request,uidb64,token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user,token):
        user.is_active = True
        user.save()
        #login(request,user)      optional login
        return render(request,'registration/signup_messages.html',{'messages':[user.username+',\n','signup is sucessful. Please login to continue.']})
    else:
        return render(request,'registration/signup_messages.html',{'messages':['Activation link is invalid.']})

def reactivate(request):
    if request.method == 'POST':
        form = UserReactivate(request.POST)
        if form.is_valid():
            user = User.objects.get(username=form.cleaned_data.get('username'))
            current_site = get_current_site(request)
            mail_subject = 'Activate your blog account'
            message = render_to_string('registration/signup_confirm_email.html',{
                'user':user,
                'domain':current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)).decode('utf-8'),
                'token':account_activation_token.make_token(user),
                })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
                )
            email.send()
            return render(request,'registration/signup_messages.html',{'messages':['We have sent activation link to your email. Please confirm to complete the registration.']})
    else:
        form = UserReactivate()
    return render(request,'registration/signup_reactivate.html',{'form':form})
