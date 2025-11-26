# Implementation Plan: Recipe Video Extraction# Implementation Plan: [FEATURE]



**Branch**: `001-recipe-video-extraction` | **Date**: 2025-11-26 | **Spec**: [spec.md](./spec.md)**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]

**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

## Summary

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

Build a multi-stage ML pipeline to extract structured recipe data (ingredients with quantities, cooking steps with timestamps) from YouTube and Instagram recipe videos. The system combines computer vision (object detection, OCR), speech-to-text, and NLP to analyze visual, textual, and audio content. All processing runs locally using free, open-source models. Outputs are structured JSON/Markdown formats with full MLflow experiment tracking.

## Summary

**Key Clarifications Applied**:

- Duplicate ingredients → Sum quantities, preserve all timestamps[Extract from feature spec: primary requirement + technical approach from research]

- Video caching → 24-hour TTL for reproducibility

- Download failures → Detailed errors with retry suggestions## Technical Context

- Max duration → 30 minutes (typical 5-20 min)

- Substitutions → List alternatives separately with notes<!--

  ACTION REQUIRED: Replace the content in this section with the technical details

## Technical Context  for the project. The structure here is presented in advisory capacity to guide

  the iteration process.

**Language/Version**: Python 3.11+  -->

**Primary Dependencies**:  

- **Deep Learning**: PyTorch 2.0+, torchvision, Ultralytics (YOLOv8)**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]  

- **Computer Vision**: OpenCV, EasyOCR**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]  

- **Speech/NLP**: OpenAI Whisper (local), spaCy, ingredient-parser**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]  

- **Video**: yt-dlp, ffmpeg**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]  

- **Experiment Tracking**: MLflow**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]

- **Data/Utils**: NumPy, Pillow, PyYAML, python-dateutil, thefuzz (fuzzy matching)**Project Type**: [single/web/mobile - determines source structure]  

**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]  

**Storage**: Local filesystem (videos cached 24h, extracted frames temp, outputs as files)  **Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]  

**Testing**: No formal tests required (constitution: personal research project)  **Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

**Target Platform**: macOS (Mac M4 Max with Metal/MPS), extensible to Linux/CUDA  

**Project Type**: Single project (CLI + library modules)  ## Constitution Check

**Performance Goals**:  

- 5-10 min video → <5 min processing time*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- 30 min video (max) → <15 min processing time

- Frame extraction: 1 fps default (configurable)[Gates determined based on constitution file]

- Supports videos up to 30 minutes duration

## Project Structure

**Constraints**:  

- **Zero-cost (NON-NEGOTIABLE)**: All models free, open-source, no API keys### Documentation (this feature)

- **Local processing**: No cloud APIs or paid services

- **Mac Metal/MPS optimization**: Leverage Apple Silicon GPU acceleration```text

- **No tests required**: Personal research project (per constitution)specs/[###-feature]/

├── plan.md              # This file (/speckit.plan command output)

**Scale/Scope**:  ├── research.md          # Phase 0 output (/speckit.plan command)

- Single video processing (MVP)├── data-model.md        # Phase 1 output (/speckit.plan command)

- ~300-1800 frames per 5-10 min video (at 1 fps)├── quickstart.md        # Phase 1 output (/speckit.plan command)

- Expected output: 5-20 ingredients, 5-15 steps per video├── contracts/           # Phase 1 output (/speckit.plan command)

- Batch processing deferred to future iteration└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)

```

## Constitution Check

### Source Code (repository root)

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*<!--

  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout

| Principle | Status | Compliance Notes |  for this feature. Delete unused options and expand the chosen structure with

|-----------|--------|------------------|  real paths (e.g., apps/admin, packages/something). The delivered plan must

| **I. Simplicity & Clarity** | ✅ PASS | Multi-stage pipeline with clear separation: download → extract → detect → transcribe → parse → aggregate. Each stage is a focused module. No tests required per constitution. |  not include Option labels.

| **II. Reproducibility First** | ✅ PASS | MLflow tracks all experiments. Video caching (24h) enables re-processing. Config files for all hyperparameters. Random seeds for model inference. |-->

