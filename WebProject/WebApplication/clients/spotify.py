from django.conf import settings
import requests
import base64
import logging
import urllib.parse
import time
from django.core.cache import cache

logger = logging.getLogger(__name__)


class SpotifyAPIError(Exception):
    """Base class for Spotify API related errors."""


class SpotifyAuthError(SpotifyAPIError):
    """Raised when Spotify authentication fails."""


class SpotifyRequestError(SpotifyAPIError):
    """Raised when a request to Spotify API fails."""


# SpotifyAPIClient is a client for interacting with the Spotify Web API.
    # It literally deals with low-level API requests, no business logic - that lives in `services/spotify_service.py`.
class SpotifyAPIClient:
    TOKEN_URL = "https://accounts.spotify.com/api/token"
    BASE_URL = "https://api.spotify.com/v1"
    AUTH_URL = "https://accounts.spotify.com/authorize"

    CLIENT_TOKEN_KEY = "spotify_client_access_token"
    CLIENT_TOKEN_EXPIRY_KEY = "spotify_client_token_expires_at"

    def __init__(self):
        self.client_id = settings.SPOTIFY_CLIENT_ID
        self.client_secret = settings.SPOTIFY_CLIENT_SECRET

# Get an OAuth access token using client credentials.
    # This method is used to authenticate the client and obtain an access token.
    def authenticate_client(self):
        logger.info("SpotifyAPIClient.authenticate_client() called")

        try:
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()

            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            data = {"grant_type": "client_credentials"}

            response = requests.post(self.TOKEN_URL, headers=headers, data=data)
            response.raise_for_status()

            response_data = response.json()
            access_token = response_data.get("access_token")
            expires_in = response_data.get("expires_in", 3600)

            expires_at = time.time() + expires_in

            # Cache token and expiry
            cache.set(self.CLIENT_TOKEN_KEY, access_token, timeout=expires_in)
            cache.set(self.CLIENT_TOKEN_EXPIRY_KEY, expires_at, timeout=expires_in)

            logger.info("Spotify client access token refreshed and cached")
            return access_token

        except requests.RequestException as e:
            logger.exception("Failed to authenticate with Spotify")
            raise SpotifyAuthError("Failed to authenticate with Spotify") from e

# Helper function to get clients access token, and if need be, refresh it.
    def get_client_access_token(self):
        access_token = cache.get(self.CLIENT_TOKEN_KEY)
        expires_at = cache.get(self.CLIENT_TOKEN_EXPIRY_KEY)

        if not access_token or not expires_at or time.time() >= expires_at:
            logger.info("Cached token missing or expired — refreshing")
            return self.authenticate_client()

        return access_token

# Build headers for API requests
    def build_headers(self, access_token):
        logger.debug("SpotifyAPIClient.build_headers() called")
        
        if not access_token:
            raise SpotifyAuthError("Access token is required but not provided")
        
        return {"Authorization": f"Bearer {access_token}"}

# Generate Spotify OAuth2 authorization URL.
    # This URL is used to redirect users to Spotify for authentication and authorization.
    def get_auth_url(self, redirect_uri, scope=None, state=None, show_dialog=False):
        """
        Generate Spotify OAuth2 authorization URL.
        """
        logger.info("SpotifyAPIClient.get_auth_url() called")
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
        }
        if scope:
            params["scope"] = scope
        if state:
            params["state"] = state
        if show_dialog:
            params["show_dialog"] = "true"

        url = f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}"
        logger.debug(f"Generated Spotify auth URL: {url}")
        return url
    
# Exchange authorization code for access and refresh tokens - for auth users.
    # This method is called after the user has authenticated and authorized the application.
    def exchange_code_for_token(self, code, redirect_uri):
        """
        Exchange authorization code for access and refresh tokens.
        """
        logger.info("SpotifyAPIClient.exchange_code_for_token() called")
        try:
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            response = requests.post(self.TOKEN_URL, data=data, headers=headers)
            response.raise_for_status()
            token_data = response.json()

            logger.debug(f"Received token data: {token_data}")
            return {
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token"),
                "expires_in": token_data.get("expires_in"),
                "scope": token_data.get("scope"),
                "token_type": token_data.get("token_type"),
            }

        except requests.HTTPError as e:
            logger.error(f"HTTP error exchanging code for token: {e.response.status_code} {e.response.text}")
            raise SpotifyAuthError(f"Failed to exchange code for token: {e.response.status_code}") from e

        except requests.RequestException as e:
            logger.exception("Network error during token exchange")
            raise SpotifyAuthError("Network error during token exchange") from e


