import youtube_dl
from enum import Enum
import requests
from typing import List, Tuple


class DownloadStatus(Enum):
    SUCCESS = 1
    FAILURE = 2


class YoutubeDownloader:

    ydl_opts = {
        'format': 'bestaudio/best',
        # 'outtmpl': 'music/%(title)s' + '.mp3',  # path for downloaded music
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': True,
        'quiet': True
    }

    def __init__(self, dl_dir: str):
        self.ydl_opts = YoutubeDownloader.ydl_opts
        self.ydl_opts['outtmpl'] = f'{dl_dir}/%(title)s.mp3'
        print(f'directory set to {dl_dir}/')
        self.ydl = youtube_dl.YoutubeDL(self.ydl_opts)
        print('YoutubeDL initialized')

    def search(self, search_args: str, num_results: int = 5) -> List[Tuple[str, str]]:
        print(type(search_args))
        search_res = None
        is_link = False
        try:
            requests.get(search_args)
            is_link = True
        except Exception as e:
            print(f'EXCEPTION: {e}')

        if is_link:
            try:
                search_res = self.ydl.extract_info(search_args, download=False)
            except youtube_dl.DownloadError:
                print('DOWNLOAD ERROR - invalid link')
        else:
            try:
                search_res = self.ydl.extract_info(f'ytsearch{num_results}:{search_args}', download=False)
            except youtube_dl.DownloadError:
                print('DOWNLOAD ERROR - invalid search')

        if 'entries' in search_res:
            search_res = [(result['title'], result['webpage_url']) for result in search_res['entries']]
        else:
            search_res = [(search_res['title'], search_res['webpage_url'])]

        return search_res


'''
def download_video_as_mp3(yt_link):
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            audio_info = ydl.extract_info(url=yt_link)
            file_name = audio_info['title'] + '.mp3'
            return DownloadStatus.SUCCESS, file_name
        except youtube_dl.DownloadError:
            return DownloadStatus.FAILURE, ''
'''

if __name__ == '__main__':

    args = [
        'TRUE Storyteller',
        'https://www.youtube.com/watch?v=5rz1TcLVFzY',
        'Babymetal - doki doki morning',
        'aaljfbaoufbnaifnaoifbnaoufibaoufbalofuiaobf'
    ]

    ytdlr = YoutubeDownloader('music')

    for arg in args:
        res = ytdlr.search(arg, num_results=5)
        print(len(res))
        for x in res:
            print(f'  {x}')
