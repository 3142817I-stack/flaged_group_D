from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q
from django.conf import settings
from django.views.decorators.http import require_http_methods
import json

from flagd.models import UserProfile, Flag, CountryAlias
from flagd.forms import * #UserForm, UserProfileForm, UserUpdateForm, UserProfileUpdateForm

import random


def index(request):
    context_dict = {}
    from django.contrib.auth.models import User
    top_users = User.objects.order_by('-userprofile__score')[:3] 
    context_dict = {'top_users': top_users}
    return render(request, 'flagd/index.html', context=context_dict)


def about(request):
    context_dict = {}
    return render(request, 'flagd/about.html', context=context_dict)


def leaderboard(request):
    from django.contrib.auth.models import User
    users = User.objects.all().order_by('-userprofile__score')
    context_dict = {'users': users}
    return render(request, 'flagd/leaderboard.html', context=context_dict)


def play(request):
    # Logged-in users can always access play
    if request.user.is_authenticated:
        return render(request, 'flagd/play.html', {})

    # Guests can access play only after explicitly choosing guest mode
    if request.session.get('guest_mode'):
        return render(request, 'flagd/play.html', {})

    # First-time unauthenticated visitors get redirected to account page
    return redirect('flagd:account')

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
    # Clear session if starting a new game (current_question is 1)
    if current_question == 1:
        request.session['shown_flags'] = []
        shown_flags = []
        # Also clear quiz results when starting a new game
        if 'quiz_results' in request.session:
            del request.session['quiz_results']
            request.session.modified = True
    else:
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
    
    # Check if this is an AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Build JSON response for AJAX
        if 'flag' in context_dict:
            flag = context_dict['flag']
            flag_data = {
                'flag_id': flag.flag_id,
                'country_name': flag.country_name,
                'country_code': flag.country_code,
                'continent': flag.continent,
            }
            aliases_data = context_dict['aliases']
        else:
            flag_data = None
            aliases_data = []
        
        data = {
            'flag': flag_data,
            'aliases': aliases_data,
            'mode': context_dict['mode'],
            'mode_name': context_dict['mode_name'],
            'timer_duration': context_dict['timer_duration'],
            'num_questions': context_dict['num_questions'],
            'current_question': context_dict['current_question'],
            'is_last_question': context_dict['is_last_question']
        }
        return JsonResponse(data)
    else:
        # For non-AJAX requests, add initial data for the template to use
        if 'flag' in context_dict:
            flag = context_dict['flag']
            flag_data = {
                'flag_id': flag.flag_id,
                'country_name': flag.country_name,
                'country_code': flag.country_code,
                'continent': flag.continent,
            }
            aliases_data = list(flag.aliases.values_list('alias_name', flat=True))
        else:
            flag_data = None
            aliases_data = []
        
        context_dict['initial_data_json'] = json.dumps({
            'flag': flag_data,
            'aliases': aliases_data,
            'mode': mode,
            'mode_name': mode_names.get(mode, mode.title()),
            'timer_duration': timer_duration,
            'num_questions': num_questions,
            'current_question': current_question,
            'is_last_question': current_question >= num_questions
        })
        
        return render(request, 'flagd/play_game.html', context=context_dict)


@require_http_methods(["POST"])
def save_quiz_result(request):
    """Save a quiz result to the session via AJAX"""
    try:
        data = json.loads(request.body)
        
        # Initialize quiz_results in session if not exists
        if 'quiz_results' not in request.session:
            request.session['quiz_results'] = []
        
        # Add the result to the session
        result = {
            'flag_id': data.get('flag_id'),
            'country_name': data.get('country_name'),
            'country_code': data.get('country_code'),
            'is_correct': data.get('is_correct', False),
            'question_number': data.get('current_question'),
            'score': data.get('score', 0),
            'time_taken': data.get('time_taken', 0),
        }
        
        request.session['quiz_results'].append(result)
        request.session.modified = True
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def play_results(request, mode):
    """Display quiz results after completing all questions"""
    from django.db.models import Q
    
    # Define mode display names
    mode_names = {
        'global': 'Global',
        'europe': 'Europe',
        'africa': 'Africa',
        'asiaoceania': 'Asia Oceania',
        'americas': 'Americas'
    }
    
    # Get timer and question count from query params
    timer_duration = request.GET.get('timer', '30')
    num_questions = request.GET.get('num_questions', '1')
    total_score = request.GET.get('total_score', 0)
    
    # Get quiz results from session
    quiz_results = request.session.get('quiz_results', [])
    
    # Calculate statistics
    total_questions = len(quiz_results)
    correct_answers = sum(1 for r in quiz_results if r.get('is_correct'))
    incorrect_answers = total_questions - correct_answers
    
    # Calculate percentage based on correct answers
    if total_questions > 0:
        percentage = round((correct_answers / total_questions) * 100, 1)
    else:
        percentage = 0
    
    # Get list of wrong answers with flag details
    wrong_answers = []
    for result in quiz_results:
        if not result.get('is_correct'):
            wrong_answers.append({
                'country_name': result.get('country_name'),
                'country_code': result.get('country_code'),
                'flag_id': result.get('flag_id'),
            })
    
    # Calculate total score from session results (time-based scoring)
    calculated_total_score = 0
    for result in quiz_results:
        calculated_total_score += result.get('score', 0)
    
    # Use the higher of the two scores (from URL or calculated)
    final_total_score = max(int(total_score), calculated_total_score)
    
    # Calculate max possible score (1000 points per question, 10000 for 10 questions)
    max_possible_score = total_questions * 1000
    
    # Calculate score percentage (out of 1000 for 10 questions)
    if max_possible_score > 0:
        score_percentage = round((final_total_score / max_possible_score) * 100, 1)
    else:
        score_percentage = 0
    
    # Update user high score ONLY for 20 seconds and 10 questions
    if request.user.is_authenticated and total_questions > 0:
        try:
            profile = request.user.userprofile
            # Check if this is a high score game (20 seconds, 10 questions)
            is_high_score_game = (int(timer_duration) == 20 and int(num_questions) == 10)
            
            if is_high_score_game:
                # Add time-based score to user profile (max 10000 for 10 questions)
                profile.score += final_total_score
                profile.save()
        except UserProfile.DoesNotExist:
            pass
    
    context_dict = {
        'mode': mode,
        'mode_name': mode_names.get(mode, mode.title()),
        'timer_duration': timer_duration,
        'num_questions': num_questions,
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'incorrect_answers': incorrect_answers,
        'percentage': percentage,
        'wrong_answers': wrong_answers,
        'total_score': final_total_score,
        'max_possible_score': max_possible_score,
        'score_percentage': score_percentage,
    }
    
    return render(request, 'flagd/play_results.html', context=context_dict)


