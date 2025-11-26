"""HuggingFace-based food classifier for ingredient recognition."""
import torch
import logging
from pathlib import Path
from typing import List
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification
from ..entities import DetectedObject, Frame

logger = logging.getLogger(__name__)


class FoodClassifier:
    """Food classification using HuggingFace models (Food-101, etc)."""
    
    def __init__(
        self,
        model_name: str = "nateraw/food",
        conf_threshold: float = 0.10,
        device: str = "auto",
    ):
        """
        Initialize food classifier.
        
        Args:
            model_name: HuggingFace model ID (e.g., 'nateraw/food' for Food-101)
            conf_threshold: Confidence threshold (0-1)
            device: Device to use (auto, cpu, cuda, mps)
        """
        self.model_name = model_name
        self.conf_threshold = conf_threshold
        
        # Determine device
        if device == "auto":
            if torch.cuda.is_available():
                self.device = "cuda"
            elif torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"
        else:
            self.device = device
        
        self.processor = None
        self.model = None
        
        logger.info(f"Initialized FoodClassifier: {model_name} on {self.device}")
    
    def _load_model(self):
        """Lazy load model on first use."""
        if self.model is None:
            logger.info(f"Loading food classification model: {self.model_name} on {self.device}")
            self.processor = AutoImageProcessor.from_pretrained(self.model_name)
            self.model = AutoModelForImageClassification.from_pretrained(self.model_name)
            self.model = self.model.to(self.device)
            self.model.eval()
            logger.info("Food classification model loaded successfully")
    
    def classify(self, image_path: str, timestamp: float = 0.0, top_k: int = 3) -> List[DetectedObject]:
        """
        Classify food items in a single image.
        
        Args:
            image_path: Path to image file
            timestamp: Timestamp for this frame
            top_k: Return top K predictions above threshold
            
        Returns:
            List of DetectedObject entities
        """
        self._load_model()
        
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            inputs = self.processor(image, return_tensors='pt')
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Run inference
            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Get top K predictions
            top_probs, top_indices = torch.topk(probs[0], top_k)
            
            # Convert to DetectedObject entities
            detections = []
            for prob, idx in zip(top_probs, top_indices):
                confidence = prob.item()
                if confidence >= self.conf_threshold:
                    label = self.model.config.id2label[idx.item()]
                    
                    # Note: Image classification doesn't provide bounding boxes
                    # Use full image bounds as placeholder
                    bbox = [0.0, 0.0, float(image.width), float(image.height)]
                    
                    detections.append(DetectedObject(
                        label=label,
                        confidence=confidence,
                        bbox=bbox,
                        timestamp=timestamp,
                    ))
            
            return detections
            
        except Exception as e:
            logger.error(f"Error classifying image {image_path}: {e}")
            return []
    
    def classify_batch(self, frames: List[Frame]) -> List[Frame]:
        """
        Classify food items in multiple frames.
        
        Args:
            frames: List of Frame entities with image paths
            
        Returns:
            List of Frame entities with detected_objects populated
        """
        self._load_model()
        
        logger.info(f"Classifying food in {len(frames)} frames")
        
        for frame in frames:
            detections = self.classify(
                frame.image_path,
                timestamp=frame.timestamp,
                top_k=3  # Get top 3 food predictions per frame
            )
            frame.detected_objects.extend(detections)
        
        total_detections = sum(len(f.detected_objects) for f in frames)
        logger.info(f"Classified {total_detections} food items across {len(frames)} frames")
        
        return frames
