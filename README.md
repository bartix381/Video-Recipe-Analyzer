# Video Recipe Analyzer

A computer vision and NLP system that extracts structured recipe data (ingredients with quantities, cooking steps with timestamps) from YouTube and Instagram recipe videos. Combines multiple AI models for comprehensive ingredient detection from both visual and audio sources.

## Features

- 🎥 **Multi-Platform Support**: Download and process videos from YouTube and Instagram
- 🥕 **Ingredient Detection**: Roboflow API for accurate raw ingredient recognition (31 classes: tomato, onion, garlic, etc.)
- 📝 **OCR**: EasyOCR for extracting on-screen text (ingredient lists, measurements)
- 🎤 **Speech-to-Text**: Whisper for transcribing audio narration with ingredient mentions
- 🧮 **Smart Parsing**: Extract quantities, units, and ingredient names
- 🔄 **Intelligent Merging**: Deduplicate ingredients from multiple sources (visual + audio + OCR)
- 📊 **Experiment Tracking**: Full MLflow integration for reproducibility
- 🚀 **GPU Acceleration**: Supports CUDA, Apple Metal (MPS), and CPU
- 📁 **Smart Output Management**: All outputs organized in `outputs/` directory

## Installation

### Prerequisites

- Python 3.11 or higher (tested on 3.13)
- ffmpeg (for audio extraction)
- UV package manager (recommended) or pip

```bash
# Install UV (recommended - faster, better dependency resolution)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or use pip
python -m pip install --upgrade pip

# Install ffmpeg (macOS)
brew install ffmpeg

# Install ffmpeg (Ubuntu/Debian)
sudo apt-get install ffmpeg

# Install ffmpeg (Windows)
# Download from https://ffmpeg.org/download.html
```

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/Video-Recipe-Analyzer.git
cd Video-Recipe-Analyzer

# Install dependencies with UV (recommended)
uv sync

# Or with pip
python3.11 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

### Environment Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Add your Roboflow API key to `.env`:
   ```bash
   ROBOFLOW_API_KEY=your_api_key_here
   ```

### Roboflow API Key (Required for Ingredient Detection)

For accurate **raw ingredient detection** (tomato, onion, garlic, carrot, etc.), you need a free Roboflow account:

1. **Sign up** at https://app.roboflow.com/ (100% free!)
2. **Get API key** from https://app.roboflow.com/settings/api
3. **Add to `.env` file**:
   ```bash
   ROBOFLOW_API_KEY=your_api_key_here
   ```

**What you get:**
- ✅ **31 ingredient classes**: bell_pepper, broccoli, carrot, chili_pepper, corn, cucumber, eggplant, fish, garlic, ginger, lemon, lime, mushroom, okra, onion, potato, pumpkin, spinach, tomato, turmeric, and more
- ✅ **9,272 training images** with high accuracy
- ✅ **1,000 free predictions/month** (enough for 10-15 recipe videos)
- ✅ **Trained specifically for cooking ingredients** (unlike Food-101 which detects finished dishes)

**Why Roboflow?** 
The project previously used Food-101, but it detects finished dishes (apple_pie, pizza, sushi) rather than raw ingredients. Roboflow's specialized ingredient detection model is perfect for recipe extraction. See [docs/ingredient-detection-switch.md](docs/ingredient-detection-switch.md) for the full comparison.

**Fallback**: If no API key is provided, the system falls back to YOLOv8n general object detection (limited ingredient recognition).

## Quick Start

### Basic Usage

Extract a recipe from YouTube (outputs to `outputs/recipes/recipe.json`):

```bash
python -m src.cli extract "https://www.youtube.com/watch?v=VIDEO_ID"
```

Extract from Instagram:

```bash
python -m src.cli extract "https://www.instagram.com/p/POST_ID/"
```

Specify custom output filename (auto-saves to `outputs/recipes/`):

```bash
python -m src.cli extract "VIDEO_URL" --output my_recipe.json
```

### Output Formats

```bash
# JSON output (default) - structured data for processing
python -m src.cli extract "VIDEO_URL" --output recipe.json --format json

# Markdown output (coming in Phase 4)
# python -m src.cli extract "VIDEO_URL" --output recipe.md --format markdown

# Plain text output (coming in Phase 4)
# python -m src.cli extract "VIDEO_URL" --output recipe.txt --format text
```

### Advanced Usage

```bash
# Use custom config file
python -m src.cli extract "VIDEO_URL" --config experiments/configs/custom_config.yaml

# Override specific parameters
python -m src.cli extract "VIDEO_URL" --fps 2 --whisper-model small

# Specify full output path (relative to project root)
python -m src.cli extract "VIDEO_URL" --output outputs/recipes/special/my_recipe.json
```

