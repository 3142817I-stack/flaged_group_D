from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from flagd.models import UserProfile
from flagd.forms import UserForm, UserProfileForm #CategoryForm, PageForm, 
from django.contrib.auth.models import User
import random

def index(request):
    context_dict = {}

    #visitor_cookie_handler(request)

    return render(request, 'flagd/index.html', context=context_dict)

def about(request):
    context_dict = {}
    return render(request, 'flagd/about.html', context=context_dict)

def leaderboard(request):
    from django.contrib.auth.models import User #experiment - is this line needed?
    users = User.objects.all().order_by('-userprofile__score') #removed 1 _
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


#all the account stuff

#user_login equivalent
def account(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('flagd:index'))
            else:
                return HttpResponse("Your Flag-D account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'flagd/account.html')


#register equivalent
def sign_up(request):
    registered = False
    created_user = None

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            
            profile.save()
            registered = True
            created_user=user

        else:
            print(user_form.errors, profile_form.errors)

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    
    return render(request, 'flagd/sign_up.html', context={'user_form': user_form, 'profile_form': profile_form, 'registered': registered, 'user': created_user})


@login_required
def user_profile(request, profile_name_slug):
    try:
        user = User.objects.get(username=profile_name_slug)
        profile = user.userprofile
    except User.DoesNotExist:
        return HttpResponse("User not found.")
    except UserProfile.DoesNotExist:
        return HttpResponse("Profile not found.")

    context_dict = {
        'selected_user': user,
        'profile': profile,
    }
    return render(request, 'flagd/user_profile.html', context=context_dict)

@login_required
def user_settings(request):
    return render(request, 'flagd/user_settings.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('flagd:index'))