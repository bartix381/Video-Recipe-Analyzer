"""Audio extraction from video files."""
import ffmpeg
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class AudioExtractor:
    """Extract audio track from video files."""
    
    def __init__(self, output_dir: str = "outputs/audio", format: str = "wav"):
        """
        Initialize audio extractor.
        
        Args:
            output_dir: Directory to save extracted audio
            format: Audio format (wav, mp3, m4a)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.format = format
        logger.info(f"Initialized AudioExtractor: format={format}")
    
    def extract(self, video_path: str) -> str:
        """
        Extract audio from video.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Path to extracted audio file
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        logger.info(f"Extracting audio from {video_path.name}")
        
        # Output path
        audio_filename = f"{video_path.stem}.{self.format}"
        audio_path = self.output_dir / audio_filename
        
        try:
            # Extract audio using ffmpeg
            stream = ffmpeg.input(str(video_path))
            
            if self.format == "wav":
                # Extract as WAV with specific parameters for Whisper
                stream = ffmpeg.output(
                    stream,
                    str(audio_path),
                    acodec='pcm_s16le',  # 16-bit PCM
                    ac=1,  # Mono
                    ar='16000'  # 16kHz sample rate (Whisper preference)
                )
            else:
                stream = ffmpeg.output(stream, str(audio_path))
            
            # Run ffmpeg
            ffmpeg.run(stream, quiet=True, overwrite_output=True)
            
            logger.info(f"Extracted audio to {audio_path}")
            return str(audio_path)
        
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}")
            raise RuntimeError(f"Failed to extract audio: {str(e)}")
