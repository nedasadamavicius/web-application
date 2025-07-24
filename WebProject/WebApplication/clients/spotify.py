from django.conf import settings
import requests
import base64
import logging
import urllib.parse

logger = logging.getLogger(__name__)


class SpotifyAPIError(Exception):
    """Base class for Spotify API related errors."""


class SpotifyAuthError(SpotifyAPIError):
    """Raised when Spotify authentication fails."""


class SpotifyRequestError(SpotifyAPIError):
    """Raised when a request to Spotify API fails."""


class SpotifyAPIClient:
    TOKEN_URL = "https://accounts.spotify.com/api/token"
    BASE_URL = "https://api.spotify.com/v1"
    AUTH_URL = "https://accounts.spotify.com/authorize"


    def __init__(self):
        self.client_id = settings.SPOTIFY_CLIENT_ID
        self.client_secret = settings.SPOTIFY_CLIENT_SECRET
        self.access_token = None


    def authenticate(self):
        """
        Get an OAuth access token using client credentials.
        """
        logger.info("SpotifyAPIClient.authenticate() called")
        try:
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()

            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            data = {"grant_type": "client_credentials"}

            response = requests.post(self.TOKEN_URL, headers=headers, data=data)

            if response.status_code != 200:
                logger.error(f"Authentication failed: {response.status_code} {response.text}")
                raise SpotifyAuthError("Failed to authenticate with Spotify API")

            self.access_token = response.json().get("access_token")
            logger.info("Spotify authentication succeeded")
            return self.access_token

        except requests.RequestException as e:
            logger.exception("Network error during Spotify authentication")
            raise SpotifyAuthError("Network error during Spotify authentication") from e


    def _get_headers(self):
        logger.debug("SpotifyAPIClient._get_headers() called")
        if not self.access_token:
            logger.warning("Access token missing; calling authenticate()")
            self.authenticate()
        return {"Authorization": f"Bearer {self.access_token}"}


    def get_auth_url(self, redirect_uri, scope=None, state=None):
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

        url = f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}"
        logger.debug(f"Generated Spotify auth URL: {url}")
        return url
    

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
        

    def search_artists_by_genre(self, genre, limit=20):
        """
        Search for artists by genre.
        """
        logger.info(f"SpotifyAPIClient.search_artists_by_genre('{genre}') called")

        genre_query = genre.replace(" ", "+").lower()
        
        url = f"{self.BASE_URL}/search?q=genre:%22{genre_query}%22&type=artist&limit={limit}"
        
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            logger.debug(f"Search results: {response.json()}")
            return response.json()["artists"]["items"]
        
        except requests.HTTPError as e:
            logger.error(f"HTTP error in search_artists_by_genre: {e.response.status_code} {e.response.text}")
            raise SpotifyRequestError(f"Failed to search artists: {e.response.status_code}") from e
        
        except requests.RequestException as e:
            logger.exception("Network error during search_artists_by_genre")
            raise SpotifyRequestError("Network error during search_artists_by_genre") from e


    def fetch_artist_details(self, artist_id):
        """
        Get details of a specific artist by Spotify ID.
        """
        logger.info(f"SpotifyAPIClient.fetch_artist_details('{artist_id}') called")
        url = f"{self.BASE_URL}/artists/{artist_id}"
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            logger.debug(f"Artist details: {response.json()}")
            return response.json()
        except requests.HTTPError as e:
            logger.error(f"HTTP error in fetch_artist_details: {e.response.status_code} {e.response.text}")
            raise SpotifyRequestError(f"Failed to fetch artist details: {e.response.status_code}") from e
        except requests.RequestException as e:
            logger.exception("Network error during fetch_artist_details")
            raise SpotifyRequestError("Network error during fetch_artist_details") from e


    def get_user_profile(self, access_token):
        """
        Fetch the current Spotify user's profile using their access token.
        """
        logger.info("SpotifyAPIClient.get_user_profile() called")
        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"{self.BASE_URL}/me"

        try:
            response = requests.get(url, headers=headers)
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
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            logger.error(f"HTTP error in get_user_top_artists: {e.response.status_code} {e.response.text}")
            raise SpotifyRequestError("Failed to fetch user’s top artists")
    
