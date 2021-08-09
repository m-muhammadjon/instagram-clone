from django.urls import path

from . import views
app_name = 'post'

urlpatterns = [
    path('create/', views.post_create, name='post_create'),
    path('<int:id>/', views.post_detail, name='post_detail'),
    path('like/', views.post_like, name='post_like'),
    path('comment_create/', views.create_comment, name='comment'),
    path('explore/', views.explore, name='explore'),

]