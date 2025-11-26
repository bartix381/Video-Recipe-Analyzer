"""Base downloader interface for video sources."""
import logging
from abc import ABC, abstractmethod
from typing import Optional
from ..entities import Video

logger = logging.getLogger(__name__)


class DownloadError(Exception):
    """Custom exception for download failures."""
    pass


class BaseDownloader(ABC):
    """Abstract base class for video downloaders."""
    
    def __init__(self, cache_dir: str, max_duration: int = 1800):
        """
        Initialize downloader.
        
        Args:
            cache_dir: Directory for downloaded videos
            max_duration: Maximum video duration in seconds (default: 1800 = 30 min)
        """
        self.cache_dir = cache_dir
        self.max_duration = max_duration
        logger.info(f"Initialized {self.__class__.__name__} with max_duration={max_duration}s")
    
    @abstractmethod
    def download(self, url: str) -> Video:
        """
        Download video from URL.
        
        Args:
            url: Video URL
            
        Returns:
            Video entity with local_path set
            
        Raises:
            DownloadError: If download fails
        """
        pass
    
    @abstractmethod
    def get_metadata(self, url: str) -> dict:
        """
        Get video metadata without downloading.
        
        Args:
            url: Video URL
            
        Returns:
            Dictionary with metadata (title, duration, etc.)
            
        Raises:
            DownloadError: If metadata retrieval fails
        """
        pass
    
    def _validate_duration(self, duration: float, url: str):
        """
        Validate video duration against maximum.
        
        Args:
            duration: Video duration in seconds
            url: Video URL for error message
            
        Raises:
            DownloadError: If duration exceeds maximum
        """
        if duration > self.max_duration:
            raise DownloadError(
                f"Video duration ({duration:.0f}s) exceeds maximum allowed "
                f"({self.max_duration}s = {self.max_duration/60:.0f} minutes). "
                f"Please use a shorter video. URL: {url}"
            )
