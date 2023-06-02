from dotenv import  load_dotenv
import os
import base64
from requests import post, get
import json
from flask import Flask, request, url_for, session, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

app = Flask(__name__)
app.secret_key = "yummyyummy"
app.config['SESSION_COOKIE_NAME'] = 'Session'
TOKEN_INFO = "token_info"

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=url_for('redirectPage', _external=True,),
        scope="user-library-read")

def getToken():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise "exception"
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if(is_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info

@app.route('/')
def login():
    sp_auth = create_spotify_oauth()
    auth_url = sp_auth.get_authorize_url()
    return redirect(auth_url)

@app.route('/getRecs')
def getRecs():
    try:
        token_info = getToken()
    except:
        print("User Not Logged in")
        redirect(url_for('login', _external=False))  
    sp = spotipy.Spotify(auth=token_info['access_token'])
    first_track = sp.current_user_saved_tracks(limit=50, offset=0)['items'][0]
    track_info = first_track['track']
    track_artist = track_info['artists'][0]['name']
    state = "{} by {}".format(track_info['name'], track_artist)
    return state

@app.route('/redirect')
def redirectPage():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('getRecs', _external=True))




if __name__ == "__main__":
  app.run()




# def get_token():
#     auth_string = client_id + ":" + client_secret
#     auth_bytes = auth_string.encode("utf-8")
#     auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
#     url = "https://accounts.spotify.com/api/token"
#     headers = {
#         "Authorization": "Basic " + auth_base64,
#         "Content-Type": "application/x-www-form-urlencoded",
#     }
#     data = {"grant_type": "client_credentials"}
#     result = post(url, headers=headers, data=data)
#     json_result = json.loads(result.content)
#     token = json_result["access_token"]
#     return token
#
# def get_auth_header(token):
#     return {"Authorization": "Bearer " + token}
#
# def search_artist(token, artist_name):
#     url = "https://api.spotify.com/v1/search"
#     headers = get_auth_header(token)
#     query = f"?q={artist_name}&type=artist&limit=1"
#
#     query_url = url + query
#     result = get(query_url, headers=headers)
#     json_result = json.loads(result.content)["artists"]["items"]
#     if len(json_result) == 0:
#         print("No artist exists with that name")
#         return None
#     return json_result[0]
#
# def get_tracks_by_artist(token, artist_id):
#     url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
#     headers = get_auth_header(token)
#     result = get(url, headers=headers)
#     json_result = json.loads(result.content)["tracks"]
#     return json_result
#
#
# token = get_token()
# result = search_artist(token, "Justin Bieber")
# artist_id = result["id"]
# tracks = get_tracks_by_artist(token, artist_id)

# for idx, song in enumerate(tracks):
#     print(f"{idx + 1}.{song['name']}")

# print(result)


