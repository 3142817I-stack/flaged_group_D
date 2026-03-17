from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
import random

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
    # Show game mode selection only
    context_dict = {}
    return render(request, 'flagd/play.html', context=context_dict)

def play_timer(request, mode):
    # Show timer selection screen
    mode_names = {
        'global': 'Global',
        'europe': 'Europe',
        'africa': 'Africa',
        'asiaoceania': 'Asia Oceania',
        'americas': 'Americas'
    }
    
    context_dict = {
        'mode': mode,
        'mode_name': mode_names.get(mode, mode.title())
    }
    return render(request, 'flagd/play_timer.html', context=context_dict)

def play_game(request, mode):
    from flagd.models import Flag, CountryAlias
    from django.db.models import Q
    
    # Define mode display names
    mode_names = {
        'global': 'Global',
        'europe': 'Europe',
        'africa': 'Africa',
        'asiaoceania': 'Asia Oceania',
        'americas': 'Americas'
    }
    
    # Get timer duration from query parameter (default to 30 seconds)
    timer_duration = request.GET.get('timer', '30')
    try:
        timer_duration = int(timer_duration)
        # Validate timer duration (between 5 and 120 seconds)
        if timer_duration < 5:
            timer_duration = 5
        elif timer_duration > 120:
            timer_duration = 120
    except ValueError:
        timer_duration = 30
    
    # Get flags based on mode
    if mode == 'global':
        flags = Flag.objects.all()
    elif mode == 'asiaoceania':
        # Include both Asia and Oceania flags
        flags = Flag.objects.filter(Q(continent__iexact='asia') | Q(continent__iexact='oceania'))
    else:
        # Filter by continent (case-insensitive)
        flags = Flag.objects.filter(continent__iexact=mode)
    
    # Get a random flag for the game
    if flags.exists():
        flag = random.choice(flags)
        # Get all aliases for this flag
        aliases = list(flag.aliases.values_list('alias_name', flat=True))
        context_dict = {
            'flag': flag,
            'aliases': aliases,
            'mode': mode,
            'mode_name': mode_names.get(mode, mode.title()),
            'timer_duration': timer_duration
        }
    else:
        context_dict = {
            'mode': mode,
            'mode_name': mode_names.get(mode, mode.title()),
            'timer_duration': timer_duration
        }
    
    return render(request, 'flagd/play_game.html', context=context_dict)


#def about(request):
#    return render(request, 'flagd/about.html')
