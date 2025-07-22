from django.shortcuts import render
from django.core.cache import cache
from .services.spotify_service import SpotifyService, NoArtistsFound, SpotifyServiceError


spotify_service = SpotifyService()


def home_view(request):
    genre_name = request.GET.get('genre_name', 'synthwave')
    artists = []
    error_message = None

    try:
        # Fetch artist IDs and details
        artist_ids = spotify_service.get_artists_by_genre(genre_name)
        artists = spotify_service.get_artists_details_bulk(artist_ids)

    except NoArtistsFound:
        error_message = f"No artists found for the genre '{genre_name}'. Try another genre."
    except SpotifyServiceError:
        error_message = "Sorry! We’re having trouble fetching artists from Spotify right now."
    except Exception as e:
        error_message = "An unexpected error occurred. Please try again later."

    # Get genres (SpotifyService caches them)
    try:
        genres = spotify_service.get_genres()
    except SpotifyServiceError:
        genres = []
        if not error_message:
            error_message = "Could not load genres from Spotify."

    return render(request, "WebApplication/home.html", {
        "artists": artists,
        "genres": genres,
        "genre": genre_name,
        "error_message": error_message
    })


def artist_view(request, id):
    artist = None
    error_message = None

    try:
        artist = spotify_service.get_artist_details(id)
    except SpotifyServiceError as e:
        error_message = "Sorry! We couldn’t load this artist’s details right now."
    except Exception as e:
        error_message = "An unexpected error occurred while loading the artist page."

    return render(request, "WebApplication/artist.html", {
        "artist": artist,
        "error_message": error_message
    })


def about_view(request):
    return render(request, 'WebApplication/about.html')
