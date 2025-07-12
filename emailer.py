import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime, timedelta, timezone
import smtplib
from email.message import EmailMessage

# Load environment variables
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
SMTPLIB_ID = os.getenv("SMTPLIB_ID")  # Gmail App Password

# Email setup
msg = EmailMessage()
msg['From'] = 'aarush.shivkumar@gmail.com'
msg['To'] = 'nottingham_reds@hotmail.com'

# Spotify Authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=["user-read-recently-played"],
    cache_path=os.path.join(os.getcwd(), ".cache")
))

# Time window: Last 2 hours
now = datetime.now(timezone.utc)
time_threshold = now - timedelta(hours=2)

# Fetch recently played tracks
results = sp.current_user_recently_played(limit=50)

track_uris = []
track_artists = []
track_time = []
track_name = []
email_txt = []

playlist_name = "mixtape/" + now.strftime("%Y-%m-%d")

for idx, item in enumerate(results['items']):
    played_at_str = item['played_at']
    try:
        played_at_time = datetime.strptime(played_at_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    except ValueError:
        played_at_time = datetime.strptime(played_at_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

    if played_at_time > time_threshold:
        track = item['track']
        track_uris.append(track['uri'])
        track_artists.append(track['artists'][0]['name'])
        track_time.append(played_at_str)
        track_name.append(track['name'])
        print(idx, track['artists'][0]['name'], " – ", track['name'])

# Compose email using your original logic and formatting
if track_uris:
    msg['Subject'] = "Update on " + playlist_name
    for i in range(len(track_uris)):
        temp = track_time[i] + " : " + track_artists[i] + " – " + track_name[i]
        email_txt.append(temp)
    email_content = '\n'.join(email_txt)
    msg.set_content(email_content)
else:
    msg['Subject'] = "No new songs in " + playlist_name
    msg.set_content("Check later")

# Send email
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login('aarush.shivkumar@gmail.com', SMTPLIB_ID)
    smtp.send_message(msg)