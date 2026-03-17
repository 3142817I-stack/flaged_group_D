from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect

def index(request):
    context_dict = {}

    #visitor_cookie_handler(request)

    return render(request, 'flagd/index.html', context=context_dict)

def about(request):
    context_dict = {}
    return render(request, 'flagd/about.html', context=context_dict)

def account(request):
    context_dict = {}
    return render(request, 'flagd/account.html', context=context_dict)

def leaderboard(request):
    from flagd.models import User
    users = User.objects.all().order_by('-score')
    context_dict = {'users': users}
    return render(request, 'flagd/leaderboard.html', context=context_dict)

def play(request):
    context_dict = {}
    return render(request, 'flagd/play.html', context=context_dict)


#def about(request):
#    return render(request, 'flagd/about.html')
