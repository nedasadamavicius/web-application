from django.conf import settings
from django.core.cache import cache
import requests


# Self-explanatory
def get_access_token():
    client_id = settings.SPOTIFY_CLIENT_ID
    client_secret = settings.SPOTIFY_CLIENT_SECRET

    url = "https://accounts.spotify.com/api/token"

    response = requests.post(url, auth=(client_id, client_secret), data={'grant_type': 'client_credentials'})

    return response.json().get('access_token')


# Helper for caching
def fetch_genres(access_token):
    url = "https://api.spotify.com/v1/recommendations/available-genre-seeds"

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(url, headers=headers)

    return response.json().get('genres', [])


# Self-explanatory function
def fetch_and_cache_genres():
    genres = cache.get('spotify_genres')
    if not genres:
        access_token = get_access_token()
        genres = fetch_genres(access_token)
        cache.set('spotify_genres', genres, timeout=86400)  # Cache for 24 hours
    return genres


# Self-explanatory function
def fetch_artist_ids_by_genre(access_token, genre_name):
    genre_query = genre_name.replace(" ", "+").lower()

    url = f"https://api.spotify.com/v1/search?q=genre:%22{genre_query}%22&type=artist&limit=20"

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        artists = response.json().get('artists', {}).get('items', [])
        return [{'id': artist['id']} for artist in artists]
    else:
        return []


# Function to get Artist object from the Spotify API, then parse it and return a list of artists   
def fetch_artist_details_home(access_token, artist_ids):
    detailed_artists = []

    for artist_id in artist_ids:
        url = f"https://api.spotify.com/v1/artists/{artist_id}"
        
        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            artist_details = response.json()
            detailed_artists.append({
                'spotify_id': artist_details['id'],
                'image_url': artist_details['images'][0]['url'] if 'images' in artist_details and artist_details['images'] else None,
                'name': artist_details['name'],
                'popularity': artist_details.get('popularity', 0)
            })
        else:
            print(f"Failed to fetch details for artist ID: {artist_id}")

    return detailed_artists


def fetch_individual_artist(access_token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        artist_details = response.json()
        return {
            'spotify_id': artist_details.get('id'),
            'image_url': artist_details['images'][0]['url'] if artist_details.get('images') and len(artist_details['images']) > 0 else None,
            'name': artist_details.get('name'),
            'popularity': artist_details.get('popularity', 0),
            'genres': artist_details.get('genres', []),
            'followers': artist_details.get('followers', {}).get('total', 0),
            'external_url': artist_details.get('external_urls', {}).get('spotify', '')
        }
    else:
        raise Exception(f"Failed to fetch details for artist ID: {artist_id}")