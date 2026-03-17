from django.urls import path
from flagd import views

app_name = 'flagd'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('account/', views.account, name='account'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('play/', views.play, name='play'),
    path('play/<str:mode>/timer/', views.play_timer, name='play_timer'),
    path('play/<str:mode>/questions/', views.play_questions, name='play_questions'),
    path('play/<str:mode>/', views.play_game, name='play_game'),
    #path('category/<slug:category_name_slug>/', views.show_category, name='show_category'),
    #path('add_category/', views.add_category, name='add_category'),
    #path('category/<slug:category_name_slug>/add_page/', views.add_page, name='add_page'),
    #path('register/', views.register, name='register'),
    #path('login/', views.user_login, name='login'),
    #path('logout/', views.user_logout, name='logout'),
]