## CLI Commands

### Extract Recipe

```bash
python -m src.cli extract <url> [OPTIONS]
```

**Options:**
- `--output, -o`: Output filename (default: `recipe.json`, auto-saves to `outputs/recipes/`)
- `--format, -f`: Output format (`json`/`markdown`/`text`)
- `--config, -c`: Path to custom config file
- `--fps`: Frame extraction rate (overrides config)
- `--whisper-model`: Whisper model size (`tiny`/`base`/`small`/`medium`/`large`)

**Examples:**
```bash
# Basic extraction (saves to outputs/recipes/recipe.json)
python -m src.cli extract "https://youtube.com/..."

# Custom filename (saves to outputs/recipes/my_recipe.json)
python -m src.cli extract "https://youtube.com/..." --output my_recipe.json

# Custom path (relative to project root)
python -m src.cli extract "https://youtube.com/..." --output data/recipes/test.json

# Higher quality settings
python -m src.cli extract "https://youtube.com/..." --fps 2 --whisper-model small
```

### View Configuration

```bash
python -m src.cli show-config [--config PATH]
```

### Cache Management

```bash
# Show cache statistics
python -m src.cli cache-info

# Clear expired cache
python -m src.cli cache-clear
```

### Device Information

```bash
# Check available compute devices (CUDA/MPS/CPU)
python -m src.cli device-info
```

## Example Output

```json
{
  "title": "Simple Chocolate Chip Cookies",
  "source_url": "https://www.youtube.com/watch?v=example",
  "ingredients": [
    {
      "name": "butter",
      "quantity": 1.0,
      "unit": "cup",
      "source": "merged",
      "confidence": 0.92,
      "timestamps": [12.5, 45.2],
      "raw_text": "1 cup butter",
      "alternative_note": null
    },
    {
      "name": "flour",
      "quantity": 2.0,
      "unit": "cup",
      "source": "audio",
      "confidence": 0.95,
      "timestamps": [15.8],
      "raw_text": "two cups of all-purpose flour",
      "alternative_note": null
    },
    {
      "name": "chocolate_chips",
      "quantity": 1.5,
      "unit": "cup",
      "source": "visual",
      "confidence": 0.88,
      "timestamps": [34.2, 56.1],
      "raw_text": null,
      "alternative_note": null
    }
  ],
  "steps": [],
  "extraction_date": "2025-11-27T12:00:00",
  "processing_time": 38.5,
  "metadata": {
    "models_used": {
      "ingredient_detection": "roboflow:ingredients-mqhxf/v1",
      "ocr": "easyocr",
      "transcription": "whisper-base"
    },
    "video_info": {
      "duration": 120.5,
      "fps": 30.0,
      "frames_analyzed": 121
    },
    "detection_stats": {
      "total_detections": 145,
      "unique_ingredients": 8,
      "sources": {
        "visual": 3,
        "audio": 2,
        "merged": 3
      }
    }
  }
}
```

**Ingredient Sources:**
- `visual`: Detected by Roboflow computer vision (raw ingredients in video frames)
- `audio`: Extracted from Whisper speech transcription
- `merged`: Combined from multiple sources (visual + audio, or visual + OCR)
- `ocr`: Extracted from on-screen text
- `metadata`: Derived from video title/description

## Configuration

The system uses YAML configuration files for pipeline settings.

**Default config**: `experiments/configs/default_config.yaml`

### Key Configuration Sections

```yaml
# Video settings
video:
  max_duration: 1800        # 30 minutes max
  cache_ttl: 86400          # 24 hours
  download_timeout: 120     # 2 minutes

# Frame extraction
frame_extraction:
  fps: 1.0                  # 1 frame per second
  format: "jpg"             # Image format
  quality: 95               # JPEG quality

# Ingredient detection (Roboflow)
ingredient_detection:
  model: "roboflow"         # or "yolov8n" for fallback
  confidence: 0.4           # Detection threshold
  overlap: 0.3              # NMS overlap threshold

# OCR settings
ocr:
  languages: ["en"]         # Supported languages
  confidence: 0.4           # Text confidence threshold

# Audio transcription
transcription:
  model: "base"             # Whisper model size
  language: null            # Auto-detect
  device: "cpu"             # Force CPU for Whisper (MPS has NaN issues)

# MLflow tracking
mlflow:
  tracking_uri: "./experiments/mlruns"
  experiment_name: "recipe-video-extraction"
  enabled: true
```

### Override Configuration

```bash
# Use custom config file
python -m src.cli extract "URL" --config my_config.yaml

# Override individual parameters
python -m src.cli extract "URL" --fps 2 --whisper-model small
```

## Project Structure

