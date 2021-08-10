from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.decorators.csrf import csrf_exempt
from. import views

urlpatterns = [
    # path('login/', views.user_login, name='login')
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.homepage, name='homepage'),
    path('accounts/register/', views.register, name='register'),
    path('accounts/profile/<str:username>/', views.profile, name='profile'),
    path('user/follow/', views.user_follow, name='user_follow'),
    path('accounts/edit/', views.edit_profile, name='edit_profile'),
    path('explore/people/suggested/', views.suggested, name='suggested'),
    path('save/', views.post_save, name='post_save'),
    path('<str:username>/saved/', views.profile_saved, name='saved'),
    path('search-users/', csrf_exempt(views.search_users), name='search_users'),


]