#all the catalogue views
def catalogue(request):
    query = request.GET.get('q', '').strip()
    
    flags = Flag.objects.all().order_by('country_name')
    
    if query:
        flags = Flag.objects.filter(
            Q(country_name__icontains=query) |
            Q(aliases__alias_name__icontains=query)
        ).distinct().order_by('country_name')
        
        # If there is exactly one result and it exactly matches a country or alias,
        # send the user straight to the detail page.
        exact_match = Flag.objects.filter(
            Q(country_name__iexact=query) |
            Q(aliases__alias_name__iexact=query)
        ).distinct()
        
        if exact_match.count() == 1:
            return redirect('flagd:flag_detail', flag_id=exact_match.first().flag_id)
    
    context_dict = {
        'flags': flags,
        'query': query,
    }
    return render(request, 'flagd/catalogue.html', context=context_dict)


def flag_detail(request, flag_id):
    flag = get_object_or_404(Flag, flag_id=flag_id)
    aliases = flag.aliases.all().order_by('alias_name')
    
    # Get the 'next' parameter to determine where to go back to
    next_url = request.GET.get('next', None)
    
    context_dict = {
        'flag': flag,
        'aliases': aliases,
        'next_url': next_url,
    }
    return render(request, 'flagd/flag_detail.html', context=context_dict)


#all the account views
def account(request):
    #if user signed in already, redirect
    if request.user.is_authenticated:
        return redirect('flagd:user_profile', profile_name_slug=request.user.username)
    
    error_message = None
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user:
            if user.is_active:
                login(request, user)
                request.session.pop('guest_mode', None)
                return redirect('flagd:user_profile', profile_name_slug=user.username)
            else:
                error_message = "Your account is disabled."
        else:
            error_message = "Invalid username or password."
    
    return render(request, 'flagd/account.html', {'error_message': error_message})


def sign_up(request):
    #also if user already signed up, redirect to profile
    if request.user.is_authenticated:
        return redirect('flagd:user_profile', profile_name_slug=request.user.username)
    
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            
            profile = profile_form.save(commit=False)
            profile.user = user
            
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            else:
                profile.picture = random.choice(settings.DEFAULT_PFPS)
            
            profile.save()
            login(request, user)  # login after signup completed
            request.session.pop('guest_mode', None)
            
            # go straight to profile page
            return redirect('flagd:user_profile', profile_name_slug=user.username)
        
        else:
            print(user_form.errors, profile_form.errors)
    
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    
    return render(request, 'flagd/sign_up.html',{'user_form': user_form,'profile_form': profile_form,})


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
    user_form = UserUpdateForm(instance=request.user)
    profile_form = UserProfileUpdateForm(instance=request.user.userprofile)
    password_form = PasswordChangeForm(user=request.user)
    delete_form = DeleteAccountForm(user=request.user)
    
    success_message = None
    
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            user_form = UserUpdateForm(request.POST, instance=request.user)
            profile_form = UserProfileUpdateForm(
                request.POST,
                request.FILES,
                instance=request.user.userprofile
            )
            password_form = PasswordChangeForm(user=request.user)
            delete_form = DeleteAccountForm(user=request.user)
            
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                success_message = "Profile updated successfully."
        
        elif 'change_password' in request.POST:
            user_form = UserUpdateForm(instance=request.user)
            profile_form = UserProfileUpdateForm(instance=request.user.userprofile)
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            delete_form = DeleteAccountForm(user=request.user)
            
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                success_message = "Password changed successfully."
        
        elif 'delete_account' in request.POST:
            user_form = UserUpdateForm(instance=request.user)
            profile_form = UserProfileUpdateForm(instance=request.user.userprofile)
            password_form = PasswordChangeForm(user=request.user)
            delete_form = DeleteAccountForm(user=request.user, data=request.POST)
            
            if delete_form.is_valid():
                user = request.user
                logout(request)
                user.delete()
                return redirect('flagd:index')
    
    return render(
        request,'flagd/user_settings.html', 
        {'user_form': user_form, 'profile_form': profile_form, 'password_form': password_form, 'delete_form': delete_form, 'success_message': success_message,}
    )

def continue_as_guest(request):
    request.session['guest_mode'] = True
    return redirect('flagd:play')


@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('flagd:index'))