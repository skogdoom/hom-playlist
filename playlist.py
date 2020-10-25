from secrets import spotify_client_id, spotify_client_secret, spotify_user_id
import requests
from bs4 import BeautifulSoup, NavigableString
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from time import sleep


def get_bands():
    source = requests.get('https://www.houseofmetal.se/en/history/').text
    soup = BeautifulSoup(source, 'html.parser')
    elements = soup.select('div.et_pb_text_inner')
    bands_by_year = {}
    for element in elements:
        year = element.find('strong')

        if year is None:
            continue

        bands = element.find('p')

        band_list = []
        for b in bands:
            if isinstance(b, NavigableString):
                band_list.append(b)

        bands_by_year[year.text] = band_list

    return bands_by_year


def find_songs(client, artist):
    results = client.search(q=artist, type='artist')

    items = list(filter(lambda i: i['name'] == artist, results['artists']['items']))
    track_ids = []

    if len(items) > 0:
        artist_id = 'spotify:artist:' + items[0]['id']
        top_tracks = client.artist_top_tracks(artist_id)

        for track in top_tracks['tracks'][:3]:
            track_ids.append(track['id'])

    return track_ids


def create_playlist(client, year):
    playlist = client.user_playlist_create(
        spotify_user_id,
        "HoM {year}",
        True,
        False,
        f"Songs from the House of Metal (houseofmetal.se) lineup {year}"
    )

    return playlist['id']


def add_songs_to_playlist(client, playlist_id, songs):
    client.playlist_add_items(playlist_id, songs)


def get_spotify_client():
    client_credentials_manager = SpotifyClientCredentials(
        client_id=spotify_client_id,
        client_secret=spotify_client_secret
    )
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def get_spotify_client_auth():
    scope = "playlist-modify-public"
    auth_manager = SpotifyOAuth(
        client_id=spotify_client_id,
        client_secret=spotify_client_secret,
        scope=scope,
        redirect_uri="http://localhost"
    )
    return spotipy.Spotify(auth_manager=auth_manager)


def create_playlists():
    print("Getting bands by year from https://www.houseofmetal.se/en/history/")
    bands_by_year = get_bands()

    client = get_spotify_client_auth()

    for year, bands in bands_by_year.items():
        print(f"Creating playlist for {year}...")
        playlist_id = create_playlist(client, year)
        for artist in bands_by_year[year]:
            print(f"Finding songs for {artist}...")
            songs = find_songs(client, artist)
            if len(songs) > 0:
                add_songs_to_playlist(client, playlist_id, songs)
        sleep(5)  # to make sure we don't hit the rate limit


if __name__ == '__main__':
    create_playlists()
