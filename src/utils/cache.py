"""Video cache management with TTL."""
import os
import time
import logging
import hashlib
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class VideoCache:
    """Video cache manager with 24-hour TTL."""
    
    def __init__(self, cache_dir: str, ttl_hours: int = 24):
        """
        Initialize video cache.
        
        Args:
            cache_dir: Directory for cached videos
            ttl_hours: Time-to-live in hours (default: 24)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_hours * 3600
        logger.info(f"Initialized video cache at {self.cache_dir} with TTL={ttl_hours}h")
    
    def _get_cache_key(self, url: str) -> str:
        """Generate cache key from URL."""
        return hashlib.md5(url.encode()).hexdigest()
    
    def _get_cache_path(self, url: str, extension: str = ".mp4") -> Path:
        """Get cache file path for URL."""
        cache_key = self._get_cache_key(url)
        return self.cache_dir / f"{cache_key}{extension}"
    
    def _get_metadata_path(self, url: str) -> Path:
        """Get metadata file path for URL."""
        cache_key = self._get_cache_key(url)
        return self.cache_dir / f"{cache_key}.meta"
    
    def get(self, url: str) -> Optional[str]:
        """
        Get cached video path if exists and not expired.
        
        Args:
            url: Video URL
            
        Returns:
            Path to cached video if valid, None otherwise
        """
        # Try common video extensions
        for ext in [".mp4", ".webm", ".mkv", ".mov"]:
            cache_path = self._get_cache_path(url, ext)
            if cache_path.exists():
                # Check if expired
                age = time.time() - cache_path.stat().st_mtime
                if age < self.ttl_seconds:
                    logger.info(f"Cache hit for {url} (age: {age/3600:.1f}h)")
                    return str(cache_path)
                else:
                    logger.info(f"Cache expired for {url} (age: {age/3600:.1f}h)")
                    self._remove(cache_path)
        
        logger.info(f"Cache miss for {url}")
        return None
    
    def put(self, url: str, video_path: str) -> str:
        """
        Add video to cache.
        
        Args:
            url: Video URL
            video_path: Path to video file
            
        Returns:
            Path to cached video
        """
        ext = Path(video_path).suffix or ".mp4"
        cache_path = self._get_cache_path(url, ext)
        
        # Copy or move video to cache
        if Path(video_path).resolve() != cache_path.resolve():
            shutil.copy2(video_path, cache_path)
            logger.info(f"Cached video: {cache_path}")
        
        # Save metadata
        meta_path = self._get_metadata_path(url)
        with open(meta_path, 'w') as f:
            f.write(f"url={url}\n")
            f.write(f"cached_at={datetime.now().isoformat()}\n")
            f.write(f"original_path={video_path}\n")
        
        return str(cache_path)
    
    def _remove(self, path: Path):
        """Remove cached file and its metadata."""
        try:
            path.unlink()
            logger.debug(f"Removed: {path}")
        except Exception as e:
            logger.warning(f"Failed to remove {path}: {e}")
        
        # Remove metadata
        meta_path = path.with_suffix('.meta')
        if meta_path.exists():
            try:
                meta_path.unlink()
            except Exception as e:
                logger.warning(f"Failed to remove metadata {meta_path}: {e}")
    
    def cleanup(self):
        """Remove expired cached videos."""
        removed_count = 0
        total_size = 0
        
        for file_path in self.cache_dir.glob("*"):
            if file_path.suffix == ".meta":
                continue  # Skip metadata files
            
            age = time.time() - file_path.stat().st_mtime
            if age >= self.ttl_seconds:
                size = file_path.stat().st_size
                self._remove(file_path)
                removed_count += 1
                total_size += size
        
        if removed_count > 0:
            logger.info(
                f"Cleaned up {removed_count} expired videos "
                f"({total_size / 1024 / 1024:.1f} MB)"
            )
        else:
            logger.info("No expired videos to clean up")
        
        return removed_count
    
    def clear(self):
        """Clear all cached videos."""
        removed_count = 0
        for file_path in self.cache_dir.glob("*"):
            self._remove(file_path)
            removed_count += 1
        
        logger.info(f"Cleared cache: removed {removed_count} files")
        return removed_count
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        files = list(self.cache_dir.glob("*"))
        video_files = [f for f in files if f.suffix != ".meta"]
        
        total_size = sum(f.stat().st_size for f in video_files)
        
        return {
            "cache_dir": str(self.cache_dir),
            "file_count": len(video_files),
            "total_size_mb": total_size / 1024 / 1024,
            "ttl_hours": self.ttl_seconds / 3600,
        }