```
Video-Recipe-Analyzer/
├── src/
│   ├── cli.py                    # Command-line interface with Click
│   ├── pipeline/
│   │   └── recipe_pipeline.py    # Main extraction pipeline orchestration
│   ├── entities/
│   │   └── data_models.py        # Pydantic data classes
│   ├── downloaders/
│   │   ├── base.py               # YouTube/Instagram video downloaders
│   │   └── ...
│   ├── extractors/
│   │   ├── frame_extractor.py    # Video frame extraction (OpenCV)
│   │   └── audio_extractor.py    # Audio extraction (FFmpeg)
│   ├── models/
│   │   ├── roboflow_detector.py  # Roboflow ingredient detection API
│   │   ├── object_detector.py    # YOLOv8 fallback detector
│   │   ├── ocr_engine.py         # EasyOCR text extraction
│   │   └── transcriber.py        # Whisper speech-to-text
│   ├── parsers/
│   │   ├── quantity_parser.py    # Quantity/unit extraction & normalization
│   │   └── ingredient_parser.py  # Ingredient name parsing & deduplication
│   └── utils/
│       ├── config.py             # YAML configuration management
│       ├── device.py             # GPU/CPU device detection
│       ├── cache.py              # Video file caching with TTL
│       ├── mlflow_utils.py       # MLflow experiment tracking
│       └── validators.py         # JSON schema validation
├── experiments/
│   ├── configs/
│   │   └── default_config.yaml   # Default pipeline configuration
│   └── mlruns/                   # MLflow tracking data (gitignored)
├── specs/                        # Technical specifications & planning docs
├── docs/                         # Additional documentation
├── cache/                        # Downloaded videos (auto-cleaned, gitignored)
├── outputs/
│   ├── recipes/                  # Extracted recipe JSON files
│   ├── frames/                   # Temporary video frames (gitignored)
│   └── audio/                    # Temporary audio files (gitignored)
├── .env                          # Environment variables (gitignored)
├── .env.example                  # Environment template
├── pyproject.toml                # UV project configuration
└── requirements.txt              # Python dependencies
```

**Key Directories:**
- **`outputs/recipes/`**: All extracted recipes save here by default
- **`cache/`**: Video cache (24h TTL, auto-cleanup)
- **`experiments/mlruns/`**: MLflow tracking data for reproducibility
- **Path resolution**: All paths resolve relative to project root, regardless of where commands are run

## Roadmap

### ✅ Phase 1: Setup & Infrastructure (Complete)
- Project structure with UV package manager
- Configuration management (YAML)
- Device detection (CUDA/MPS/CPU)
- Video caching with TTL
- MLflow experiment tracking

### ✅ Phase 2: Foundational Prerequisites (Complete)
- Pydantic data models
- YouTube/Instagram downloaders
- Frame & audio extractors
- Model wrappers (Roboflow, YOLOv8, EasyOCR, Whisper)

### ✅ Phase 3: MVP - Ingredient Extraction (Complete) ✨
- **Roboflow ingredient detection** (31 classes, 9K+ training images)
- **Multi-source extraction**: Visual + Audio + OCR
- **Intelligent merging**: Fuzzy matching with confidence scoring
- **Quantity parsing**: Extract measurements from text
- **JSON output** with full metadata
- **Path management**: All outputs organized in `outputs/` directory
- **Whisper MPS fix**: Force CPU to avoid NaN errors

**Current Status**: Fully functional MVP! Tested with multiple recipe videos. Audio extraction, visual detection, and source merging all working.

### 🚧 Phase 4: Structured Output Formats (In Progress)
- [ ] Markdown formatter (recipe card style)
- [ ] Plain text formatter (human-readable)
- [ ] Schema validation for all formats

### 📋 Phase 5: Step Extraction (Planned)
- [ ] Action verb detection from transcripts
- [ ] Step parsing with temporal ordering
- [ ] Step-ingredient linking
- [ ] Timestamp association

### 🌍 Phase 6: Multi-Language Support (Future)
- [ ] Spanish, French, Italian language support
- [ ] Multi-language Whisper models
- [ ] Translation capabilities

## Technical Details

### Architecture

The system uses a **multi-source extraction pipeline**:

1. **Video Download**: YouTube/Instagram downloaders with caching
2. **Frame Extraction**: OpenCV extracts frames at configurable FPS
3. **Audio Extraction**: FFmpeg extracts audio track for transcription
4. **Parallel Processing**:
   - **Visual**: Roboflow API detects ingredients in frames
   - **OCR**: EasyOCR extracts on-screen text
   - **Audio**: Whisper transcribes narration
5. **Intelligent Aggregation**: Fuzzy matching merges ingredients from all sources
6. **Output**: Structured JSON with metadata and MLflow tracking