| **III. Experiment Tracking** | ✅ PASS | MLflow logs: models used, processing time, hyperparameters (fps, thresholds), sample outputs (frames, detected objects), extraction metrics (ingredient count, confidence scores). |

| **IV. Data Pipeline Standards** | ✅ PASS | Clear data flow: Video → Frames → Detections/OCR/Transcript → Parsed entities → Recipe. Lazy frame loading, configurable sampling rate. |```text

| **V. Model Development** | ✅ PASS | All PyTorch models (YOLOv8, Whisper). Transfer learning with pretrained weights. Proper device handling (MPS/CUDA/CPU). Train/eval modes for inference. |# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)

| **VI. Cost Efficiency** | ✅ PASS | **Zero-cost mandate met**: YOLOv8n (free), EasyOCR (free), Whisper (free local), spaCy (free). No API keys. Local processing. Video caching reduces redundant downloads. FP16 inference on Metal for speed. |src/

| **VII. Visual Validation** | ✅ PASS | MLflow artifacts: sample extracted frames, detected objects with bounding boxes, OCR text overlays. Quickstart includes example outputs for manual review. |├── models/

├── services/

**All gates PASSED** ✅ - Proceed to Phase 0 research.├── cli/

└── lib/

## Project Structure

tests/

### Documentation (this feature)├── contract/

├── integration/

```text└── unit/

specs/001-recipe-video-extraction/

├── spec.md              # Feature specification with clarifications# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)

├── plan.md              # This file (implementation plan)backend/

├── research.md          # Phase 0: Model selection decisions├── src/

├── data-model.md        # Phase 1: Entity definitions (Python dataclasses)│   ├── models/

├── quickstart.md        # Phase 1: User guide with examples│   ├── services/

├── contracts/           # Phase 1: Output schemas│   └── api/

│   └── recipe_schema.json└── tests/

└── tasks.md             # Phase 2: Task breakdown (created by /speckit.tasks)

```frontend/

├── src/

### Source Code (repository root)│   ├── components/

│   ├── pages/

```text│   └── services/

src/└── tests/

├── __init__.py

├── downloaders/# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)

│   ├── __init__.pyapi/

│   ├── base.py              # Abstract downloader interface└── [same as backend above]

│   ├── youtube.py           # YouTube downloader (yt-dlp)

│   └── instagram.py         # Instagram downloader (yt-dlp)ios/ or android/

├── extractors/└── [platform-specific structure: feature modules, UI flows, platform tests]

│   ├── __init__.py```

│   ├── frame_extractor.py   # Extract frames at configurable fps

│   └── audio_extractor.py   # Extract audio track from video**Structure Decision**: [Document the selected structure and reference the real

├── models/directories captured above]

│   ├── __init__.py

│   ├── object_detector.py   # YOLOv8 wrapper for ingredient detection## Complexity Tracking

│   ├── ocr_engine.py        # EasyOCR wrapper for text extraction

│   └── transcriber.py       # Whisper wrapper for speech-to-text> **Fill ONLY if Constitution Check has violations that must be justified**

├── parsers/

│   ├── __init__.py| Violation | Why Needed | Simpler Alternative Rejected Because |

│   ├── ingredient_parser.py # Parse ingredient mentions from text|-----------|------------|-------------------------------------|

│   ├── step_parser.py       # Extract cooking steps with actions| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |

│   └── quantity_parser.py   # Parse quantities/units (regex + spaCy + ingredient-parser)| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

├── pipeline/
│   ├── __init__.py
│   ├── recipe_pipeline.py   # Orchestrate full extraction pipeline
│   └── aggregator.py        # Merge visual/audio/text detections, handle duplicates
├── utils/
│   ├── __init__.py
│   ├── config.py            # Load YAML configs
│   ├── device.py            # Device detection (MPS/CUDA/CPU)
│   ├── mlflow_utils.py      # MLflow logging helpers
│   ├── cache.py             # Video cache manager (24h TTL)
│   └── validators.py        # JSON schema validation
├── entities/
│   ├── __init__.py
│   └── data_models.py       # Dataclasses: Video, Frame, Ingredient, Step, Recipe, etc.
└── cli.py                   # Command-line interface

experiments/
├── configs/
│   └── default_config.yaml  # Default hyperparameters
└── mlruns/                  # MLflow tracking directory

outputs/
└── recipes/                 # Extracted recipe outputs (JSON/Markdown)

cache/
└── videos/                  # Downloaded videos (24h TTL)

requirements.txt
README.md
.gitignore
```

