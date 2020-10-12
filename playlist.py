import requests
from bs4 import BeautifulSoup, NavigableString
import json
from secrets import spotify_client_id, spotify_client_secret, spotify_user_id
import base64
import uuid
import hashlib
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from time import sleep

def get_bands():
    print("Gotta go get a dictionary by year from https://www.houseofmetal.se/en/history/")

    source = requests.get('https://www.houseofmetal.se/en/history/').text
    soup = BeautifulSoup(source, 'html.parser')
    elements = soup.select('div.et_pb_text_inner')
    bandsByYear = {}
    for element in elements:
        year = element.find('strong')

        if (year == None):
            continue

        bands = element.find('p')

        bandList = []
        for b in bands:
            if (isinstance(b, NavigableString)):
                bandList.append(b)

        bandsByYear[year.text] = bandList

    return bandsByYear


def print_bands(bands_by_year):
    for year, bands in bands_by_year.items():
        print(year)
        for band in bands:
            print(band)


def find_songs(client, artist):
    print("finding songs for " + artist + "...")
    #sp = get_spotify_client()
    results = client.search(q='artist:' + artist, type='artist')

    items = results['artists']['items']
    track_ids = []

    if len(items) > 0:
        # print(items[0]['id'])
        # print(items[0]['name'])
        artist_id = 'spotify:artist:' + items[0]['id']

        top_tracks = client.artist_top_tracks(artist_id)

        for track in top_tracks['tracks'][:3]:
            track_ids.append(track['id'])
            # print(track['id'])
            # print(track['name'])

    return track_ids


def create_playlist(client, year):
    print("create playlists...")

    #sp = get_spotify_client_auth()

    playlist = client.user_playlist_create(
        spotify_user_id,
        "HOM {}".format(year),
        True,
        False,
        "Songs from the House of Metal (houseofmetal.se) lineup {}".format(year)
    )
    print(playlist)
    return playlist['id']


def add_songs_to_playlist(client, playlist_id, songs):
    #sp = get_spotify_client_auth()
    client.playlist_add_items(playlist_id, songs)


def call_spotify_test():
    sp = get_spotify_client()
    track_results = sp.search(q='metallica', type='track', limit=5, offset=0)
    print(track_results)


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


if __name__ == '__main__':
    bands_by_year = get_bands()
    # print_bands(bands_by_year)

    client = get_spotify_client_auth()

    #create_playlist("2020")
    #add_songs_to_playlist('6MmOQ2bRz7TsjiEyn7aIfO', find_songs('metallica'))

    for year, bands in bands_by_year.items():
        # create playlist for year
        # print(year)
        playlist_id = create_playlist(client, year)
        for artist in bands_by_year[year]:
            songs = find_songs(client, artist)
            if len(songs) > 0:
                add_songs_to_playlist(client, playlist_id, songs)

        sleep(5) # to make sure we don't hit the rate limit