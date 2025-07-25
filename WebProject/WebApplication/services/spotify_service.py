import logging
from django.core.cache import cache
from ..clients.spotify import SpotifyAPIClient, SpotifyAPIError

logger = logging.getLogger(__name__)


class SpotifyServiceError(Exception):
    """Base class for Spotify service-related errors."""


class NoArtistsFound(SpotifyServiceError):
    """Raised when no artists are found for a genre."""

class SpotifyRequestError(SpotifyServiceError):
    """Raised when there is an error in the Spotify API request."""


class SpotifyService:
# Baked-in genre seeds for non-authenticated users
    GENRE_SEEDS = [
        "hiphop","r&b","rock","pop","latin","country",
        "soul","electronic","jazz","metal","indie",
        "blues"
    ]

    def __init__(self):
        logger.info("SpotifyService initialized")
        self.client = SpotifyAPIClient()


# NOTE: SECTION FOR FUNCTIONS RELATED TO USER AUTHENTICATION.
# Generate Spotify authorization URL that is used to redirect users to Spotify for authentication.
    def get_auth_url(self, redirect_uri, scope=None, state=None, show_dialog=False):
        """
        Generate Spotify authorization URL.
        """
        logger.info("SpotifyService.get_auth_url() called")
        return self.client.get_auth_url(redirect_uri, scope, state, show_dialog)


# This is called once after the user has authenticated with Spotify and granted permissions.
    def exchange_code_for_token(self, code, redirect_uri):
        """
        Exchange authorization code for access and refresh tokens.
        """
        logger.info("SpotifyService.exchange_code_for_token() called")
        return self.client.exchange_code_for_token(code, redirect_uri)


# Refresh the user's access token using their refresh token.
    def refresh_access_token(self, refresh_token):
        logger.info("SpotifyService.refresh_access_token() called")
        return self.client.refresh_access_token(refresh_token)


# NOTE: SECTION FOR FUNCTIONS THAT ONLY AUTHENTICATED USERS CAN MAKE USE OF
# Fetch user profile information.
    def get_user_profile(self, access_token):
        """
        Fetch and return Spotify user profile info.
        """
        logger.info("SpotifyService.get_user_profile() called")
        try:
            user_data = self.client.get_user_profile(access_token)
            profile_info = {
                "id": user_data.get("id"),
                "display_name": user_data.get("display_name"),
                "email": user_data.get("email"),
                "profile_url": user_data.get("external_urls", {}).get("spotify"),
                "image_url": (
                    user_data.get("images", [{}])[0].get("url")
                    if user_data.get("images") else None
                ),
                "country": user_data.get("country"),
                "followers": user_data.get("followers", {}).get("total"),
            }
            logger.debug(f"Formatted user profile info: {profile_info}")
            return profile_info

        except SpotifyRequestError as e:
            logger.error(f"Error fetching user profile: {str(e)}")
            raise SpotifyServiceError("Failed to fetch user profile") from e

        except Exception as e:
            logger.exception("Unexpected error in get_user_profile()")
            raise SpotifyServiceError("Unexpected error in get_user_profile") from e


# Fetch user's top genres based on their listening history.
    def get_user_top_genres(self, access_token, limit=20):
        """
        Fetch user's top artists and derive most frequent genres from them.
        This reflects what genres the user listens to most based on artist metadata.
        """
        logger.info("SpotifyService.get_user_top_genres() called")
        
        try:
            # 1. Fetch user's top 50 artists from Spotify (based on listening history)
            top_artists_data = self.client.get_user_top_artists(access_token, limit=50)

            genres = []

            # 2. Collect all genre tags from those top artists
            for artist in top_artists_data.get("items", []):
                genres.extend(artist.get("genres", []))  # One artist can have multiple genre labels

            # 3. Count how often each genre appears across the user's top artists
            genre_freq = {}
            for genre in genres:
                genre_freq[genre] = genre_freq.get(genre, 0) + 1  # Increment frequency count

            # 4. Sort genres by frequency, from most common to least
            sorted_genres = sorted(genre_freq, key=genre_freq.get, reverse=True)

            # 5. Return the top N genres, based on the provided limit
            logger.debug(f"User top genres: {sorted_genres[:limit]}")
            return sorted_genres[:limit]

        except SpotifyAPIError as e:
            logger.error(f"Error fetching user’s top genres: {str(e)}")
            raise SpotifyServiceError("Failed to fetch user’s top genres")
        

