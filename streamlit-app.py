import streamlit as st
import credentials as se
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas
from datetime import datetime


def authorise():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=se.CLIENT_ID, client_secret=se.CLIENT_SECRET,
                                                   redirect_uri=se.REDIRECT_URI, scope='user-library-read'))
    return sp


def populate_lists(sp):
    results = pandas.DataFrame(sp.current_user_playlists()['items'])[['id', 'name']]
    ATM_id = results['id'][results['name'] == 'ATM']
    items = pandas.DataFrame(sp.playlist_items(playlist_id=ATM_id.values[0],
                                               fields='items(added_at, track(album(artists(), images), name, id))')[
                                 'items'])
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

    music_dict = {'Added_At': added_at, 'Track_ID': track_ids, 'Track_Name': track_name, 'Artist_Names': artist_names,
                  'Album_Images': album_images}
    music_df = pandas.DataFrame(music_dict)

    return music_df


def finalise_dfs(music_df, sp):
    track_features = pandas.DataFrame(sp.audio_features(list(music_df['Track_ID']))).drop(
        ['uri', 'track_href', 'analysis_url', 'type'], axis=1)

    total_df = music_df.merge(track_features, left_on='Track_ID', right_on='id', how='inner').drop(
        ['id', 'time_signature'], axis=1)
    total_df['Added_At'] = pandas.to_datetime(total_df['Added_At']).dt.tz_localize(None)
    total_df['Days_In_Playlist'] = (datetime.now() - total_df['Added_At']).dt.days
    total_df['Day_Of_Week_Added'] = total_df['Added_At'].dt.day_name()

    total_df['duration_ms'] = total_df['duration_ms'] / (1000 * 60)
    total_df = total_df.rename({'duration_ms': 'duration_mins'}, axis=1)

    return total_df


def run_all():
    sp = authorise()
    music_df = populate_lists(sp)
    total_df = finalise_dfs(music_df, sp)

    return total_df


total_df = run_all()

st.markdown(
        f"""
<style>
    .reportview-container .main .block-container{{
        max-width: 1500px;
</style>
""",
        unsafe_allow_html=True,
    )
for i in range(len(total_df)):
    cols = st.beta_columns(2)
    cols[0].markdown(f'![Test] ({total_df.Album_Images[i]})')
    cols[1].header(total_df.Track_Name[i] + ' - ' + ', '.join(total_df.Artist_Names[i]))
    my_expander = cols[1].beta_expander("Song details", expanded=False)
    with my_expander:
        st.write('Song duration - ' + str(round(total_df.duration_mins[i], 2)) + ' mins')
        st.write('Danceability - ' + str(round(total_df.danceability[i], 2)))
        st.write('Energy - ' + str(round(total_df.energy[i], 2)))
        st.write('Key - ' + str(round(total_df.key[i], 2)))
        st.write('Loudness - ' + str(round(total_df.loudness[i], 2)))
        st.write('Mode - ' + str(total_df['mode'][i]))
        st.write('Speechiness - ' + str(round(total_df.speechiness[i], 2)))
        st.write('Acousticness - ' + str(round(total_df.acousticness[i], 2)))
        st.write('Instrumentalness - ' + str(round(total_df.instrumentalness[i], 2)))
        st.write('Liveness - ' + str(round(total_df.liveness[i], 2)))
        st.write('Valence - ' + str(round(total_df.valence[i], 2)))
        st.write('Tempo - ' + str(round(total_df.tempo[i], 2)))