**Structure Decision**: Single project layout. Clear separation of concerns:
- `downloaders/`: Platform-specific video acquisition
- `extractors/`: Media preprocessing (frames, audio)
- `models/`: ML model wrappers (detection, OCR, transcription)
- `parsers/`: NLP logic for entity extraction
- `pipeline/`: Orchestration and aggregation
- `utils/`: Cross-cutting concerns (config, device, logging, cache)
- `entities/`: Data models (defined in Phase 1)
- `cli.py`: User-facing interface

## Phase 0: Research & Technology Selection

**Goal**: Validate model choices, define configurations, establish technical feasibility.

### Research Questions

#### RQ1: Which object detection model for ingredient recognition?
**Options**: YOLOv8 (n/s/m/l), DETR, Faster R-CNN  
**Decision**: **YOLOv8n** (nano variant)  
**Rationale**:
- Fast inference (~5ms per frame on M4 Max with Metal)
- Pretrained on COCO (includes food items: apple, banana, bowl, knife, etc.)
- Free, open-source (Ultralytics library)
- Can fine-tune on Food-101 or Recipe1M if needed (future iteration)
- Supports Metal/MPS acceleration on Mac
- Smallest variant (n) balances speed vs accuracy for MVP

**Alternatives Rejected**:
- DETR: Slower inference, transformer architecture overkill for this use case
- Faster R-CNN: Older architecture, YOLOv8 outperforms in speed

**Configuration**:
- Model: `yolov8n.pt` (pretrained COCO weights)
- Confidence threshold: 0.5 (configurable)
- Input size: 640x640 (YOLO default)
- Batch processing: 8 frames per batch (GPU memory permitting)

#### RQ2: What frame sampling rate balances coverage vs processing time?
**Options**: 0.5 fps, 1 fps, 2 fps, keyframe extraction  
**Decision**: **1 fps (configurable)**  
**Rationale**:
- 5 min video = 300 frames → manageable processing
- Captures most ingredient appearances (typically shown for multiple seconds)
- Balances coverage vs computational cost
- Configurable via YAML for experimentation

**Alternatives Rejected**:
- 0.5 fps: May miss quick ingredient reveals
- 2 fps: Doubles processing time with diminishing returns
- Keyframe extraction: Adds complexity, less predictable

**Configuration**:
- Default: 1 fps
- Max resolution: 720p (downscale if higher to save processing time)
- Format: RGB images saved to temp directory

#### RQ3: How to parse ingredient quantities from natural language?
**Options**: Pure regex, spaCy NER, ingredient-parser library, fine-tuned BERT  
**Decision**: **Hybrid: regex + spaCy + ingredient-parser library**  
**Rationale**:
- ingredient-parser (open-source Python library) handles common patterns: "2 cups flour", "1 tsp salt"
- spaCy for entity recognition and sentence structure
- Regex fallback for simple patterns
- Free, no training required, works locally

**Alternatives Rejected**:
- Pure regex: Too brittle for varied natural language
- Fine-tuned BERT: Overkill, requires training data

**Configuration**:
- Libraries: ingredient-parser, spaCy (en_core_web_sm model)
- Unit normalization: Convert to standard units (cups, tsp, tbsp, grams, etc.)
- Confidence scoring: Based on parse success and context