# NOTE: SECTION OF FUNCTIONS THAT CAN BE USED BY BOTH AUTHENTICATED AND NON-AUTHENTICATED USERS.
# Get access token, distiguishing between authenticated and non-authenticated users.
    def get_access_token(self, request):
        if request.session.get("is_spotify_authenticated"):
            access_token = request.session.get("spotify_access_token")
            
            if not access_token:
                logger.info("No access token found in session - attempting to refresh token")
                refresh_token = request.session.get("spotify_refresh_token")
                
                if not refresh_token:
                    logger.error("Authenticated user missing refresh token – cannot proceed")
                    raise SpotifyRequestError("Missing refresh token for authenticated user")
                
                token_data = self.refresh_access_token(refresh_token)
                access_token = token_data.get("access_token")
                request.session["spotify_access_token"] = access_token
                request.session.modified = True
            
            return access_token
        else:
            logger.info("Non-authenticated user - using default access token")
            return self.client.get_client_access_token()
            

    def get_artists_by_genre(self, genre_name, access_token):
        """
        Get artist IDs for a given genre, with Redis caching.
        """
        logger.info(f"SpotifyService.get_artists_by_genre('{genre_name}') called")

        cache_key = f"artists_for_genre:{genre_name.lower()}"
        cached = cache.get(cache_key)
        if cached:
            logger.debug(f"Cache hit for {cache_key}")
            return cached

        try:
            logger.info(f"Access token being used: {access_token}")
            artists = self.client.search_artists_by_genre(genre_name, access_token)
            if not artists:
                logger.warning(f"No artists found for genre '{genre_name}'")
                raise NoArtistsFound(f"No artists found for genre '{genre_name}'")

            artist_ids = [artist['id'] for artist in artists]
            cache.set(cache_key, artist_ids, timeout=60 * 60)  # 1 hour cache
            logger.debug(f"Cached artist IDs for genre '{genre_name}'")
            return artist_ids

        except SpotifyAPIError as e:
            logger.error(f"Error searching artists for genre '{genre_name}': {str(e)}")
            raise SpotifyServiceError("Failed to fetch artists by genre") from e

        except Exception as e:
            logger.exception("Unexpected error in get_artists_by_genre()")
            raise SpotifyServiceError("Unexpected error in get_artists_by_genre()") from e


    def get_artist_details(self, artist_id, access_token):
        """
        Fetch details for a single artist, with Redis caching.
        """
        logger.info(f"SpotifyService.get_artist_details('{artist_id}') called")

        cache_key = f"artist_details:{artist_id}"
        
        cached = cache.get(cache_key)

        if cached:
            logger.debug(f"Cache hit for {cache_key}")

            return cached

        try:
            artist_data = self.client.fetch_artist_details(artist_id, access_token)

            artist_info = {
                "spotify_id": artist_data.get("id"),
                "name": artist_data.get("name"),
                "popularity": artist_data.get("popularity", 0),
                "genres": artist_data.get("genres", []),
                "followers": artist_data.get("followers", {}).get("total", 0),
                "image_url": artist_data['images'][0]['url'] if artist_data.get('images') else None,
                "external_url": artist_data.get("external_urls", {}).get("spotify", "")
            }

            cache.set(cache_key, artist_info, timeout=60 * 60)  # Cache for 1 hour
            logger.debug(f"Cached artist details for {artist_id}")

            return artist_info

        except SpotifyAPIError as e:
            logger.error(f"Error fetching artist details for ID '{artist_id}': {str(e)}")
            raise SpotifyServiceError("Failed to fetch artist details") from e

        except Exception as e:
            logger.exception("Unexpected error in get_artist_details()")
            raise SpotifyServiceError("Unexpected error in get_artist_details()") from e


    def get_artists_details_bulk(self, artist_ids, access_token):
        """
        Fetch details for a list of artist IDs.
        """
        logger.info(f"SpotifyService.get_artists_details_bulk() called for {len(artist_ids)} artists")

        details_list = []
        
        for artist_id in artist_ids:
            try:
                details = self.get_artist_details(artist_id, access_token)
                
                details_list.append(details)
            
            except SpotifyServiceError as e:
                logger.warning(f"Skipping artist ID '{artist_id}' due to error: {str(e)}")
                
                continue  # Skip failed artist and continue
        
        logger.debug(f"Successfully fetched details for {len(details_list)} artists")
        
        return details_list

