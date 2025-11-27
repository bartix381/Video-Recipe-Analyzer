"""Roboflow-based ingredient detection using official SDK."""
import logging
from typing import List
from pathlib import Path
from roboflow import Roboflow

from ..entities import DetectedObject

logger = logging.getLogger(__name__)


class RoboflowDetector:
    """Ingredient detection using Roboflow SDK."""
    
    def __init__(
        self,
        api_key: str,
        workspace: str = "python-wfiwe",
        project: str = "ingredients-mqhxf",
        version: int = 1,
        conf_threshold: float = 0.40,
        overlap_threshold: float = 0.30,
    ):
        """
        Initialize Roboflow detector.
        
        Args:
            api_key: Roboflow API key (get from https://app.roboflow.com/settings/api)
            workspace: Roboflow workspace ID
            project: Project ID
            version: Model version number
            conf_threshold: Confidence threshold (0-1)
            overlap_threshold: Overlap threshold for NMS (0-1)
        """
        self.conf_threshold = conf_threshold
        self.overlap_threshold = overlap_threshold
        
        # Initialize Roboflow
        rf = Roboflow(api_key=api_key)
        self.project = rf.workspace(workspace).project(project)
        self.model = self.project.version(version).model
        
        logger.info(f"Initialized Roboflow detector: {workspace}/{project}/v{version}")
        logger.info(f"Confidence threshold: {conf_threshold}, Overlap: {overlap_threshold}")
    
    def detect(self, image_path: str, timestamp: float = 0.0) -> List[DetectedObject]:
        """
        Detect ingredients in a single image.
        
        Args:
            image_path: Path to image file
            timestamp: Timestamp in seconds
            
        Returns:
            List of detected ingredients
        """
        image_path = Path(image_path)
        
        # Run inference using Roboflow SDK
        result = self.model.predict(
            str(image_path),
            confidence=int(self.conf_threshold * 100),
            overlap=int(self.overlap_threshold * 100)
        ).json()
        
        # Parse predictions
        detections = []
        for pred in result.get("predictions", []):
            # Convert Roboflow format to our format
            # Roboflow gives: x, y, width, height (center + dimensions)
            detection = DetectedObject(
                label=pred["class"],
                confidence=pred["confidence"],
                bbox=(pred["x"], pred["y"], pred["width"], pred["height"]),
                timestamp=timestamp
            )
            detections.append(detection)
        
        return detections
    
    def detect_batch(self, frames: List['Frame']) -> List['Frame']:
        """
        Detect ingredients in multiple frames.
        
        Args:
            frames: List of Frame objects
            
        Returns:
            Frames with detections added
        """
        logger.info(f"Detecting ingredients in {len(frames)} frames using Roboflow")
        
        for i, frame in enumerate(frames):
            if (i + 1) % 100 == 0:
                logger.info(f"Processed {i + 1}/{len(frames)} frames")
            
            detections = self.detect(frame.image_path, frame.timestamp)
            frame.detected_objects.extend(detections)
        
        total_detections = sum(len(frame.detected_objects) for frame in frames)
        logger.info(f"Detected {total_detections} ingredients across {len(frames)} frames")
        
        return frames