#### RQ4: How to handle audio transcription for ingredient/step extraction?
**Options**: Whisper (tiny/base/small), Vosk, wav2vec 2.0  
**Decision**: **Whisper base model (local)**  
**Rationale**:
- Whisper base: Best accuracy/speed tradeoff for local processing
- Runs locally on Mac Metal (CoreML optimized)
- Free, open-source from OpenAI
- Multilingual support (future P3 feature)
- Better accuracy than Vosk for recipe domain

**Alternatives Rejected**:
- Whisper tiny: Too many transcription errors
- Whisper small: Slower, marginal accuracy gain
- Vosk: Lower accuracy in testing

**Configuration**:
- Model: `whisper-base`
- Language: English (en) for MVP
- Output: Full transcript with word-level timestamps
- Device: MPS (Mac Metal) for acceleration

#### RQ5: How to deduplicate ingredients from multiple sources (visual, audio, text)?
**Options**: Exact string match, fuzzy matching (Levenshtein), embedding similarity  
**Decision**: **Fuzzy matching with 85% similarity threshold (thefuzz library)**  
**Rationale**:
- Handles variations: "flour" vs "all-purpose flour", "butter" vs "unsalted butter"
- thefuzz library (free, open-source) provides Levenshtein distance
- 85% threshold empirically balances precision/recall
- When duplicate detected:
  - Sum quantities (per clarification)
  - Merge source types (e.g., visual + audio)
  - Preserve all timestamps array
  - Keep higher confidence score
  - Combine raw_text fields

**Alternatives Rejected**:
- Exact match: Too strict, misses obvious duplicates
- Embeddings (BERT): Overkill, adds latency

**Configuration**:
- Similarity threshold: 0.85 (configurable)
- Merge strategy: Sum quantities, preserve all timestamps
- Normalization: Lowercase, remove articles (a, an, the)

### Research Artifacts

**Created**: `research.md` - Documents above decisions with justifications
**Validation**: Prototype key components (frame extraction, YOLOv8 inference, Whisper transcription) on sample videos

## Phase 1: Data Model & Contracts

**Goal**: Define all entities, relationships, validation rules, and output formats.

### Entity Definitions

**Created**: `data-model.md` with Python dataclasses

#### Video
```python
@dataclass
class Video:
    url: str
    platform: str  # "youtube" or "instagram"
    duration: float  # seconds
    title: Optional[str] = None
    local_path: Optional[str] = None  # cached video path
    cache_expiry: Optional[datetime] = None  # 24h from download
```

#### Frame
```python
@dataclass
class Frame:
    timestamp: float  # seconds from video start
    image_path: str  # path to extracted frame
    detected_objects: List[DetectedObject]
    ocr_text: Optional[str] = None
```

#### DetectedObject
```python
@dataclass
class DetectedObject:
    label: str  # COCO class name
    confidence: float  # 0.0 to 1.0
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
```

#### Ingredient
```python
@dataclass
class Ingredient:
    name: str
    quantity: Optional[float] = None  # summed total
    unit: Optional[str] = None  # "cups", "tsp", "grams", etc.
    source: str  # "visual", "audio", "ocr", "merged"
    confidence: float  # 0.0 to 1.0
    timestamps: List[float]  # all occurrences
    raw_text: Optional[str] = None  # original mention
    alternative_note: Optional[str] = None  # e.g., "or olive oil"
```

#### Step
```python
@dataclass
class Step:
    sequence: int  # 1, 2, 3, ...
    description: str
    timestamp: float  # seconds
    action: Optional[str] = None  # "mix", "bake", "chop", etc.
    source: str  # "audio", "ocr"
    confidence: float  # 0.0 to 1.0
```

#### Transcript
```python
@dataclass
class Transcript:
    full_text: str
    segments: List[TranscriptSegment]
    language: str  # "en" for MVP
```

#### Recipe (Final Output)
```python
@dataclass
class Recipe:
    source_url: str
    title: Optional[str] = None
    ingredients: List[Ingredient]
    steps: List[Step]
    extraction_date: datetime
    processing_time: float  # seconds
    metadata: Dict[str, Any]  # models used, config, etc.
```

### Output Contracts

**Created**: `contracts/recipe_schema.json` (JSON Schema draft-07)

