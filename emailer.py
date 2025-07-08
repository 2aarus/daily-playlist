import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime, time, date, timedelta
import requests
from io import BytesIO
from PIL import Image
import base64
import smtplib
from email.message import EmailMessage

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
SMTPLIB_ID = os.getenv("SMTPLIB_ID")

print("1")
CACHE_PATH = os.path.join(os.getcwd(), ".cache")
msg = EmailMessage()
msg['From'] = 'aarush.shivkumar@gmail.com'
msg['To'] = 'nottingham_reds@hotmail.com'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=["user-read-recently-played" ,"playlist-modify-public", "user-read-private", "ugc-image-upload"],
    cache_path=CACHE_PATH
))

current_time = datetime.combine(datetime.now(), time.min)
with open('time.txt', 'r') as file:
    createtime = file.read().rstrip()
print(current_time)

token_info = sp.auth_manager.get_cached_token()
if not token_info:
    print("❌ ERROR: No access token retrieved!")
    token_info = sp.auth_manager.get_access_token(as_dict=True)
else:
    print("✅ Token retrieved successfully.")
results = sp.current_user_recently_played(limit=50)
print("3")
track_uris = []
track_artists = []
track_time = []
track_name = []
email_txt = []
playlist_name = "mixtape/"+ str(date(day=datetime.now().day ,month=datetime.now().month ,year=datetime.now().year))
for idx, item in enumerate(results['items']):
    played_at_str = item['played_at']
    try:
        played_at_time = datetime.strptime(played_at_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        played_at_time = datetime.strptime(played_at_str, "%Y-%m-%dT%H:%M:%SZ")
    if played_at_time > current_time:
        if idx == 0:
            createtime = item['played_at']
        track = item['track']
        track_uris.append(track['uri'])
        track_artists.append(track['artists'][0]['name'])
        track_time.append(played_at_str)
        track_name.append(track['name'])
        print(idx, track['artists'][0]['name'], " – ", track['name'])
with open('time.txt', 'w') as file:
    file.seek(0)
    file.truncate()
    file.write(str(createtime))
if track_uris:
    msg['Subject'] = "Update on " + playlist_name
    for i in range(len(track_uris)):
        temp = played_at_str + " : " + track_artists[i] + " – ", track_name[i]
        email_txt.append(temp)
    email_content = '\n'.join(email_txt)
    msg.set_content(email_content)
else:
    msg['Subject'] = "No new songs in " + playlist_name
    msg.set_content("Check later")

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login('aarush.shivkumar@gmail.com', SMTPLIB_ID)
    smtp.send_message(msg)
