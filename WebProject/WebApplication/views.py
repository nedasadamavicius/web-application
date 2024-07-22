from django.shortcuts import render, get_object_or_404
from .models import Artist
import base64

# Create your views here.

# Collection of artists in the database
def home_view(request):
    artists = Artist.objects.all()
    for artist in artists:
        if artist.album_image:
            artist.image_data = base64.b64encode(artist.album_image).decode('utf-8')
        else:
            artist.image_data = None
    return render(request, 'WebApplication/home.html', {'artists': artists})

# User profile page
def profile_view(request):
    return render(request, 'WebApplication/profile.html')

# Individual artist page
def artist_view(request, id):
    artist = get_object_or_404(Artist, pk=id)
    if artist.album_image:
        artist.image_data = base64.b64encode(artist.album_image).decode('utf-8')
    else:
        artist.image_data = None
    return render(request, 'WebApplication/artist.html', {'artist': artist})
