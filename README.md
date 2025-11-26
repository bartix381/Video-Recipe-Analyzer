# Video Recipe Analyzer

A computer vision and NLP system that extracts structured recipe data (ingredients with quantities, cooking steps with timestamps) from YouTube and Instagram recipe videos. All processing runs locally using free, open-source models.

## Features

- 🎥 **Multi-Platform Support**: Download and process videos from YouTube and Instagram
- 🔍 **Computer Vision**: YOLOv8 object detection for identifying visible ingredients
- 📝 **OCR**: EasyOCR for extracting on-screen text (ingredient lists, measurements)
- 🎤 **Speech-to-Text**: Whisper for transcribing audio instructions
- 🧮 **Smart Parsing**: Extract quantities, units, and ingredient names
- 🔄 **Intelligent Merging**: Deduplicate ingredients with fuzzy matching
- 📊 **Experiment Tracking**: Full MLflow integration for reproducibility
- 🚀 **GPU Acceleration**: Supports CUDA, Apple Metal (MPS), and CPU

## Installation

### Prerequisites

- Python 3.11 or higher
- ffmpeg (for audio extraction)

```bash
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

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Download spaCy language model (optional, for NLP)
python -m spacy download en_core_web_sm
```

## Quick Start

### Extract Recipe from YouTube

```bash
python -m src extract "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Extract Recipe from Instagram

```bash
python -m src extract "https://www.instagram.com/p/POST_ID/"
```

### Specify Output Format

```bash
# JSON output (default)
python -m src extract "VIDEO_URL" --output recipe.json --format json

# Markdown output (coming in Phase 4)
# python -m src extract "VIDEO_URL" --output recipe.md --format markdown

# Plain text output (coming in Phase 4)
# python -m src extract "VIDEO_URL" --output recipe.txt --format text
```

### Custom Configuration

```bash
# Use custom config file
python -m src extract "VIDEO_URL" --config experiments/configs/custom_config.yaml

# Override specific parameters
python -m src extract "VIDEO_URL" --fps 2 --whisper-model small --detector yolov8m
```

## CLI Commands

### Extract Recipe

```bash
python -m src extract <url> [OPTIONS]
```

**Options:**
- `--output, -o`: Output file path (default: recipe.json)
- `--format, -f`: Output format (json/markdown/text)
- `--config, -c`: Path to custom config file
- `--fps`: Frame extraction rate (overrides config)
- `--whisper-model`: Whisper model size (tiny/base/small/medium/large)
- `--detector`: YOLO model (yolov8n/yolov8s/yolov8m/yolov8l/yolov8x)

### View Configuration

```bash
python -m src show-config [--config PATH]
```

### Cache Management

```bash
# Show cache statistics
python -m src cache-info

