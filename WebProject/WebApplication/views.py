from django.shortcuts import render
from django.core.cache import cache
from .services.spotify_service import SpotifyService, NoArtistsFound


spotify_service = SpotifyService()


def home_view(request):
    genre_name = request.GET.get('genre_name', 'synthwave')

    try:
        # Get artist IDs and their details
        artist_ids = spotify_service.get_artists_by_genre(genre_name)
        artists = spotify_service.get_artists_details_bulk(artist_ids)
        error_message = None
    except NoArtistsFound as e:
        artists = []
        error_message = str(e)
    except Exception as e:
        artists = []
        error_message = f"Unexpected error: {str(e)}"

    # Get genres from cache (already handled in SpotifyService)
    genres = spotify_service.get_genres()

    return render(request, 'WebApplication/home.html', {
        'artists': artists,
        'genres': genres,
        'genre': genre_name,
        'error_message': error_message
    })


def artist_view(request, id):
    try:
        artist = spotify_service.get_artist_details(id)
    except Exception as e:
        # Optionally, handle artist fetch errors gracefully
        artist = None
        error_message = f"Error fetching artist: {str(e)}"
        return render(request, 'WebApplication/artist.html', {
            'artist': artist,
            'error_message': error_message
        })

    return render(request, 'WebApplication/artist.html', {'artist': artist})


def about_view(request):
    return render(request, 'WebApplication/about.html')
