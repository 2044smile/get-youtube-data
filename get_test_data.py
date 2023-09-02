import os
import argparse
import pandas as pd

from googleapiclient.discovery import build


def make_csv(playlist: list, channel_name: str):
    lst_title = []
    lst_thumbnails = []

    for pl in playlist:
        lst_title.append(pl['snippet']['title'])
        lst_thumbnails.append(pl['snippet']['thumbnails']['default']['url'])

    df = pd.DataFrame(
        {
            "title": lst_title,
            "thumbnails": lst_thumbnails
        }
    )
    df.to_csv(f"/Users/cslee/vscode/get-youtube-data/csv/{channel_name}.csv")


class YouTube:
    def __init__(self):
        developer_key = os.getenv('YOUTUBE_DEVELOPER_KEY')
        youtube_api_service_name = 'youtube'
        youtube_api_version = 'v3'
        self.youtube = build(youtube_api_service_name, youtube_api_version, developerKey=developer_key)

    def get_all_youtube_playlists(self, channel_id: str) -> list:
        """
        :param channel_id:
        :return: googleapiclient playlist['items']

        유튜버가 가지고 있는 재생목록의 플레이 리스트를 제공합니다.
        """
        playlist = self.youtube.playlists().list(
            channelId=channel_id,
            part='snippet',
            maxResults=20
        ).execute()

        return playlist['items']

    def get_my_selected_youtube_playlists(self, playlist_id: str):
        playlist_items = self.youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults=50
        ).execute()

        return playlist_items


parser = argparse.ArgumentParser(description="유튜브 채널 이름을 입력해 주세요. EX) 곽튜브, 빠니보틀")
parser.add_argument('-c', '--channel')
parser.add_argument('-n', '--number')
args = parser.parse_args()

youtube = YouTube()
if args.channel == '빠니보틀':
    target = youtube.get_all_youtube_playlists(channel_id='UCNhofiqfw5nl-NeDJkXtPvw')
    make_csv(target, channel_name='빠니보틀')
    if args.number:
        youtube.get_my_selected_youtube_playlists(
            playlist_id=target[int(args.number)]['id']
        )
elif args.channel == '곽튜브':
    target = youtube.get_all_youtube_playlists(channel_id='UClRNDVO8093rmRTtLe4GEPw')
    make_csv(target, channel_name='곽튜브')
    if args.number:
        youtube.get_my_selected_youtube_playlists(
            playlist_id=target[int(args.number)]['id']
        )
else:
    print("유튜브 채널 이름을 입력해 주세요.")

