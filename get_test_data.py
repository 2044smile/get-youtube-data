import os
from googleapiclient.discovery import build


class YouTube:
    def __init__(self):
        developer_key = os.getenv('YOUTUBE_DEVELOPER_KEY')
        youtube_api_service_name = 'youtube'
        youtube_api_version = 'v3'
        self.youtube = build(youtube_api_service_name, youtube_api_version, developerKey=developer_key)

    def play(self):
        print(self.youtube)


youtube = YouTube()
youtube.play()
