"""Whisper-based speech-to-text transcriber."""
import whisper
import torch
import logging
from pathlib import Path
from ..entities import Transcript, TranscriptSegment

logger = logging.getLogger(__name__)


class Transcriber:
    """Whisper-based audio transcription."""
    
    def __init__(
        self,
        model_name: str = "base",
        language: str = None,
        device: str = "auto",
        fp16: bool = True,
        condition_on_previous_text: bool = True
    ):
        """
        Initialize transcriber.
        
        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
            language: Language code (None for auto-detection)
            device: Device to use (auto, cpu, cuda, mps)
            fp16: Use FP16 inference
            condition_on_previous_text: Use context from previous segments
        """
        self.model_name = model_name
        self.language = language
        self.fp16 = fp16
        self.condition_on_previous_text = condition_on_previous_text
        
        # Determine device
        # NOTE: Whisper has known issues with NaN values on MPS, so we force CPU
        # even if MPS is available. This is more stable for speech recognition.
        if device == "auto":
            if torch.cuda.is_available():
                self.device = "cuda"
            else:
                # Use CPU for Whisper (more stable than MPS)
                self.device = "cpu"
        else:
            self.device = device
        
        # Disable FP16 if on CPU
        if self.device == "cpu":
            self.fp16 = False
            
        if device == "auto" and torch.backends.mps.is_available():
            logger.info("MPS available but using CPU for Whisper (more stable for audio transcription)")
        
        logger.info(f"Loading Whisper model: {model_name} on {self.device}")
        
        # Load model
        self.model = whisper.load_model(model_name, device=self.device)
        
        logger.info("Whisper model loaded successfully")
    
    def transcribe(self, audio_path: str) -> Transcript:
        """
        Transcribe audio file.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Transcript entity with segments
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        logger.info(f"Transcribing audio: {audio_path.name}")
        
        # Transcribe
        result = self.model.transcribe(
            str(audio_path),
            language=self.language,
            fp16=self.fp16,
            condition_on_previous_text=self.condition_on_previous_text,
            verbose=False,
        )
        
        # Extract segments
        segments = []
        for segment in result.get('segments', []):
            segments.append(TranscriptSegment(
                text=segment['text'].strip(),
                start=segment['start'],
                end=segment['end'],
            ))
        
        # Create transcript
        transcript = Transcript(
            full_text=result.get('text', '').strip(),
            segments=segments,
            language=result.get('language', self.language or 'unknown'),
        )
        
        logger.info(f"Transcribed {len(segments)} segments, language: {transcript.language}")
        logger.debug(f"First 100 chars: {transcript.full_text[:100]}...")
        
        return transcript
