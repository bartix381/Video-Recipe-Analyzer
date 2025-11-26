# Research: Recipe Video Extraction

## Model Selection

### Object Detection: YOLOv8n
- **Rationale**: Fast inference, good for real-time needs, runs well on Mac Metal
- **Source**: Ultralytics (free, open source)
- **Alternative**: DETR from HuggingFace if food detection inadequate

### OCR: EasyOCR
- **Rationale**: Supports multiple languages, good accuracy, pure Python
- **Source**: JaidedAI (free, open source)
- **Alternative**: Tesseract if performance issues

### Speech-to-Text: Whisper base
- **Rationale**: Excellent accuracy, handles noisy audio, runs locally
- **Source**: OpenAI (open source, no API key)
- **Alternative**: Whisper small for better accuracy, Vosk for lightweight

### NLP: spaCy + ingredient-parser
- **Rationale**: Fast, accurate entity recognition; ingredient-parser handles quantities
- **Source**: Explosion AI + open source community
- **Alternative**: HuggingFace BERT for complex cases

## Configuration Decisions

### Frame Sampling: 1 fps
- Captures multiple frames per ingredient (shown 2-5 sec typically)
- Balances coverage and processing time
- Configurable parameter

### Quantity Parsing: Regex + spaCy + ingredient-parser
- Regex for simple patterns (e.g., "2 cups", "1/2 tsp")
- spaCy for context and entity recognition
- ingredient-parser for structured parsing

### Audio Processing: Whisper base + volume normalization
- Handles moderate background noise well
- Basic preprocessing for very noisy videos
- Upgrade to Whisper small if accuracy issues

### Deduplication: Fuzzy matching (85% threshold)
- Merge similar ingredient names (e.g., "flour" variants)
- Confidence-weighted aggregation
- Source provenance tracking for debugging

## Performance Expectations

- YOLOv8n: ~50-100 fps on Mac M4 Max (Metal)
- Whisper base: ~10x realtime (10 min audio → 1 min processing)
- EasyOCR: ~1-2 sec per frame
- Overall: 5-10 min video → <5 min processing time (achievable)

## Research Questions Resolved

### 1. Best Food Detection Model
**Decision**: YOLOv8n (Ultralytics)
- Lightweight and fast
- Good balance of accuracy and speed
- Excellent Mac Metal/MPS support
- Can upgrade to YOLOv8m if needed

### 2. Frame Sampling Rate
**Decision**: 1 fps (configurable)
- Recipe videos typically show ingredients for 2-5 seconds
- 1 fps captures 2-5 frames per ingredient
- Higher fps increases processing time without significant benefit

### 3. Ingredient Parsing Strategy
**Decision**: Multi-layered approach
- **Regex**: Handle simple patterns (numbers, fractions, units)
- **spaCy**: Named entity recognition for ingredient names
- **ingredient-parser**: Specialized library for recipe parsing
- **Fuzzy matching**: Deduplicate similar ingredients (85% threshold)

### 4. Audio Quality Handling
**Decision**: Whisper base with preprocessing
- Whisper robust to moderate background noise
- Add volume normalization for very quiet videos
- Upgrade to Whisper small if base accuracy insufficient

### 5. Multi-Source Deduplication
**Decision**: Confidence-weighted fuzzy matching
- Visual detection: High confidence (direct observation)
- OCR: Medium confidence (depends on text clarity)
- Audio: Variable confidence (depends on transcription quality)
- Merge ingredients with >85% name similarity
- Aggregate quantities when merging

## Technology Stack Justification

All choices align with constitution requirements:
- ✅ Zero-cost: All models free and open source
- ✅ Local processing: No cloud APIs
- ✅ No API keys: Everything runs offline
- ✅ Mac optimized: Metal/MPS support where available
- ✅ Simple: Clear, maintainable implementations

## Implementation Notes

### Model Loading Strategy
- Load models lazily (only when needed)
- Cache model instances to avoid reloading
- Use appropriate device (mps > cuda > cpu)

### Error Handling
- Graceful degradation if model fails (skip stage)
- Fallback strategies (e.g., OCR if object detection fails)
- User-friendly error messages

### Performance Optimization
- Batch frame processing where possible
- Parallel processing for independent stages
- Efficient memory management (cleanup temp files)
- Mixed precision inference (FP16) on Metal
