from django.conf import settings
import requests
import base64


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
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials"}

        response = requests.post(self.TOKEN_URL, headers=headers, data=data)
        if response.status_code != 200:
            raise Exception(f"Spotify auth failed: {response.status_code} {response.text}")

        self.access_token = response.json().get("access_token")
        return self.access_token

    def _get_headers(self):
        if not self.access_token:
            self.authenticate()
        return {"Authorization": f"Bearer {self.access_token}"}

    def fetch_categories(self):
        """
        Fetch Spotify browse categories (genres).
        """
        url = f"{self.BASE_URL}/browse/categories"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def search_artists_by_genre(self, genre, limit=20):
        """
        Search for artists by genre.
        """
        genre_query = genre.replace(" ", "+").lower()
        url = f"{self.BASE_URL}/search?q=genre:%22{genre_query}%22&type=artist&limit={limit}"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def fetch_artist_details(self, artist_id):
        """
        Get details of a specific artist by Spotify ID.
        """
        url = f"{self.BASE_URL}/artists/{artist_id}"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