# Clear cache
python -m src cache-clear
```

### Device Information

```bash
# Check available compute devices
python -m src device-info
```

## Example Output

```json
{
  "title": "Simple Chocolate Chip Cookies",
  "source_url": "https://www.youtube.com/watch?v=example",
  "ingredients": [
    {
      "name": "flour",
      "quantity": 2.0,
      "unit": "cup",
      "source": "audio",
      "confidence": 0.95,
      "timestamps": [12.5, 45.2],
      "raw_text": "two cups of flour",
      "alternative_note": null
    },
    {
      "name": "butter",
      "quantity": 1.0,
      "unit": "cup",
      "source": "ocr",
      "confidence": 0.88,
      "timestamps": [15.2],
      "raw_text": "1 cup butter",
      "alternative_note": "or olive oil"
    }
  ],
  "steps": [],
  "extraction_date": "2025-11-26T10:30:00",
  "processing_time": 45.3,
  "metadata": {
    "models_used": {
      "object_detection": "yolov8n.pt",
      "ocr": "easyocr",
      "transcription": "base"
    },
    "config": {
      "fps": 1.0,
      "yolo_conf": 0.25
    }
  }
}
```

## Configuration

The system uses YAML configuration files. Default config: `experiments/configs/default_config.yaml`

Key settings:
- **Video**: Max duration (30 min), cache TTL (24h), download timeout
- **Frame Extraction**: FPS (1.0), format (jpg), quality (95)
- **Object Detection**: Model (yolov8n.pt), confidence threshold (0.25)
- **OCR**: Languages (en), confidence threshold (0.4)
- **Transcription**: Model (base), language (auto-detect)
- **MLflow**: Experiment tracking enabled by default

## Project Structure

```
Video-Recipe-Analyzer/
├── src/
│   ├── cli.py                    # Command-line interface
│   ├── pipeline.py               # Main processing pipeline
│   ├── entities/
│   │   └── data_models.py        # Data classes (Video, Frame, Ingredient, etc.)
│   ├── downloaders/
│   │   ├── base.py               # Abstract downloader
│   │   ├── youtube.py            # YouTube downloader
│   │   └── instagram.py          # Instagram downloader
│   ├── extractors/
│   │   ├── frame_extractor.py    # Frame extraction
│   │   └── audio_extractor.py    # Audio extraction
│   ├── models/
│   │   ├── object_detector.py    # YOLOv8 wrapper
│   │   ├── ocr_engine.py         # EasyOCR wrapper
│   │   └── transcriber.py        # Whisper wrapper
│   ├── parsers/
│   │   ├── quantity_parser.py    # Quantity/unit parsing
│   │   └── ingredient_parser.py  # Ingredient name parsing
│   └── utils/
│       ├── config.py             # Configuration management
│       ├── device.py             # Device detection
│       ├── cache.py              # Video caching
│       ├── mlflow_utils.py       # MLflow tracking
│       └── validators.py         # JSON schema validation
├── experiments/
│   └── configs/
│       └── default_config.yaml   # Default configuration
├── specs/                        # Feature specifications
├── cache/                        # Downloaded videos (auto-cleaned)
└── outputs/                      # Extracted frames and audio

```

## Roadmap

### Phase 1: Setup & Infrastructure ✅
- Project structure, dependencies, configuration
- Core utilities (device detection, config, MLflow, cache)

### Phase 2: Foundational Prerequisites ✅
- Data models, downloaders, extractors
- ML model wrappers (YOLO, OCR, Whisper)

### Phase 3: MVP - Ingredient Extraction ✅ (Current)
- Object detection, OCR, transcription
- Ingredient parsing and aggregation
- JSON output with MLflow tracking

### Phase 4: Structured Output Formats (Next)
- Markdown formatter
- Plain text formatter
- Schema validation

### Phase 5: Step Extraction
- Action verb detection
- Step parsing from audio and OCR
- Sequential step ordering with timestamps

### Phase 6: Multi-Language Support
- Support for Spanish, French, Italian videos
- Translation capabilities

## Constitution Compliance

This project follows a strict **zero-cost mandate**:
- ✅ All models are free and open-source (YOLOv8, EasyOCR, Whisper)
- ✅ No API keys or cloud services required
- ✅ Local processing on Mac Metal (MPS), CUDA, or CPU
- ✅ Full MLflow experiment tracking for reproducibility
- ✅ No formal tests (personal research project)

## Performance

Typical processing times (5-10 minute video on Mac M4 Max):
- Download: 10-30 seconds (cached after first run)
- Frame extraction (1 fps): 5-10 seconds
- Object detection: 20-40 seconds
- OCR: 30-60 seconds
- Audio transcription: 60-120 seconds
- **Total**: ~2-5 minutes

## Limitations

- Maximum video duration: 30 minutes
- Cache TTL: 24 hours
- English language optimized (multi-language in Phase 6)
- Ingredient detection depends on visual clarity and audio quality
- Step extraction coming in Phase 5

## Troubleshooting

### Import Errors
```bash
# Make sure all dependencies are installed
pip install -r requirements.txt

# For Apple Silicon Macs, ensure PyTorch with MPS support
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### FFmpeg Not Found
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg
```

### CUDA/MPS Not Detected
```bash
# Check available devices
python -m src device-info

# Force CPU usage if needed
python -m src extract "URL" --config experiments/configs/cpu_config.yaml
```

## Contributing

This is a personal research project following the specifications in `specs/001-recipe-video-extraction/`. 

## License

[Specify your license here]

## Acknowledgments

- **YOLOv8** by Ultralytics
- **EasyOCR** by JaidedAI
- **Whisper** by OpenAI
- **MLflow** for experiment tracking

