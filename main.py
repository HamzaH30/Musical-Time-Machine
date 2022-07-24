# Name: Hamza H.
# Date Last Modified: July 24, 2022

from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

# CONSTANTS
SPOTIPY_CLIENT_ID = os.environ["SPOTIPY_CLIENT_ID"]
SPOTIPY_CLIENT_SECRET = os.environ["SPOTIPY_CLIENT_SECRET"]
SPOTIPY_REDIRECT_URI = os.environ["SPOTIPY_REDIRECT_URI"]

# Input prompt asking the user for what year they would like to travel to
travel_date = input(
    "Which year do you want to musically time travel back to? Type the date in this format YYYY-MM-DD: ")

# Sending request to Billboard Charts website
response = requests.get("https://www.billboard.com/charts/hot-100/" + travel_date)

# Creating a BeautifulSoup object
soup = BeautifulSoup(response.text, "html.parser")

# Scraping the top 100 songs and storing it in a list
song_tags = soup.select(selector="li h3", class_="c-title", id="title-of-a-story")
song_titles = [song.getText().strip() for song in song_tags[:100]]

# Scraping the artists and storing it in a list
artist_tags = soup.select(selector="ul li ul li span", class_="c-label")
artists = [artist.getText().strip() for artist in artist_tags[::7]]

# Using Spotipy to connect to Spotify

# The scope is required by Spotify - outlines the permissions the user will have to enable for the program to run.
# https://developer.spotify.com/documentation/general/guides/authorization/scopes/#playlist-modify-private
scope = "playlist-modify-private"

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        scope=scope,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        show_dialog=True,
        cache_path="token.txt"
    )
)

# Getting the spotify user's ID
spotify_user_id = sp.current_user()["id"]

# Creating a list of all the Spotify Song URIs
song_uris = []
for song in song_titles:
    try:
        search_results = sp.search(q=f"track: {song} artist: {artists[song_titles.index(song)]}", type="track")
        song_uris.append(search_results["tracks"]["items"][0]["uri"])
    except:
        print(f"This song: \"{song}\" has no Spotify URI")

# Creating a Playlist
playlist_name = f"{travel_date} Top 100 Songs"
playlist = sp.user_playlist_create(
    user=spotify_user_id,
    name=playlist_name,
    public=False,
    description=f"A playlist of the top 100 songs on {travel_date} according to Billboard."
)
playlist_id = playlist["id"]

# Adding the songs to the playlist
sp.playlist_add_items(playlist_id=playlist_id, items=song_uris)
