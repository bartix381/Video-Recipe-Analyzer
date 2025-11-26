"""Frame extraction from video files."""
import cv2
import logging
from pathlib import Path
from typing import List
from ..entities import Frame

logger = logging.getLogger(__name__)


class FrameExtractor:
    """Extract frames from video at specified FPS."""
    
    def __init__(self, fps: float = 1.0, output_dir: str = "outputs/frames", format: str = "jpg", quality: int = 95):
        """
        Initialize frame extractor.
        
        Args:
            fps: Frames per second to extract (default: 1.0)
            output_dir: Directory to save extracted frames
            format: Image format (jpg, png)
            quality: Image quality for JPEG (1-100)
        """
        self.fps = fps
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.format = format
        self.quality = quality
        logger.info(f"Initialized FrameExtractor: fps={fps}, format={format}")
    
    def extract(self, video_path: str) -> List[Frame]:
        """
        Extract frames from video.
        
        Args:
            video_path: Path to video file
            
        Returns:
            List of Frame entities
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        logger.info(f"Extracting frames from {video_path.name}")
        
        # Open video
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise RuntimeError(f"Failed to open video: {video_path}")
        
        # Get video properties
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / video_fps if video_fps > 0 else 0
        
        logger.info(f"Video: fps={video_fps:.2f}, frames={frame_count}, duration={duration:.2f}s")
        
        # Calculate frame interval
        frame_interval = int(video_fps / self.fps) if self.fps > 0 else 1
        
        frames = []
        frame_idx = 0
        extracted_count = 0
        
        # Create subdirectory for this video
        video_name = video_path.stem
        frame_dir = self.output_dir / video_name
        frame_dir.mkdir(exist_ok=True)
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Extract frame at specified interval
                if frame_idx % frame_interval == 0:
                    timestamp = frame_idx / video_fps
                    frame_filename = f"frame_{timestamp:.2f}s.{self.format}"
                    frame_path = frame_dir / frame_filename
                    
                    # Save frame
                    if self.format.lower() in ['jpg', 'jpeg']:
                        cv2.imwrite(
                            str(frame_path), 
                            frame,
                            [cv2.IMWRITE_JPEG_QUALITY, self.quality]
                        )
                    else:
                        cv2.imwrite(str(frame_path), frame)
                    
                    frames.append(Frame(
                        timestamp=timestamp,
                        image_path=str(frame_path),
                    ))
                    extracted_count += 1
                
                frame_idx += 1
        
        finally:
            cap.release()
        
        logger.info(f"Extracted {extracted_count} frames at {self.fps} fps")
        return frames
