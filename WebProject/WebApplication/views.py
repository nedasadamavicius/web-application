from django.shortcuts import render
from django.core.cache import cache
from .spotify_api import get_access_token, fetch_artist_ids_by_genre, fetch_artist_details_home, fetch_individual_artist
from .spotify_api import NoArtistsFound

# Create your views here.

def home_view(request):
    genre_name = request.GET.get('genre_name', 'synthwave')
    access_token = get_access_token()

    try:
        artist_ids = fetch_artist_ids_by_genre(access_token, genre_name)
        artist_ids = [artist['id'] for artist in artist_ids]
        artists = fetch_artist_details_home(access_token, artist_ids)
        error_message = None
    except NoArtistsFound as e:
        artists = []
        error_message = str(e)
    except Exception as e:
        artists = []
        error_message = f"Unexpected error: {str(e)}"

    genres = cache.get('spotify_genres')

    return render(request, 'WebApplication/home.html', {
        'artists': artists,
        'genres': genres,
        'genre': genre_name,
        'error_message': error_message
    })

# # Landing page
# def home_view(request):
#     genre_name = request.GET.get('genre_name', 'synthwave')  # Initially default to 'synthwave'
#     access_token = get_access_token()

#     artist_ids = fetch_artist_ids_by_genre(access_token, genre_name)
#     artist_ids = [artist['id'] for artist in artist_ids]

#     artists = fetch_artist_details_home(access_token, artist_ids)

#     genres = cache.get('spotify_genres')

#     return render(request, 'WebApplication/home.html', {
#         'artists': artists,
#         'genres': genres,
#         'genre': genre_name
#     })


# Individual artist page
def artist_view(request, id):
    access_token = get_access_token()

    artist = fetch_individual_artist(access_token, id)

    return render(request, 'WebApplication/artist.html', {'artist': artist})


# About page
def about_view(request):
    return render(request, 'WebApplication/about.html')
