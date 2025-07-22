from django.conf import settings
import requests
import base64
import logging

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

    def fetch_categories(self):
        """
        Fetch Spotify browse categories (genres).
        """
        logger.info("SpotifyAPIClient.fetch_categories() called")
        url = f"{self.BASE_URL}/browse/categories"
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            logger.debug(f"Fetched categories: {response.json()}")
            return response.json()
        except requests.HTTPError as e:
            logger.error(f"HTTP error in fetch_categories: {e.response.status_code} {e.response.text}")
            raise SpotifyRequestError(f"Failed to fetch categories: {e.response.status_code}") from e
        except requests.RequestException as e:
            logger.exception("Network error during fetch_categories")
            raise SpotifyRequestError("Network error during fetch_categories") from e

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
            return response.json()
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
