from django.shortcuts import render
from .models import Artist

# Create your views here.

# Collection of artists in the database
def home_view(request):
    artists = Artist.objects.all()
    return render(request, 'WebApplication/home.html', {'artists': artists})

# User profile page
def profile_view(request):
    return render(request, 'WebApplication/profile.html')

# Individual artist page
def artist_view(request):
    return render(request, 'WebApplication/artist.html')
