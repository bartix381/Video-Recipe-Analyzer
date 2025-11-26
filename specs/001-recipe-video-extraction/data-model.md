# Data Models for Recipe Video Extraction

## Core Entities

### Video
```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Video:
    """Represents a recipe video from YouTube or Instagram"""
    url: str
    platform: str  # "youtube" or "instagram"
    title: Optional[str] = None
    duration: Optional[float] = None  # seconds
    local_path: Optional[str] = None  # temporary download path
```

**Attributes**:
- `url`: Original video URL
- `platform`: Source platform (youtube/instagram)
- `title`: Video title (if available from metadata)
- `duration`: Total video length in seconds
- `local_path`: Path to downloaded video file

**Relationships**:
- Has many `Frame` objects (extracted at intervals)
- Has one `Transcript` (from audio)

---

### Frame
```python
@dataclass
class Frame:
    """Single video frame extracted at specific timestamp"""
    timestamp: float  # seconds from video start
    image_path: str  # path to saved frame image
    detected_objects: List['DetectedObject'] = None
    ocr_text: Optional[str] = None
```

**Attributes**:
- `timestamp`: Position in video (seconds)
- `image_path`: Path to saved frame image file
- `detected_objects`: List of objects detected in this frame
- `ocr_text`: Text extracted via OCR (if any)

**Relationships**:
- Belongs to one `Video`
- Has many `DetectedObject` instances

---

### DetectedObject
```python
@dataclass
class DetectedObject:
    """Object detected in a frame (e.g., bowl of flour, eggs)"""
    label: str  # object class name
    confidence: float  # detection confidence 0-1
    bbox: List[float]  # [x1, y1, x2, y2] bounding box
    timestamp: float  # from parent frame
```

**Attributes**:
- `label`: Object class (e.g., "bowl", "egg", "flour")
- `confidence`: Detection confidence score (0.0 to 1.0)
- `bbox`: Bounding box coordinates [x1, y1, x2, y2]
- `timestamp`: When object was detected (from frame)

**Relationships**:
- Belongs to one `Frame`
- May map to one or more `Ingredient` instances

---

### Ingredient
```python
@dataclass
class Ingredient:
    """Parsed ingredient with quantity and metadata"""
    name: str  # normalized ingredient name
    quantity: Optional[float] = None
    unit: Optional[str] = None  # "cup", "tsp", "g", "ml", etc.
    source: str = "unknown"  # "visual", "ocr", "audio"
    confidence: float = 0.0  # 0-1
    timestamp: Optional[float] = None
    raw_text: Optional[str] = None  # original text before parsing
```

**Attributes**:
- `name`: Normalized ingredient name (e.g., "flour", "butter")
- `quantity`: Numeric amount (e.g., 2.0, 1.5)
- `unit`: Measurement unit (cup, tsp, tbsp, g, ml, oz, etc.)
- `source`: Detection source (visual/ocr/audio/merged)
- `confidence`: Extraction confidence (0.0 to 1.0)
- `timestamp`: When ingredient was detected/mentioned
- `raw_text`: Original text before normalization

**Relationships**:
- May be detected in multiple `Frame` instances
- May be mentioned in `Transcript`
- Aggregated into final `Recipe`

**Normalization Rules**:
- Lowercase ingredient names
- Remove extra whitespace
- Standardize units (e.g., "tablespoon" → "tbsp")
- Merge similar names (fuzzy matching >85%)

---

### Step
```python
from enum import Enum

class ActionVerb(Enum):
    """Common cooking action verbs"""
    MIX = "mix"
    WHISK = "whisk"
    BAKE = "bake"
    BOIL = "boil"
    CHOP = "chop"
    SLICE = "slice"
    HEAT = "heat"
    ADD = "add"
    POUR = "pour"
    STIR = "stir"
    COOL = "cool"
    REFRIGERATE = "refrigerate"

@dataclass
class Step:
    """Cooking instruction/step with timestamp"""
    sequence: int  # step number (1, 2, 3...)
    description: str  # human-readable step description
    timestamp: float  # seconds from video start
    action: Optional[ActionVerb] = None
    source: str = "audio"  # "audio", "ocr", "inferred"
    confidence: float = 0.0
```

