import os
import yt_dlp
from config import Config

class Downloader:
    @staticmethod
    def download_url(url):
        """
        Downloads audio from a video URL using yt-dlp.
        Returns the path to the downloaded audio file.
        """
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(Config.UPLOAD_FOLDER, '%(id)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = f"{info['id']}.mp3"
                filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
                return filepath, info.get('title', 'Unknown Title')
        except Exception as e:
            print(f"Error downloading URL: {e}")
            return None, None
