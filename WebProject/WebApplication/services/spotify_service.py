from django.core.cache import cache
from ..clients.spotify import SpotifyAPIClient


class NoArtistsFound(Exception):
    pass


class SpotifyService:
    def __init__(self):
        self.client = SpotifyAPIClient()

    def get_genres(self):
        """
        Fetch and cache genres.
        """
        genres = cache.get("spotify_genres")
        if genres is None:
            categories_data = self.client.fetch_categories()
            genres = [
                category['name']
                for category in categories_data.get("categories", {}).get("items", [])
            ]
            cache.set("spotify_genres", genres, timeout=60 * 60 * 24)  # 24 hours
        return genres

    def get_artists_by_genre(self, genre_name):
        """
        Get artist IDs for a given genre.
        """
        data = self.client.search_artists_by_genre(genre_name)
        artists = data.get("artists", {}).get("items", [])
        if not artists:
            raise NoArtistsFound(f"No artists found for genre '{genre_name}'")
        return [artist['id'] for artist in artists]

    def get_artist_details(self, artist_id):
        """
        Fetch details for a single artist.
        """
        artist_data = self.client.fetch_artist_details(artist_id)
        return {
            "spotify_id": artist_data.get("id"),
            "name": artist_data.get("name"),
            "popularity": artist_data.get("popularity", 0),
            "genres": artist_data.get("genres", []),
            "followers": artist_data.get("followers", {}).get("total", 0),
            "image_url": artist_data['images'][0]['url'] if artist_data.get('images') else None,
            "external_url": artist_data.get("external_urls", {}).get("spotify", "")
        }

    def get_artists_details_bulk(self, artist_ids):
        """
        Fetch details for a list of artist IDs.
        """
        return [
            self.get_artist_details(artist_id)
            for artist_id in artist_ids
        ]
