from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('spotify-login/', views.spotify_login, name='spotify_login'),
    path("logout/", views.spotify_logout, name="spotify_logout"),
    path('callback/', views.spotify_callback, name='spotify_callback'),
    path('home/', views.home_view, name='home'),
    path('artist/<str:id>/', views.artist_view, name='artist'),
    path('about/', views.about_view, name='about')
]
