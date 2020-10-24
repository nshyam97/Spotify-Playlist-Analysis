import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas
from secrets import *
from datetime import datetime
import plotly.graph_objects as go

pandas.options.display.max_columns = 50
pandas.options.display.max_colwidth = 100
pandas.options.display.width=500

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI, scope='user-library-read'))
results = pandas.DataFrame(sp.current_user_playlists()['items'])[['id', 'name']]
ATM_id = results['id'][results['name'] == 'ATM']
items = pandas.DataFrame(sp.playlist_items(playlist_id=ATM_id.values[0],
                                           fields='items(added_at, track(album(artists(), images), name, id))')['items'])
added_at = list(items['added_at'])
track_name = []
artist_names = []
track_ids = []
album_images = []
for i in range(len(items['track'])):
    track_name.append(items['track'][i]['name'])
    track_ids.append(items['track'][i]['id'])
    grouped_artists = []
    album_images.append(items['track'][i]['album']['images'][1]['url'])
    for j in range(len(items['track'][i]['album']['artists'])):
        grouped_artists.append(items['track'][i]['album']['artists'][j]['name'])
    artist_names.append(grouped_artists)

music_dict = {'Added_At':added_at, 'Track_ID':track_ids, 'Track_Name':track_name, 'Artist_Names':artist_names, 'Album_Images':album_images}
music_df = pandas.DataFrame(music_dict)

track_features = pandas.DataFrame(sp.audio_features(list(music_df['Track_ID']))).drop(['uri', 'track_href', 'analysis_url', 'type'], axis=1)

total_df = music_df.merge(track_features, left_on='Track_ID', right_on='id', how='inner').drop(['id', 'time_signature'], axis=1)
total_df['Added_At'] = pandas.to_datetime(total_df['Added_At']).dt.tz_localize(None)
total_df['Days_In_Playlist'] = (datetime.now() - total_df['Added_At']).dt.days
total_df['Day_Of_Week_Added'] = total_df['Added_At'].dt.day_name()

total_df['duration_ms'] = total_df['duration_ms']/(1000*60)
total_df = total_df.rename({'duration_ms':'duration_mins'}, axis=1)
print(total_df)