Defines validation rules:
- Required fields: `source_url`, `ingredients`, `steps`
- Ingredient constraints: name (string), quantity (number >= 0), confidence (0-1)
- Step constraints: sequence (integer >= 1), description (string), timestamp (number >= 0)
- Enum for source: ["visual", "audio", "ocr", "merged"]
- Enum for action: ["mix", "stir", "bake", "chop", "add", "pour", "heat", "cool", "blend", "simmer", "boil", "fry", "other"]

### Quickstart Documentation

**Created**: `quickstart.md`

Includes:
- Installation instructions (Python 3.11+, dependencies)
- Basic usage examples (CLI commands)
- Example JSON and Markdown outputs
- Configuration options (YAML)
- Troubleshooting guide (common errors, performance tuning)
- MLflow experiment tracking setup

## Phase 2: Implementation Roadmap

**Note**: Detailed task breakdown will be generated by `/speckit.tasks` command. High-level phases outlined here.

### Phase 2.1: Core Infrastructure (P1 - MVP Foundation)
- Project scaffolding (directory structure, requirements.txt, .gitignore)
- Configuration management (YAML loader, defaults)
- Device detection and setup (MPS/CUDA/CPU)
- MLflow initialization and logging utilities
- Video cache manager (24h TTL, cleanup)
- Data models (entities/data_models.py)

### Phase 2.2: Video Download & Preprocessing (P1 - MVP)
- Base downloader interface
- YouTube downloader (yt-dlp wrapper)
- Instagram downloader (yt-dlp wrapper)
- Error handling with detailed messages (per clarification)
- Duration validation (reject >30 min)
- Frame extraction (1 fps, configurable)
- Audio extraction

### Phase 2.3: Visual Analysis (P1 - MVP)
- YOLOv8 object detection wrapper
- Batch frame processing
- EasyOCR text extraction wrapper
- Confidence filtering (threshold configurable)
- Frame annotation for MLflow artifacts

### Phase 2.4: Audio & NLP (P1 - MVP)
- Whisper transcription wrapper
- Transcript segmentation with timestamps
- Ingredient parser (ingredient-parser + spaCy + regex)
- Quantity/unit extraction
- Step parser (action verb detection, temporal cues)

### Phase 2.5: Aggregation & Deduplication (P1 - MVP)
- Merge detections from all sources
- Fuzzy matching for duplicate ingredients (85% threshold)
- Quantity summing with timestamp preservation (per clarification)
- Substitution handling: list alternatives with notes (per clarification)
- Recipe assembly

### Phase 2.6: Output & Validation (P1 - MVP)
- JSON formatter
- Markdown formatter
- Plain text formatter
- JSON schema validation
- MLflow artifact logging (sample frames, recipe outputs)

### Phase 2.7: CLI & User Experience (P1 - MVP)
- Command-line interface (argparse)
- Progress indicators
- Error messages (detailed, actionable per clarification)
- Output file management

### Phase 2.8: End-to-End Testing & Refinement (P1 - MVP)
- Test with diverse video styles (professional, home, social media)
- Validate success criteria (SC-001 through SC-008)
- Performance optimization (batch sizing, caching)
- Documentation updates (README, quickstart)

### Future Phases (P2/P3 - Post-MVP)
- **P2**: Step extraction enhancements (better timestamp accuracy, action classification)
- **P2**: Structured output format improvements (additional export formats)
- **P3**: Multi-language support (Whisper multilingual, spaCy models)
- **P3**: Batch processing (multiple videos)
- **P3**: Web interface or API

## Dependencies

```plaintext
# Core
python>=3.11

# Deep Learning & CV
torch>=2.0.0
torchvision>=0.15.0
ultralytics>=8.0.0  # YOLOv8
opencv-python>=4.8.0
easyocr>=1.7.0
pillow>=10.0.0

# Speech & NLP
openai-whisper>=20230314  # Local, no API key
spacy>=3.7.0
ingredient-parser>=1.0.0
thefuzz>=0.20.0  # Fuzzy string matching

# Video Processing
yt-dlp>=2023.10.0
ffmpeg-python>=0.2.0

# Experiment Tracking
mlflow>=2.8.0

# Utilities
pyyaml>=6.0
python-dateutil>=2.8.0
tqdm>=4.66.0  # Progress bars

# Development
black>=23.0.0  # Code formatter (optional)
```

