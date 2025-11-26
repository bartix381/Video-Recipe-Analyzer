"""Data models for recipe video extraction."""
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class ActionVerb(Enum):
    """Common cooking action verbs."""
    MIX = "mix"
    WHISK = "whisk"
    BAKE = "bake"
    BOIL = "boil"
    CHOP = "chop"
    SLICE = "slice"
    DICE = "dice"
    HEAT = "heat"
    ADD = "add"
    POUR = "pour"
    STIR = "stir"
    COOL = "cool"
    REFRIGERATE = "refrigerate"
    FRY = "fry"
    SIMMER = "simmer"
    BLEND = "blend"
    COMBINE = "combine"
    FOLD = "fold"
    SEASON = "season"


@dataclass
class Video:
    """Represents a recipe video from YouTube or Instagram."""
    url: str
    platform: str  # "youtube" or "instagram"
    title: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[float] = None  # seconds
    local_path: Optional[str] = None  # temporary download path


@dataclass
class DetectedObject:
    """Object detected in a frame (e.g., bowl of flour, eggs)."""
    label: str  # object class name
    confidence: float  # detection confidence 0-1
    bbox: List[float]  # [x1, y1, x2, y2] bounding box
    timestamp: float  # from parent frame


@dataclass
class Frame:
    """Single video frame extracted at specific timestamp."""
    timestamp: float  # seconds from video start
    image_path: str  # path to saved frame image
    detected_objects: List[DetectedObject] = field(default_factory=list)
    ocr_text: Optional[str] = None


@dataclass
class Ingredient:
    """Parsed ingredient with quantity and metadata."""
    name: str  # normalized ingredient name
    quantity: Optional[float] = None
    unit: Optional[str] = None  # "cup", "tsp", "g", "ml", etc.
    source: str = "unknown"  # "visual", "ocr", "audio", "merged"
    confidence: float = 0.0  # 0-1
    timestamps: List[float] = field(default_factory=list)  # Multiple timestamps if mentioned multiple times
    raw_text: Optional[str] = None  # original text before parsing
    alternative_note: Optional[str] = None  # For substitutions like "or olive oil"


@dataclass
class TranscriptSegment:
    """Time-aligned transcript segment."""
    text: str
    start: float  # seconds
    end: float  # seconds


@dataclass
class Transcript:
    """Video audio transcript with timestamps."""
    full_text: str  # complete transcript
    segments: List[TranscriptSegment] = field(default_factory=list)
    language: str = "en"


@dataclass
class Step:
    """Cooking instruction/step with timestamp."""
    sequence: int  # step number (1, 2, 3...)
    description: str  # human-readable step description
    timestamp: float  # seconds from video start
    action: Optional[ActionVerb] = None
    source: str = "audio"  # "audio", "ocr", "inferred"
    confidence: float = 0.0


@dataclass
class Recipe:
    """Final structured recipe output."""
    source_url: str
    ingredients: List[Ingredient] = field(default_factory=list)
    steps: List[Step] = field(default_factory=list)
    title: Optional[str] = None
    extraction_date: Optional[str] = None  # ISO format
    processing_time: float = 0.0  # seconds
    metadata: Optional[dict] = None  # additional info (models used, config, etc.)
    
    def to_dict(self) -> dict:
        """Convert recipe to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "source_url": self.source_url,
            "ingredients": [
                {
                    "name": ing.name,
                    "quantity": ing.quantity,
                    "unit": ing.unit,
                    "source": ing.source,
                    "confidence": ing.confidence,
                    "timestamps": ing.timestamps,
                    "raw_text": ing.raw_text,
                    "alternative_note": ing.alternative_note,
                }
                for ing in self.ingredients
            ],
            "steps": [
                {
                    "sequence": step.sequence,
                    "description": step.description,
                    "timestamp": step.timestamp,
                    "action": step.action.value if step.action else None,
                    "source": step.source,
                    "confidence": step.confidence,
                }
                for step in self.steps
            ],
            "extraction_date": self.extraction_date,
            "processing_time": self.processing_time,
            "metadata": self.metadata,
        }
