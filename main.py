import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas
from secrets import *

pandas.options.display.max_columns = 50
pandas.options.display.width=500

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI, scope='user-library-read'))
results = pandas.DataFrame(sp.current_user_playlists()['items'])[['id', 'name']]
ATM_id = results['id'][results['name'] == 'ATM']
items = pandas.DataFrame(sp.playlist_items(playlist_id=ATM_id.values[0],
                                           fields='items(added_at, track(album(artists()), name, id))')['items'])
added_at = list(items['added_at'])
track_name = []
artist_names = []
track_ids = []
for i in range(len(items['track'])):
    track_name.append(items['track'][i]['name'])
    track_ids.append(items['track'][i]['id'])
    grouped_artists = []
    for j in range(len(items['track'][i]['album']['artists'])):
        grouped_artists.append(items['track'][i]['album']['artists'][j]['name'])
    artist_names.append(grouped_artists)

music_dict = {'Added_At':added_at, 'Track_ID':track_ids, 'Track_Name':track_name, 'Artist_Names':artist_names}
music_df = pandas.DataFrame(music_dict)