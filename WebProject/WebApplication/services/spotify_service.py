import logging
from django.core.cache import cache
from ..clients.spotify import SpotifyAPIClient, SpotifyAPIError

logger = logging.getLogger(__name__)


class SpotifyServiceError(Exception):
    """Base class for Spotify service-related errors."""


class NoArtistsFound(SpotifyServiceError):
    """Raised when no artists are found for a genre."""


class SpotifyService:
    def __init__(self):
        logger.info("SpotifyService initialized")
        self.client = SpotifyAPIClient()

    def get_genres(self):
        """
        Fetch and cache genres.
        """
        logger.info("SpotifyService.get_genres() called")
        try:
            def fetch_and_format_genres():
                logger.debug("Cache miss for spotify_genres, fetching from Spotify API")
                categories_data = self.client.fetch_categories()
                genres = [
                    category['name']
                    for category in categories_data.get("categories", {}).get("items", [])
                ]
                logger.info("Genres fetched and will be cached")
                return genres

            # Use get_or_set to ensure only one fetch even if multiple processes call this
            genres = cache.get_or_set(
                "spotify_genres",
                fetch_and_format_genres,
                timeout=60 * 60 * 24  # 24 hours
            )

            if genres:
                logger.debug("Cache hit for spotify_genres")
            return genres

        except SpotifyAPIError as e:
            logger.error(f"Error fetching genres from Spotify API: {str(e)}")
            raise SpotifyServiceError("Failed to fetch genres") from e

        except Exception as e:
            logger.exception("Unexpected error in get_genres()")
            raise SpotifyServiceError("Unexpected error in get_genres()") from e

    def get_artists_by_genre(self, genre_name):
        """
        Get artist IDs for a given genre.
        """
        logger.info(f"SpotifyService.get_artists_by_genre('{genre_name}') called")
        try:
            data = self.client.search_artists_by_genre(genre_name)
            artists = data.get("artists", {}).get("items", [])
            if not artists:
                logger.warning(f"No artists found for genre '{genre_name}'")
                raise NoArtistsFound(f"No artists found for genre '{genre_name}'")

            artist_ids = [artist['id'] for artist in artists]
            logger.debug(f"Found {len(artist_ids)} artists for genre '{genre_name}'")
            return artist_ids

        except SpotifyAPIError as e:
            logger.error(f"Error searching artists for genre '{genre_name}': {str(e)}")
            raise SpotifyServiceError("Failed to fetch artists by genre") from e

        except Exception as e:
            logger.exception("Unexpected error in get_artists_by_genre()")
            raise SpotifyServiceError("Unexpected error in get_artists_by_genre()") from e

    def get_artist_details(self, artist_id):
        """
        Fetch details for a single artist.
        """
        logger.info(f"SpotifyService.get_artist_details('{artist_id}') called")
        try:
            artist_data = self.client.fetch_artist_details(artist_id)
            artist_info = {
                "spotify_id": artist_data.get("id"),
                "name": artist_data.get("name"),
                "popularity": artist_data.get("popularity", 0),
                "genres": artist_data.get("genres", []),
                "followers": artist_data.get("followers", {}).get("total", 0),
                "image_url": artist_data['images'][0]['url'] if artist_data.get('images') else None,
                "external_url": artist_data.get("external_urls", {}).get("spotify", "")
            }
            logger.debug(f"Fetched details for artist {artist_info['name']} ({artist_id})")
            return artist_info

        except SpotifyAPIError as e:
            logger.error(f"Error fetching artist details for ID '{artist_id}': {str(e)}")
            raise SpotifyServiceError("Failed to fetch artist details") from e

        except Exception as e:
            logger.exception("Unexpected error in get_artist_details()")
            raise SpotifyServiceError("Unexpected error in get_artist_details()") from e

    def get_artists_details_bulk(self, artist_ids):
        """
        Fetch details for a list of artist IDs.
        """
        logger.info(f"SpotifyService.get_artists_details_bulk() called for {len(artist_ids)} artists")
        details_list = []
        for artist_id in artist_ids:
            try:
                details = self.get_artist_details(artist_id)
                details_list.append(details)
            except SpotifyServiceError as e:
                logger.warning(f"Skipping artist ID '{artist_id}' due to error: {str(e)}")
                continue  # Skip failed artist and continue
        logger.debug(f"Successfully fetched details for {len(details_list)} artists")
        return details_list