### Models Used

| Component | Model | Purpose |
|-----------|-------|---------|
| Ingredient Detection | Roboflow `ingredients-mqhxf/v1` | 31 raw ingredient classes |
| Fallback Detection | YOLOv8n | General object detection |
| OCR | EasyOCR | On-screen text extraction |
| Transcription | Whisper base (CPU) | Speech-to-text |

### Device Support

- **Apple Metal (MPS)**: EasyOCR, YOLOv8 fallback
- **CUDA**: Full GPU acceleration on NVIDIA GPUs
- **CPU**: Whisper forced to CPU (MPS has NaN issues), fallback for all models

### Performance Benchmarks

Tested on Mac M4 Max with 20-second video:

| Stage | Time | Notes |
|-------|------|-------|
| Download | ~15s | Cached after first run |
| Frame Extraction | 1-2s | 1 FPS, 21 frames |
| Roboflow Detection | 20-25s | API calls (21 frames) |
| EasyOCR | 4-5s | MPS acceleration |
| Whisper Transcription | 3-4s | CPU (forced) |
| **Total** | **~35-40s** | First run (uncached) |
| **Cached** | **~30s** | Subsequent runs |

Longer videos (5-10 min) typically take 2-5 minutes total.

## Limitations & Known Issues

- **Maximum video duration**: 30 minutes (configurable)
- **Cache TTL**: 24 hours (configurable)
- **Language support**: English optimized (multi-language in Phase 6)
- **Roboflow API**: 1,000 free predictions/month (~10-15 videos)
- **Whisper MPS**: Forced to CPU due to NaN errors on Apple Silicon
- **Step extraction**: Coming in Phase 5
- **Ingredient accuracy**: Depends on video quality, lighting, and audio clarity

### Troubleshooting

**ImportError / ModuleNotFoundError**
```bash
# Reinstall dependencies
uv sync
# Or with pip
pip install -r requirements.txt
```

**FFmpeg not found**
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Verify installation
ffmpeg -version
```

**Roboflow API errors**
```bash
# Check your API key in .env
cat .env | grep ROBOFLOW

# Test API key
python -c "from roboflow import Roboflow; rf = Roboflow(api_key='YOUR_KEY'); print('✓ API key valid')"

# If invalid, get new key from https://app.roboflow.com/settings/api
```

**CUDA/MPS not detected**
```bash
# Check available devices
python -m src.cli device-info

# System will automatically fall back to CPU if GPU unavailable
```

**Whisper NaN errors on Apple Silicon**
```bash
# Already fixed! Whisper forced to CPU in default config
# If you see NaN errors, ensure config has:
#   transcription:
#     device: "cpu"
```

**Output files in wrong location**
```bash
# Ensure you're using relative paths or just filenames
python -m src.cli extract "URL" --output my_recipe.json  # ✓ Goes to outputs/recipes/
python -m src.cli extract "URL" --output /abs/path.json  # ✓ Uses absolute path
```

## Documentation

- **[Ingredient Detection Switch](docs/ingredient-detection-switch.md)**: Why we switched from Food-101 to Roboflow
- **[Roboflow Setup Guide](docs/roboflow-setup.md)**: Detailed API setup and usage
- **[Technical Specifications](specs/001-recipe-video-extraction/)**: Complete system design docs

## Contributing

This is a personal research project following the specifications in `specs/001-recipe-video-extraction/`. 

Feel free to:
- Report bugs via GitHub issues
- Suggest features or improvements
- Share test videos or results

**Note**: This is a research project without formal tests. All validation is done through MLflow experiment tracking.

## License

MIT License - See LICENSE file for details

## Acknowledgments

- **[Roboflow](https://roboflow.com/)** - Ingredient detection model (31 classes, 9,272 images)
- **[YOLOv8](https://github.com/ultralytics/ultralytics)** by Ultralytics - Fallback object detection
- **[EasyOCR](https://github.com/JaidedAI/EasyOCR)** by JaidedAI - Text extraction
- **[Whisper](https://github.com/openai/whisper)** by OpenAI - Speech transcription
- **[MLflow](https://mlflow.org/)** - Experiment tracking and reproducibility
- **[UV](https://github.com/astral-sh/uv)** by Astral - Fast Python package management

## Citation

If you use this project in your research, please cite:

```bibtex
@software{video_recipe_analyzer,
  title = {Video Recipe Analyzer: Multi-Source Ingredient Extraction from Recipe Videos},
  author = {Your Name},
  year = {2025},
  url = {https://github.com/yourusername/Video-Recipe-Analyzer}
}
```

---

**Status**: Phase 3 MVP Complete ✅ | **Next**: Phase 4 - Structured Output Formats 🚧