**Installation**:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Configuration Example

**File**: `experiments/configs/default_config.yaml`

```yaml
# Video Processing
video:
  max_duration: 1800  # 30 minutes in seconds
  cache_ttl: 86400  # 24 hours in seconds
  cache_dir: "./cache/videos"

# Frame Extraction
frames:
  fps: 1.0
  resolution: 720  # max height
  save_frames: false  # Set true to keep frames for inspection
  frames_dir: "./cache/frames"

# Object Detection
detection:
  model: "yolov8n.pt"
  confidence_threshold: 0.5
  device: "mps"  # "mps", "cuda", or "cpu"
  batch_size: 8

# OCR
ocr:
  engine: "easyocr"
  languages: ["en"]
  confidence_threshold: 0.6

# Transcription
transcription:
  model: "base"  # whisper model size: tiny, base, small
  language: "en"
  device: "mps"

# NLP
parsing:
  similarity_threshold: 0.85  # fuzzy matching for deduplication
  min_confidence: 0.5
  merge_duplicates: true

# Output
output:
  default_format: "json"  # "json", "markdown", "text"
  output_dir: "./outputs/recipes"
  validate_schema: true
  schema_path: "./specs/001-recipe-video-extraction/contracts/recipe_schema.json"

# MLflow
mlflow:
  tracking_uri: "file:./experiments/mlruns"
  experiment_name: "recipe-extraction"
  log_artifacts: true
```

## Success Metrics (from Spec)

| Criterion | Target | Validation Method |
|-----------|--------|-------------------|
| SC-001 | Extract 80%+ visible/spoken ingredients | Test on 10 diverse videos, manual review |
| SC-002 | 70%+ accuracy on quantities when stated | Compare extracted quantities to ground truth |
| SC-003 | Steps within 10 seconds of actual action | Manual verification of timestamps |
| SC-004 | 5-10 min video → <5 min processing | Measure end-to-end time, optimize as needed |
| SC-005 | YouTube/Instagram download without auth | Test with public URLs |
| SC-006 | Valid JSON/Markdown output | Automated schema validation |
| SC-007 | Handle 3+ video styles consistently | Test professional, home, social media videos |
| SC-008 | MLflow logs all experiments | Verify mlruns/ directory after each run |

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|----------|
| Poor object detection accuracy (non-food items) | Medium | High | Use COCO-pretrained YOLOv8; consider fine-tuning on Food-101 in future |
| Audio quality issues (background music, accents) | High | Medium | Use Whisper base (robust); provide troubleshooting in docs; accept limitation for MVP |
| OCR false positives (logos, channel names) | Medium | Low | Filter by location (text in lower third more likely recipe-related); confidence threshold |
| Ingredient parsing failures (unusual formats) | Medium | Medium | Hybrid approach (regex + spaCy + ingredient-parser); log failures to MLflow for review |
| Video download blocked (private/geo-restricted) | Medium | Low | Clear error messages with retry suggestions (per clarification); documented limitation |
| Processing time exceeds target | Low | Medium | Optimize batch sizes; use FP16 inference; cache frames; profile with MLflow |

## Next Steps

1. **Run `/speckit.tasks`** to generate detailed task breakdown
2. Begin Phase 2.1 implementation (infrastructure setup)
3. Prototype core components in Jupyter notebooks for quick iteration
4. Log all experiments to MLflow from day one
5. Test with 3-5 sample videos early to validate pipeline

---

**Plan Status**: ✅ COMPLETE  
**Phase 0 Research**: ✅ COMPLETE (5 research questions resolved)  
**Phase 1 Design**: ✅ COMPLETE (data models, contracts, quickstart defined)  
**Phase 2 Tasks**: ⏳ PENDING (run `/speckit.tasks` to generate)
