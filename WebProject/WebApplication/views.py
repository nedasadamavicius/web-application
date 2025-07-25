from django.shortcuts import render
from django.shortcuts import redirect
from .services.spotify_service import SpotifyService, NoArtistsFound, SpotifyServiceError
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

spotify_service = SpotifyService()


def spotify_login(request):
    redirect_uri = settings.SPOTIFY_REDIRECT_URI
    scope = "user-read-email user-read-private user-top-read"
    auth_url = spotify_service.get_auth_url(redirect_uri, scope, show_dialog=True)
    return redirect(auth_url)


def spotify_logout(request):
    """
    Clear session data and log the user out.
    """
    request.session.flush()  # Clear all session data
    return redirect("landing")  # Send user back to landing page


def spotify_callback(request):
    code = request.GET.get('code')
    if not code:
        return redirect('landing')  # Error or denied access

    redirect_uri = redirect_uri = settings.SPOTIFY_REDIRECT_URI
    token_data = spotify_service.exchange_code_for_token(code, redirect_uri)

    # Store tokens in session
    request.session['spotify_access_token'] = token_data['access_token']
    request.session['spotify_refresh_token'] = token_data['refresh_token']
    request.session['spotify_token_expires'] = token_data['expires_in']

    request.session['is_spotify_authenticated'] = True

    return redirect('home')


# for non-authenticated users
def landing_view(request):
    genre_name = request.GET.get('genre_name', 'metal') # Default genre
    artists = []
    error_message = None

    access_token = spotify_service.get_access_token(request)

    try:
        artist_ids = spotify_service.get_artists_by_genre(genre_name, access_token)
        
        artists = spotify_service.get_artists_details_bulk(artist_ids, access_token)

    except NoArtistsFound:
        error_message = f"No artists found for the genre '{genre_name}'. Try another genre."

    except SpotifyServiceError:
        error_message = "Sorry! We’re having trouble fetching artists from Spotify right now."
    
    except Exception as e:
        error_message = "An unexpected error occurred. Please try again later."

    # these are baked-in, not fetched from Spotify
    genres = spotify_service.GENRE_SEEDS

    return render(request, "WebApplication/landing.html", {
        "artists": artists,
        "genres": genres,
        "genre": genre_name,
        "error_message": error_message
    })


# for authenticated users
def home_view(request):
# NOTE: make sure to check if access token exists in the session, if not, refresh it - in case user that's in home view has been inactive for a while.
    if not request.session.get("is_spotify_authenticated"):
        return redirect("landing")

    access_token = request.session.get("spotify_access_token")
    if not access_token:
        access_token = spotify_service.get_access_token(request) # this function will get access token, or refresh it if needed.

    user_profile = None
    genres = []
    artists = []
    selected_genre = None
    error_message = None

    # --- Fetch user profile ---
    try:
        user_profile = spotify_service.get_user_profile(access_token)
    except SpotifyServiceError:
        return redirect("landing")  # Must have profile

    # --- Fetch user’s top genres ---
    try:
        top_genres = spotify_service.get_user_top_genres(access_token)
        genres = top_genres if top_genres else []
    except SpotifyServiceError:
        genres = []
        error_message = "Couldn’t load your top genres."

    # --- Determine selected genre ---
    selected_genre = request.GET.get("genre_name")
    if not selected_genre:
        # First load: default to most played genre
        selected_genre = genres[0] if genres else None

    # --- Fetch artists for selected genre ---
    if selected_genre:
        try:
            artist_ids = spotify_service.get_artists_by_genre(selected_genre, access_token)
            artists = spotify_service.get_artists_details_bulk(artist_ids, access_token)
        except NoArtistsFound:
            error_message = f"No artists found for: {selected_genre}"
        except SpotifyServiceError:
            error_message = "Couldn’t load artists for this genre."

    return render(request, "WebApplication/home.html", {
        "user_profile": user_profile,
        "genres": genres,
        "artists": artists,
        "top_genre": selected_genre,  # 🔥 use actual selected genre
        "error_message": error_message,
    })

# NOTE: After dealing with tokens, check this - could be useful. Might be a missed detail on my part.
def artist_view(request, id):
    artist = None
    error_message = None
    access_token = spotify_service.get_access_token(request)

    # NOTE: we have a bulk list of artists details within both landing and home views
    # so we can use that to get the artist details, instead of calling service again.
    try:
        artist = spotify_service.get_artist_details(id, access_token)
    except SpotifyServiceError as e:
        error_message = "Sorry! We couldn’t load this artist’s details right now."
    except Exception as e:
        error_message = "An unexpected error occurred while loading the artist page."

    return render(request, "WebApplication/artist.html", {
        "artist": artist,
        "error_message": error_message
    })


# some info for the clueless - oo-ooh, why did u do this blabla
def about_view(request):
    return render(request, 'WebApplication/about.html')
