"""EasyOCR engine wrapper."""
import easyocr
import logging
from pathlib import Path
from typing import List
from ..entities import Frame

logger = logging.getLogger(__name__)


class OCREngine:
    """EasyOCR-based text extraction from frames."""
    
    def __init__(
        self,
        languages: List[str] = None,
        gpu: bool = True,
        confidence_threshold: float = 0.4,
        paragraph: bool = False,
        batch_size: int = 1
    ):
        """
        Initialize OCR engine.
        
        Args:
            languages: List of language codes (default: ["en"])
            gpu: Use GPU if available
            confidence_threshold: Minimum confidence for text detection
            paragraph: Return text as paragraphs
            batch_size: Batch size for processing
        """
        if languages is None:
            languages = ["en"]
        
        self.languages = languages
        self.gpu = gpu
        self.confidence_threshold = confidence_threshold
        self.paragraph = paragraph
        self.batch_size = batch_size
        
        logger.info(f"Initializing EasyOCR with languages: {languages}")
        
        # Initialize reader
        self.reader = easyocr.Reader(
            languages,
            gpu=gpu,
            verbose=False
        )
        
        logger.info("EasyOCR initialized successfully")
    
    def extract_text(self, frame: Frame) -> Frame:
        """
        Extract text from frame using OCR.
        
        Args:
            frame: Frame entity with image_path
            
        Returns:
            Frame entity with ocr_text populated
        """
        image_path = frame.image_path
        
        # Run OCR
        results = self.reader.readtext(
            image_path,
            paragraph=self.paragraph,
            batch_size=self.batch_size
        )
        
        # Filter by confidence and extract text
        texts = []
        for (bbox, text, confidence) in results:
            if confidence >= self.confidence_threshold:
                texts.append(text)
        
        # Combine all text
        frame.ocr_text = " ".join(texts) if texts else None
        
        if frame.ocr_text:
            logger.debug(f"Extracted text at {frame.timestamp:.2f}s: {frame.ocr_text[:50]}...")
        
        return frame
    
    def extract_batch(self, frames: List[Frame]) -> List[Frame]:
        """
        Extract text from multiple frames.
        
        Args:
            frames: List of Frame entities
            
        Returns:
            List of Frame entities with ocr_text populated
        """
        if not frames:
            return frames
        
        logger.info(f"Extracting text from {len(frames)} frames")
        
        # Process each frame
        for frame in frames:
            self.extract_text(frame)
        
        text_count = sum(1 for f in frames if f.ocr_text)
        logger.info(f"Found text in {text_count}/{len(frames)} frames")
        
        return frames
