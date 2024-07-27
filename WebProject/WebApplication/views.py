from django.shortcuts import render
from django.core.cache import cache
from django.http import JsonResponse
from .models import Artist
from .spotify_api import get_access_token, fetch_artist_ids_by_genre, fetch_artist_details
import base64

# Create your views here.

# Landing page
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


# Individual artist page
def artist_view(request, id):
    access_token = get_access_token()

    artist_details = fetch_artist_details(access_token, id)
    
    artist = {
        'spotify_id': artist_details['id'],
        'image_url': artist_details['images'][0]['url'] if 'images' in artist_details and artist_details['images'] else None,
        'name': artist_details['name'],
        'popularity': artist_details.get('popularity', 0)
    }

    return render(request, 'WebApplication/artist.html', {'artist': artist})
