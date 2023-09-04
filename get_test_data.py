import os
import argparse
import pandas as pd

from googleapiclient.discovery import build


def make_playlist_csv(playlist: list, channel_name: str):
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
    df.to_csv(f"/Users/cslee/vscode/get-youtube-data/csv/{channel_name}_재생목록.csv")


def make_videos_csv(stats_list: list, channel_name: str, playlist_title: str):
    df = pd.DataFrame(stats_list)
    df.to_csv(f"/Users/cslee/vscode/get-youtube-data/csv/{channel_name}_{playlist_title}_영상들.csv")


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

        유튜버가 가지고 있는 재생 목록의 플레이 리스트를 제공합니다.
        """
        playlist = self.youtube.playlists().list(
            channelId=channel_id,
            part='snippet',
            maxResults=20
        ).execute()

        return playlist['items']

    def get_videos_from_playlists_items(self, playlist_id: str) -> list:
        """
        :param playlist_id:
        :return: video_list

        유튜버가 가지고 있는 재생 목록에서 보고 싶은 플레이 리스트를 선택하면 플레이 리스트 안에 있는 데이터(video_id)를 return.
        """
        video_list = []
        next_page = True

        playlist_items = self.youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults=50
        )

        while next_page:
            response = playlist_items.execute()
            data = response['items']

            for video in data:
                video_id = video['contentDetails']['videoId']
                # * video_id 를 중복없이 video_list 에 삽입한다.
                if video_id not in video_list:
                    video_list.append(video_id)

                # Do we have more pages?
            if 'nextPageToken' in response.keys():  # 다음 페이지가 있다면 'nextPageToken' = True 없다면 'nextPageToken' 삭제
                next_page = True
                playlist_items = self.youtube.playlistItems().list(
                    part="snippet,contentDetails",
                    playlistId=playlist_id,
                    pageToken=response['nextPageToken'],  # * google-api-python-client 에서 지원하는 nextPageToken
                    maxResults=50
                )
            else:
                next_page = False  # * 'nextPageToken' in response.keys() 가 없다면 End

        return video_list

    def get_my_selected_youtube_playlists(self, playlist_id: str):
        """
        :param playlist_id:
        :return: playlist_items

        플레이 리스트 안에 있는 유튜브 영상의 상세 정보 데이터를 return.
        """
        stats_list = []
        stats_dict = {}

        video_list = self.get_videos_from_playlists_items(playlist_id=playlist_id)
        for i in range(0, len(video_list), 50):
            response = self.youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_list[i:i+50]
            ).execute()

            for video in response['items']:
                url_pk = video['id']
                channel_id = video['snippet']['channelId']
                title = video['snippet']['title']
                description = video['snippet']['description']
                thumbnails = video['snippet']['thumbnails']['high']['url']
                view_count = video['statistics'].get('viewCount', 0)
                like_count = video['statistics'].get('likeCount', 0)
                published = video['snippet']['publishedAt']
                play_time = video['contentDetails']['duration']

                stats_dict = dict(
                    url_pk=url_pk, channel_id=channel_id, title=title, description=description, thumbnails=thumbnails,
                    view_count=view_count, like_count=like_count, published=published, play_time=play_time
                )
                stats_list.append(stats_dict)

        return stats_list, video['snippet']['channelTitle']


parser = argparse.ArgumentParser(description="유튜브 채널 이름을 입력해 주세요. EX) 곽튜브, 빠니보틀")
parser.add_argument('-c', '--channel')
parser.add_argument('-n', '--number')
args = parser.parse_args()

youtube = YouTube()
if args.channel == '빠니보틀':
    target = youtube.get_all_youtube_playlists(channel_id='UCNhofiqfw5nl-NeDJkXtPvw')
    make_playlist_csv(target, channel_name='빠니보틀')
    if args.number:
        youtube_video_list, channel_title = youtube.get_my_selected_youtube_playlists(
            playlist_id=target[int(args.number)]['id'])
        make_videos_csv(youtube_video_list, channel_title, target[int(args.number)]['snippet']['title'])
elif args.channel == '곽튜브':
    target = youtube.get_all_youtube_playlists(channel_id='UClRNDVO8093rmRTtLe4GEPw')
    make_playlist_csv(target, channel_name='곽튜브')
    if args.number:
        youtube_video_list, channel_title = youtube.get_my_selected_youtube_playlists(
            playlist_id=target[int(args.number)]['id'])
        make_videos_csv(youtube_video_list, channel_title, target[int(args.number)]['snippet']['title'])
else:
    print("유튜브 채널 이름을 입력해 주세요.")
