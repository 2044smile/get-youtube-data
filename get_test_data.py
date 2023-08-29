import os
import argparse
import pandas as pd

from googleapiclient.discovery import build


class YouTube:
    def __init__(self):
        developer_key = os.getenv('YOUTUBE_DEVELOPER_KEY')
        youtube_api_service_name = 'youtube'
        youtube_api_version = 'v3'
        self.youtube = build(youtube_api_service_name, youtube_api_version, developerKey=developer_key)

    def youtuber(self, channel_id: str) -> list:
        playlist = self.youtube.playlists().list(
            channelId=channel_id,
            part='snippet',
            maxResults=20
        ).execute()

        return playlist['items']

    def make_csv(self, playlist: list, channel_name: str):
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


parser = argparse.ArgumentParser(description="유튜브 채널 이름을 입력해 주세요. EX) 곽튜브, 빠니보틀")
parser.add_argument('-c', '--channel')
args = parser.parse_args()

youtube = YouTube()
if args.channel == '빠니보틀':
    target = youtube.youtuber(channel_id='UCNhofiqfw5nl-NeDJkXtPvw')
    youtube.make_csv(target, channel_name='빠니보틀')
elif args.channel == '곽튜브':
    target = youtube.youtuber(channel_id='UClRNDVO8093rmRTtLe4GEPw')
    youtube.make_csv(target, channel_name='곽튜브')
else:
    print("유튜브 채널 이름을 입력해 주세요.")

