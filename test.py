import requests
import json
import os


import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

import youtube_dl

from exceptions import ResponseException

class CreatePlaylist:

    def __init__(self):
        self.spotify_token = "XXXXX"
        self.spotify_user_id = "XXXXX"
        self.all_song_info = {}
        self.youtube_client = self.get_yt_client()


    def get_yt_client(self):
        api_service_name = "youtube"
        version = "v3"
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        client_secrets_file = 'client_secret.json'

        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)

        credentials = flow.run_console()

        youtube_client = googleapiclient.discovery.build(
            api_service_name, version, credentials=credentials)

        return youtube_client


        

    def get_liked_videos(self):
        request = self.youtube_client.playlists().list(
            part="snippet,contentDetails",
            maxResults=25,
            mine=True
        )
        playlist_id = None
        response = request.execute()
        for item in response["items"]:
            if item["snippet"]["title"] == "Convert to Spotify":
                playlist_id = item["id"]

        if(playlist_id == None):
            return
        return playlist_id


    def get_playlist_vids(self):
        playlist_id = self.get_liked_videos()
        request = self.youtube_client.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id
        )

        response = request.execute()
        for item in response["items"]:
            vid_title = item["snippet"]["title"]
            url = "http://www.youtube.com/watch?v={}".format(item["contentDetails"]["videoId"])
            video = youtube_dl.YoutubeDL({}).extract_info(url, download=False)

            song_name = video["track"]
            artist = video["artist"]
            print(song_name)
            print(artist)
            if song_name is not None and artist is not None:
                self.all_song_info["video_title"] = {
                    "youtube_url":url,
                    "song_name":song_name,
                    "artist":artist,

                    "spotify_uri":self.get_spotify_uri(song_name,artist)
                }


    def find_playlist(self):
        
        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.spotify_user_id)

        response = requests.get(
            query,
            headers={
                "Content-Type" : "application/json",
                "Authorization" : "Bearer {}".format(self.spotify_token)
            }
        )

        response_json = response.json()["items"]

        for item in response_json:
            if(item["name"] == "YouTube Playlist"):
                return item["id"]

        return None


    def get_spotify_uri(self, song_name, artist):
        query = "https://api.spotify.com/v1/search?q=track%3A{}+artist%3A{}&type=track&offset=0&limit=20".format(
            song_name,
            artist
        )

        response = requests.get(
            query,
            headers={
                "Content-Type" : "application/json",
                "Authorization" : "Bearer {}".format(self.spotify_token)
            }
        )

        response_json = response.json()
        songs = response_json["tracks"]["items"]
        uri = songs[0]["uri"]

        return uri


    def add_song_to_playlist(self,playlist_id):

        self.get_liked_videos()


        uris = [info["spotify_uri"] for song ,info in self.all_song_info.items()]

        request_data = json.dumps(uris)

        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlist_id)


        response = requests.post(

            query,
            data=request_data,
            headers={
                "Content-Type" : "application/json",
                "Authorization" : "Bearer {}".format(self.spotify_token)
            }

        )


cp = CreatePlaylist()
cp.add_song_to_playlist()