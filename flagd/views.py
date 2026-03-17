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

def play_questions(request, mode):
    """Show question count selection screen"""
    from flagd.models import Flag
    from django.db.models import Q
    
    # Define mode display names
    mode_names = {
        'global': 'Global',
        'europe': 'Europe',
        'africa': 'Africa',
        'asiaoceania': 'Asia Oceania',
        'americas': 'Americas'
    }
    
    # Get timer duration from query parameter
    timer_duration = request.GET.get('timer', '30')
    try:
        timer_duration = int(timer_duration)
        if timer_duration < 5:
            timer_duration = 5
        elif timer_duration > 120:
            timer_duration = 120
    except ValueError:
        timer_duration = 30
    
    # Get the count of flags available for this mode
    if mode == 'global':
        total_flags = Flag.objects.count()
    elif mode == 'asiaoceania':
        total_flags = Flag.objects.filter(Q(continent__iexact='asia') | Q(continent__iexact='oceania')).count()
    else:
        total_flags = Flag.objects.filter(continent__iexact=mode).count()
    
    # Generate question count options based on total flags
    question_options = []
    for count in [5, 10, 15, 20]:
        if count <= total_flags:
            question_options.append(count)
    
    # Always add "All" option if there are flags
    if total_flags > 0:
        question_options.append(total_flags)
    
    context_dict = {
        'mode': mode,
        'mode_name': mode_names.get(mode, mode.title()),
        'timer_duration': timer_duration,
        'total_flags': total_flags,
        'question_options': question_options
    }
    return render(request, 'flagd/play_questions.html', context=context_dict)

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
    
    # Get number of questions from query parameter
    num_questions = request.GET.get('num_questions', '1')
    try:
        num_questions = int(num_questions)
        if num_questions < 1:
            num_questions = 1
    except ValueError:
        num_questions = 1
    
    # Get current question number from query parameter
    current_question = request.GET.get('current_question', '1')
    try:
        current_question = int(current_question)
        if current_question < 1:
            current_question = 1
    except ValueError:
        current_question = 1
    
    # Get already shown flags from session to avoid duplicates
    shown_flags = request.session.get('shown_flags', [])
    
    # Get flags based on mode
    if mode == 'global':
        flags = Flag.objects.exclude(flag_id__in=shown_flags)
    elif mode == 'asiaoceania':
        # Include both Asia and Oceania flags
        flags = Flag.objects.filter(Q(continent__iexact='asia') | Q(continent__iexact='oceania')).exclude(flag_id__in=shown_flags)
    else:
        # Filter by continent (case-insensitive)
        flags = Flag.objects.filter(continent__iexact=mode).exclude(flag_id__in=shown_flags)
    
    # Get a random flag for the game
    if flags.exists():
        flag = random.choice(flags)
        # Add this flag to shown flags in session
        shown_flags.append(flag.flag_id)
        request.session['shown_flags'] = shown_flags
        
        # Get all aliases for this flag
        aliases = list(flag.aliases.values_list('alias_name', flat=True))
        context_dict = {
            'flag': flag,
            'aliases': aliases,
            'mode': mode,
            'mode_name': mode_names.get(mode, mode.title()),
            'timer_duration': timer_duration,
            'num_questions': num_questions,
            'current_question': current_question,
            'is_last_question': current_question >= num_questions
        }
    else:
        context_dict = {
            'mode': mode,
            'mode_name': mode_names.get(mode, mode.title()),
            'timer_duration': timer_duration,
            'num_questions': num_questions,
            'current_question': current_question,
            'is_last_question': current_question >= num_questions
        }
    
    return render(request, 'flagd/play_game.html', context=context_dict)


#def about(request):
#    return render(request, 'flagd/about.html')
