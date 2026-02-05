import yt_dlp
import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging

class VideoDownloader:
    """Download video từ các nền tảng Trung Quốc"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Custom extractors cho các nền tảng Trung Quốc
        self.platforms = {
            "bilibili.com": {
                "extractor": "BiliBili",
                "options": {
                    'format': 'bestvideo+bestaudio/best',
                    'merge_output_format': 'mp4',
                }
            },
            "v.qq.com": {
                "extractor": "Tencent",
                "options": {
                    'format': 'best',
                }
            },
            "youku.com": {
                "extractor": "Youku",
                "options": {
                    'format': 'best',
                }
            },
            "iqiyi.com": {
                "extractor": "Iqiyi",
                "options": {
                    'format': 'best',
                }
            },
            "douyin.com": {
                "extractor": "TikTok",
                "options": {
                    'format': 'best',
                }
            }
        }
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """Lấy thông tin video"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'formats': [f['format'] for f in info.get('formats', [])[:5]],
                    'ext': info.get('ext', 'Unknown'),
                    'thumbnail': info.get('thumbnail', ''),
                    'description': info.get('description', '')[:200]
                }
        except Exception as e:
            self.logger.error(f"Error getting video info: {str(e)}")
            raise
    
    def download(self, url: str, quality: str = 'best', output_format: str = 'mp4', 
                 output_path: str = None, subtitles: bool = True, 
                 audio_only: bool = False, **kwargs) -> str:
        """Tải video"""
        
        if output_path is None:
            output_path = str(Path.home() / "Downloads")
        
        # YDL options
        ydl_opts = {
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'progress_hooks': [kwargs.get('progress_callback', None)],
            'quiet': False,
            'no_warnings': True,
            'format': self._get_format_selector(quality, audio_only),
            'merge_output_format': output_format,
            'writesubtitles': subtitles,
            'writeautomaticsub': subtitles,
            'subtitleslangs': ['zh', 'en', 'vi'] if subtitles else [],
            'postprocessors': [
                {
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': output_format,
                }
            ] if not audio_only else [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }
            ],
            'logger': self._get_logger(kwargs.get('status_callback')),
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                # Get actual output file path
                if audio_only:
                    base, _ = os.path.splitext(filename)
                    output_file = f"{base}.mp3"
                else:
                    output_file = filename
                
                return output_file
                
        except Exception as e:
            self.logger.error(f"Download error: {str(e)}")
            raise
    
    def _get_format_selector(self, quality: str, audio_only: bool) -> str:
        """Get format selector based on quality"""
        if audio_only:
            return 'bestaudio/best'
        
        quality_map = {
            'best': 'bestvideo+bestaudio/best',
            '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            '480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
            '360p': 'bestvideo[height<=360]+bestaudio/best[height<=360]',
            'worst': 'worstvideo+worstaudio/worst',
        }
        
        return quality_map.get(quality, 'bestvideo+bestaudio/best')
    
    def _get_logger(self, callback):
        """Get custom logger for yt-dlp"""
        class CustomLogger:
            def debug(self, msg):
                if callback and "Downloading" in msg:
                    callback(msg)
            
            def info(self, msg):
                if callback:
                    callback(msg)
            
            def warning(self, msg):
                if callback:
                    callback(f"Warning: {msg}")
            
            def error(self, msg):
                if callback:
                    callback(f"Error: {msg}")
        
        return CustomLogger()