# Refresh the user's access token using their refresh token - for auth users.
    # This method is used to obtain a new access token when the current one expires.
    def refresh_access_token(self, refresh_token):
        """
        Refresh the user's access token using their refresh token.
        """
        logger.info("SpotifyAPIClient.refresh_access_token() called")

        try:
            data = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }

            response = requests.post(self.TOKEN_URL, data=data, headers=headers)
            response.raise_for_status()
            token_data = response.json()

            logger.debug(f"Refreshed user token: {token_data}")
            return {
                "access_token": token_data.get("access_token"),
                "expires_in": token_data.get("expires_in"),
                "scope": token_data.get("scope"),
                "token_type": token_data.get("token_type"),
            }

        except requests.RequestException as e:
            logger.exception("Error refreshing Spotify user access token")
            raise SpotifyAuthError("Failed to refresh user access token") from e


    def search_artists_by_genre(self, genre, access_token, limit=20):
        """
        Search for artists by genre.
        """
        logger.info(f"SpotifyAPIClient.search_artists_by_genre('{genre}') called")

        # to properly encode the query: genre:"metal" -> genre%3A%22metal%22
        query = f'genre:"{genre.lower()}"'
        encoded_query = urllib.parse.quote(query)

        url = f"{self.BASE_URL}/search?q={encoded_query}&type=artist&limit={limit}"

        try:
            response = requests.get(url, headers=self.build_headers(access_token))
            response.raise_for_status()
            logger.debug(f"Search results: {response.json()}")
            return response.json()["artists"]["items"]

        except requests.HTTPError as e:
            logger.error(f"HTTP error in search_artists_by_genre: {e.response.status_code} {e.response.text}")
            raise SpotifyRequestError(f"Failed to search artists: {e.response.status_code}") from e

        except requests.RequestException as e:
            logger.exception("Network error during search_artists_by_genre")
            raise SpotifyRequestError("Network error during search_artists_by_genre") from e


    def fetch_artist_details(self, artist_id, access_token):
        """
        Get details of a specific artist by Spotify ID.
        """
        logger.info(f"SpotifyAPIClient.fetch_artist_details('{artist_id}') called")

        url = f"{self.BASE_URL}/artists/{artist_id}"
        try:
            response = requests.get(url, headers=self.build_headers(access_token))
            response.raise_for_status()
            logger.debug(f"Artist details: {response.json()}")
            return response.json()
        except requests.HTTPError as e:
            logger.error(f"HTTP error in fetch_artist_details: {e.response.status_code} {e.response.text}")
            raise SpotifyRequestError(f"Failed to fetch artist details: {e.response.status_code}") from e
        except requests.RequestException as e:
            logger.exception("Network error during fetch_artist_details")
            raise SpotifyRequestError("Network error during fetch_artist_details") from e

# Get the current user's profile information using their access token - retrieved from `exchange_code_for_token()`.
    # This method retrieves the user's profile data from Spotify.
    def get_user_profile(self, access_token):
        """
        Fetch the current Spotify user's profile using their access token.
        """
        logger.info("SpotifyAPIClient.get_user_profile() called")

        url = f"{self.BASE_URL}/me"

        try:
            response = requests.get(url, headers=self.build_headers(access_token))
            response.raise_for_status()
            user_data = response.json()
            logger.debug(f"Fetched user profile: {user_data}")
            return user_data

        except requests.HTTPError as e:
            logger.error(f"HTTP error fetching user profile: {e.response.status_code} {e.response.text}")
            raise SpotifyRequestError(f"Failed to fetch user profile: {e.response.status_code}") from e

        except requests.RequestException as e:
            logger.exception("Network error during get_user_profile")
            raise SpotifyRequestError("Network error during get_user_profile") from e


    def get_user_top_artists(self, access_token, limit=20, time_range="long_term"):
        """
        Fetch user's top artists from Spotify API.
        """
        logger.info("SpotifyAPIClient.get_user_top_artists() called")

        url = f"{self.BASE_URL}/me/top/artists?limit={limit}&time_range={time_range}"
        
        try:
            response = requests.get(url, headers=self.build_headers(access_token))
            response.raise_for_status()
            return response.json()
        
        except requests.HTTPError as e:
            logger.error(f"HTTP error in get_user_top_artists: {e.response.status_code} {e.response.text}")
            raise SpotifyRequestError("Failed to fetch user’s top artists")
    