**Attributes**:
- `sequence`: Step number in order (1, 2, 3, ...)
- `description`: Human-readable instruction
- `timestamp`: When step occurs in video
- `action`: Primary cooking action (enum)
- `source`: How step was detected
- `confidence`: Extraction confidence (0.0 to 1.0)

**Relationships**:
- Belongs to one `Recipe`
- May reference one or more `Ingredient` instances

**Action Verb Detection**:
- Parse transcript for action verbs
- Common patterns: "now we will [action]", "next, [action] the..."
- Map verbs to ActionVerb enum

---

### Transcript
```python
@dataclass
class Transcript:
    """Video audio transcript with timestamps"""
    full_text: str  # complete transcript
    segments: List['TranscriptSegment'] = None
    language: str = "en"

@dataclass
class TranscriptSegment:
    """Time-aligned transcript segment"""
    text: str
    start: float  # seconds
    end: float  # seconds
```

**Attributes**:
- `full_text`: Complete transcribed text
- `segments`: Time-aligned segments (from Whisper)
- `language`: Detected/specified language code

**TranscriptSegment**:
- `text`: Segment text (sentence or phrase)
- `start`: Segment start time (seconds)
- `end`: Segment end time (seconds)

**Relationships**:
- Belongs to one `Video`
- Contains mentions of `Ingredient` and `Step` instances

**Processing**:
- Whisper provides timestamp-aligned segments
- Parse segments for ingredient mentions
- Parse segments for cooking steps
- Extract timestamps for recipe navigation

---

### Recipe
```python
@dataclass
class Recipe:
    """Final structured recipe output"""
    title: Optional[str] = None
    source_url: str = ""
    ingredients: List[Ingredient] = None
    steps: List[Step] = None
    extraction_date: str = ""  # ISO format
    processing_time: float = 0.0  # seconds
    metadata: dict = None  # additional info (models used, config, etc.)
```

**Attributes**:
- `title`: Recipe title (from video metadata or transcript)
- `source_url`: Original video URL
- `ingredients`: List of all extracted ingredients
- `steps`: Sequential cooking steps
- `extraction_date`: ISO 8601 timestamp (e.g., "2025-11-26T10:30:00Z")
- `processing_time`: Total extraction time (seconds)
- `metadata`: Additional context (models, config, versions)

**Relationships**:
- Aggregates all `Ingredient` instances
- Aggregates all `Step` instances
- Links to source `Video`

**Output Formats**:
- JSON (default, structured)
- Markdown (human-readable)
- Plain text (simple lists)

---

## Entity Relationships

```
Video (1) ──┬──> Frames (many)
            │    └──> DetectedObjects (many)
            │
            └──> Transcript (1)
                 └──> TranscriptSegments (many)

Recipe (1) ──┬──> Ingredients (many)
             │    └── Sources: Visual, OCR, Audio
             │
             └──> Steps (many)
                  └── Extracted from Transcript
```

## Data Flow

1. **Video Download** → `Video` entity with `local_path`
2. **Frame Extraction** → Multiple `Frame` entities with timestamps
3. **Object Detection** → `DetectedObject` instances per frame
4. **OCR** → Add `ocr_text` to frames
5. **Transcription** → `Transcript` with `TranscriptSegment` list
6. **Ingredient Parsing** → Extract `Ingredient` from all sources
7. **Step Parsing** → Extract `Step` from transcript
8. **Aggregation** → Merge into final `Recipe`
9. **Output** → Serialize `Recipe` to JSON/Markdown/text

## Validation Rules

### Ingredient Validation
- `name` must not be empty
- `quantity` must be positive (if present)
- `unit` must be from known units list (if present)
- `confidence` must be between 0.0 and 1.0
- `source` must be one of: visual, ocr, audio, merged

### Step Validation
- `sequence` must be positive integer
- `description` must not be empty
- `timestamp` must be within video duration
- `confidence` must be between 0.0 and 1.0

### Recipe Validation
- `source_url` must be valid URL
- `ingredients` list must not be empty
- `steps` list must not be empty
- `steps` must be ordered by sequence number
- `extraction_date` must be valid ISO 8601 timestamp
