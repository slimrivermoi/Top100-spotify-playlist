import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
from pprint import pprint
from dotenv import load_dotenv
import os
dotenv = load_dotenv(
    dotenv_path=".env",
    verbose=True)


BILLBOARD_URL= "https://www.billboard.com/charts/hot-100/"

#### create top 100 music based on date input #####
request_date = input("Which year you want to travel to? (YYYY-MM-DD)")
# request_date = "1982-01-08"  #for testing
response = requests.get(f"{BILLBOARD_URL}{request_date}")
billboard_webpage = response.text
soup = BeautifulSoup(billboard_webpage,"html.parser")
songs = soup.select("li ul li h3")
songs_list = [song.getText().strip() for song in songs]
# print(songs_list)


###### To set up spotify authorization token ######
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI="http://example.com"
scope="playlist-modify-public"
SPOTITY_API_ENDPOINT = "https://api.spotify.com/v1"


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                                               client_secret=SPOTIFY_CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=scope,
                                               show_dialog=True,
                                               cache_path="token.txt",
                                               )
                     )

## obtain the user id
user_id = sp.current_user()['id']


### retrieve the token from token.txt
with open("token.txt") as file:
    data = file.read()
js = json.loads(data)
spotify_token = js["access_token"]

search_endpoint = "https://api.spotify.com/v1/search"
headers = {
    "Authorization": "Bearer "+spotify_token
}



### loop through songs_list to create a list for all songs_uri
songs_uri =[]
year = request_date.split("-")[0]

for song in songs_list:
    result = sp.search(q=f"track:{song} year:{year}",type="track")
    print(result)
    try:
      uri = result["tracks"]["items"][0]["uri"]
      songs_uri.append(uri)

    except IndexError:
        print(f"{song} does not exist. Skipped.")


playlist = sp.user_playlist_create(user=user_id,
                                   name=f"Top100 for {request_date}",
                                   public=True,
                                   description="Love u much! ")
playlist_id = playlist['id']

add_tracks = sp.playlist_add_items(playlist_id=playlist_id, items=songs_uri)
print(add_tracks)
