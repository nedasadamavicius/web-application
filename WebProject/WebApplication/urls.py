from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('artist/<str:id>/', views.artist_view, name='artist'),
    path('about', views.about_view, name='about')
]
