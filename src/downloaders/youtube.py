"""YouTube video downloader using yt-dlp."""
import yt_dlp
import logging
from pathlib import Path
from .base import BaseDownloader, DownloadError
from ..entities import Video

logger = logging.getLogger(__name__)


class YouTubeDownloader(BaseDownloader):
    """YouTube video downloader."""
    
    def __init__(self, cache_dir: str, max_duration: int = 1800, timeout: int = 300):
        """
        Initialize YouTube downloader.
        
        Args:
            cache_dir: Directory for downloaded videos
            max_duration: Maximum video duration in seconds
            timeout: Download timeout in seconds
        """
        super().__init__(cache_dir, max_duration)
        self.timeout = timeout
        self.ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': str(Path(cache_dir) / '%(id)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': timeout,
        }
    
    def get_metadata(self, url: str) -> dict:
        """Get video metadata without downloading."""
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'id': info.get('id'),
                    'description': info.get('description'),
                    'uploader': info.get('uploader'),
                }
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            if 'Private video' in error_msg:
                raise DownloadError(
                    f"Video is private. Please use a publicly accessible video URL. "
                    f"URL: {url}"
                )
            elif 'Video unavailable' in error_msg:
                raise DownloadError(
                    f"Video is unavailable or has been removed. URL: {url}"
                )
            elif 'Sign in to confirm your age' in error_msg or 'age' in error_msg.lower():
                raise DownloadError(
                    f"Video requires age verification. Please use a different video. "
                    f"URL: {url}"
                )
            else:
                raise DownloadError(
                    f"Failed to get video metadata: {error_msg}. "
                    f"URL: {url}. Try checking the URL or your internet connection."
                )
        except Exception as e:
            raise DownloadError(
                f"Unexpected error getting video metadata: {str(e)}. URL: {url}"
            )
    
    def download(self, url: str) -> Video:
        """Download video from YouTube."""
        try:
            # Get metadata first to check duration
            logger.info(f"Getting metadata for {url}")
            metadata = self.get_metadata(url)
            duration = metadata.get('duration')
            
            if duration:
                self._validate_duration(duration, url)
            else:
                logger.warning("Duration not available in metadata")
            
            # Download video
            logger.info(f"Downloading video: {metadata.get('title', 'Unknown')}")
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_id = info['id']
                ext = info.get('ext', 'mp4')
                local_path = Path(self.cache_dir) / f"{video_id}.{ext}"
                
                if not local_path.exists():
                    raise DownloadError(f"Download completed but file not found: {local_path}")
                
                logger.info(f"Downloaded to {local_path}")
                
                return Video(
                    url=url,
                    platform="youtube",
                    title=metadata.get('title'),
                    description=metadata.get('description'),
                    duration=duration,
                    local_path=str(local_path),
                )
        
        except DownloadError:
            raise
        except Exception as e:
            raise DownloadError(
                f"Failed to download video: {str(e)}. URL: {url}. "
                f"Suggestions: 1) Check internet connection, 2) Verify URL is correct, "
                f"3) Try again later if the issue persists."
            )
