"""YOLOv8 object detector wrapper."""
import torch
import logging
from pathlib import Path
from typing import List
from ultralytics import YOLO
from ..entities import DetectedObject, Frame

logger = logging.getLogger(__name__)


class ObjectDetector:
    """YOLOv8-based object detector for ingredient recognition."""
    
    def __init__(
        self,
        model_name: str = "yolov8n.pt",
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        max_det: int = 300,
        device: str = "auto",
        fp16: bool = True
    ):
        """
        Initialize object detector.
        
        Args:
            model_name: YOLO model name (yolov8n.pt, yolov8s.pt, etc.)
            conf_threshold: Confidence threshold (0-1)
            iou_threshold: IoU threshold for NMS
            max_det: Maximum detections per image
            device: Device to use (auto, cpu, cuda, mps)
            fp16: Use FP16 inference (faster on GPU/MPS)
        """
        self.model_name = model_name
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.max_det = max_det
        self.fp16 = fp16
        
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
        
        logger.info(f"Loading YOLO model: {model_name} on {self.device}")
        
        # Load model
        self.model = YOLO(model_name)
        
        # Set device
        if self.device == "mps":
            # For MPS, we need to handle it differently
            self.model.to("mps")
        else:
            self.model.to(self.device)
        
        logger.info(f"YOLO model loaded successfully")
    
    def detect(self, frame: Frame) -> Frame:
        """
        Detect objects in a frame.
        
        Args:
            frame: Frame entity with image_path
            
        Returns:
            Frame entity with detected_objects populated
        """
        image_path = frame.image_path
        
        # Run inference
        results = self.model(
            image_path,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            max_det=self.max_det,
            half=self.fp16 and self.device in ["cuda", "mps"],
            verbose=False,
        )
        
        # Parse results
        detected_objects = []
        for result in results:
            boxes = result.boxes
            if boxes is not None and len(boxes) > 0:
                for i in range(len(boxes)):
                    box = boxes[i]
                    detected_objects.append(DetectedObject(
                        label=result.names[int(box.cls[0])],
                        confidence=float(box.conf[0]),
                        bbox=box.xyxy[0].tolist(),
                        timestamp=frame.timestamp,
                    ))
        
        frame.detected_objects = detected_objects
        logger.debug(f"Detected {len(detected_objects)} objects at {frame.timestamp:.2f}s")
        
        return frame
    
    def detect_batch(self, frames: List[Frame]) -> List[Frame]:
        """
        Detect objects in multiple frames (batch processing).
        
        Args:
            frames: List of Frame entities
            
        Returns:
            List of Frame entities with detected_objects populated
        """
        if not frames:
            return frames
        
        logger.info(f"Detecting objects in {len(frames)} frames")
        
        # Prepare image paths
        image_paths = [f.image_path for f in frames]
        
        # Run batch inference
        results = self.model(
            image_paths,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            max_det=self.max_det,
            half=self.fp16 and self.device in ["cuda", "mps"],
            verbose=False,
        )
        
        # Parse results for each frame
        for frame, result in zip(frames, results):
            detected_objects = []
            boxes = result.boxes
            if boxes is not None and len(boxes) > 0:
                for i in range(len(boxes)):
                    box = boxes[i]
                    detected_objects.append(DetectedObject(
                        label=result.names[int(box.cls[0])],
                        confidence=float(box.conf[0]),
                        bbox=box.xyxy[0].tolist(),
                        timestamp=frame.timestamp,
                    ))
            frame.detected_objects = detected_objects
        
        total_detections = sum(len(f.detected_objects) for f in frames)
        logger.info(f"Detected {total_detections} total objects across {len(frames)} frames")
        
        return frames
