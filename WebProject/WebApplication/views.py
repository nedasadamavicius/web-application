from django.shortcuts import render, get_object_or_404
from django.core.cache import cache
from django.http import JsonResponse
from .models import Artist
from .spotify_api import get_access_token, fetch_artist_ids_by_genre, fetch_artist_details
import base64

# Create your views here.

def home_view(request):
    genre_name = request.GET.get('genre_name', 'synthwave')  # Initially default to 'synthwave'
    access_token = get_access_token()

    artist_ids = fetch_artist_ids_by_genre(access_token, genre_name)
    artist_ids = [artist['id'] for artist in artist_ids]

    artists = fetch_artist_details(access_token, artist_ids)

    genres = cache.get('spotify_genres')

    return render(request, 'WebApplication/home.html', {
        'artists': artists,
        'genres': genres,
        'genre': genre_name
    })


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
