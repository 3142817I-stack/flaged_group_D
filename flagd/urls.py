from django.urls import path
from flagd import views

app_name = 'flagd'

urlpatterns = [
    path('', views.index, name='index'),
    #play
    path('play/', views.play, name='play'),
    path('play/<str:mode>/timer/', views.play_timer, name='play_timer'),
    path('play/<str:mode>/questions/', views.play_questions, name='play_questions'),
    path('play/<str:mode>/results/', views.play_results, name='play_results'),
    path('play/save-result/', views.save_quiz_result, name='save_quiz_result'),
    path('play/<str:mode>/', views.play_game, name='play_game'),
    #leaderboard
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    #about
    path('about/', views.about, name='about'),
    #catalogue
    path('catalogue/', views.catalogue, name='catalogue'),
    path('catalogue/<int:flag_id>/', views.flag_detail, name='flag_detail'),
    #account
    path('account/', views.account, name='account'),
    path('account/sign-up/', views.sign_up, name='sign_up'),
    path('account/guest/', views.continue_as_guest, name='continue_as_guest'), #guest user path
    path('account/settings/', views.user_settings, name='user_settings'),
    path('account/<slug:profile_name_slug>/', views.user_profile, name='user_profile'),
    path('logout/', views.user_logout, name='logout'),

]