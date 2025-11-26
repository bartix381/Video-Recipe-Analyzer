# Feature Specification: Recipe Video Extraction# Feature Specification: [FEATURE NAME]



**Feature Branch**: `001-recipe-video-extraction`  **Feature Branch**: `[###-feature-name]`  

**Created**: 2025-11-26  **Created**: [DATE]  

**Status**: Draft  **Status**: Draft  

**Input**: User description: "Extract ingredients and steps from recipe videos on YouTube and Instagram. User provides a video URL (YouTube or Instagram). The system downloads/processes the video, analyzes frames and audio to identify cooking ingredients and key preparation steps. Output should be a structured list of all ingredients mentioned or shown in the video, plus a sequence of key cooking steps with timestamps. This is a computer vision + NLP project that needs to handle video processing (downloading from YouTube/Instagram), object detection for ingredients, OCR for on-screen text, and audio transcription for spoken instructions."

## Clarifications

### Session 2025-11-26

- Q: When processing detects duplicate ingredients with different quantities (e.g., "2 cups flour" at 0:30 and "1 cup flour" at 2:15), how should the system handle this? → A: Sum quantities into single entry with multiple timestamps
- Q: When the system downloads videos for processing, what should the data retention policy be for temporary video files? → A: Cache for 24 hours then auto-delete
- Q: When video download fails (private video, geo-restricted, network error), what should the system's error handling behavior be? → A: Detailed error with retry suggestion
- Q: What is the maximum video duration the system should support for processing? → A: 30 minutes
- Q: When the system encounters ingredient substitutions in the video (e.g., "use butter or olive oil"), how should it represent this in the output? → A: List alternatives separately with note

## User Scenarios & Testing



### User Story 1 - Basic Ingredient Extraction from Video (Priority: P1)<!--

  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.

A user discovers a recipe video on YouTube/Instagram without a written recipe. They want to extract the ingredients list automatically so they can prepare their shopping list.  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,

  you should still have a viable MVP (Minimum Viable Product) that delivers value.

**Why this priority**: Core value proposition - enables users to get structured ingredient lists from any recipe video. This is the MVP that delivers immediate value.  

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.

**Independent Test**: Can be fully tested by providing a YouTube/Instagram URL with visible ingredients and verifying the system returns a structured list of ingredients. Delivers standalone value even without step extraction.  Think of each story as a standalone slice of functionality that can be:

  - Developed independently

**Acceptance Scenarios**:  - Tested independently

  - Deployed independently

1. **Given** a YouTube recipe video URL, **When** user submits the URL, **Then** system returns a list of ingredients with quantities (e.g., "2 cups flour", "3 eggs", "1 tsp salt")  - Demonstrated to users independently

2. **Given** an Instagram recipe video URL, **When** user submits the URL, **Then** system downloads and extracts ingredients from both on-screen text and visual analysis-->

3. **Given** a video with ingredients shown visually (in bowls/containers), **When** system analyzes frames, **Then** detected ingredients are included in the output list

4. **Given** a video with spoken ingredients (audio only), **When** system transcribes audio, **Then** mentioned ingredients are extracted and added to the list

---

### User Story 2 - Step Extraction with Timestamps (Priority: P2)

A user wants to follow along with a recipe video but needs a quick reference guide. They want key cooking steps with timestamps so they can jump to specific parts of the video.



**Why this priority**: Enhances usability by making videos navigable. Adds significant value but ingredients alone (P1) are sufficient for MVP.**Acceptance Scenarios**:



**Independent Test**: Can be tested independently by verifying extracted steps match major cooking actions in the video and timestamps allow jumping to correct moments. Useful even if ingredient extraction isn't perfect.1. **Given** [initial state], **When** [action], **Then** [expected outcome]

2. **Given** [initial state], **When** [action], **Then** [expected outcome]

**Acceptance Scenarios**:

---

1. **Given** a recipe video, **When** user requests step extraction, **Then** system returns sequential cooking steps with timestamps (e.g., "0:45 - Mix dry ingredients", "2:30 - Add eggs and whisk")
2. **Given** a video with on-screen step text, **When** system performs OCR, **Then** steps are extracted with corresponding timestamps
3. **Given** a video with spoken instructions, **When** system analyzes audio, **Then** key action verbs (mix, bake, chop, etc.) trigger step extraction
4. **Given** extracted steps, **When** displayed to user, **Then** steps are numbered sequentially and include timestamp links

---

### User Story 3 - Multi-Language Support (Priority: P3)

A user wants to extract recipes from videos in different languages (Spanish, French, Italian cooking channels).



**Why this priority**: Nice-to-have expansion feature. English-only support (P1, P2) covers majority use case initially.1. **Given** [initial state], **When** [action], **Then** [expected outcome]



**Independent Test**: Can be tested by providing non-English videos and verifying extraction quality. Adds value for international users but not critical for initial release.---



**Acceptance Scenarios**:### User Story 3 - [Brief Title] (Priority: P3)

**Acceptance Scenarios**:

1. **Given** a Spanish recipe video, **When** system transcribes audio, **Then** Spanish ingredient names are detected and optionally translated to English
2. **Given** a video with multilingual on-screen text, **When** OCR processes frames, **Then** text is detected regardless of language

---

### User Story 4 - Structured Output Formats (Priority: P2)

A user wants to export extracted data in different formats (JSON, Markdown, plain text) for integration with recipe apps or personal notes.

**Why this priority**: Increases utility and integration potential. Important for practical use but not essential for core functionality testing.

**Independent Test**: Given extracted recipe data (from US1), verify system outputs valid JSON, Markdown, and plain text formats.

**Acceptance Scenarios**:

1. **Given** extracted recipe data, **When** user requests JSON format, **Then** system outputs structured JSON with ingredients array and steps array
2. **Given** extracted recipe data, **When** user requests Markdown format, **Then** system outputs readable Markdown with proper formatting
3. **Given** extracted recipe data, **When** user requests plain text, **Then** system outputs simple text list suitable for copying

---

### Edge Cases

- How does system handle [error scenario]?

- What happens when video contains no visible ingredients (only cooking process shown)?

- How does system handle videos with poor audio quality or heavy background music?
- What if ingredients are mentioned multiple times with different quantities (e.g., "add 2 cups flour" then later "add remaining 1 cup flour")? → Sum quantities into single entry with all timestamps preserved for traceability
- How to handle ingredient substitutions mentioned in video (e.g., "use butter or oil")? → List each alternative as separate ingredient entry with note indicating relationship (e.g., "butter (or olive oil)" and "olive oil (alternative)")
- What if video is private, geo-restricted, or requires authentication? → System provides detailed error message specifying the issue and suggesting alternatives (e.g., "Video is private. Please use a publicly accessible video URL.")
- How does system handle very long videos (>30 minutes) or short clips (<1 minute)? → Videos >30 minutes are rejected with duration limit error; very short videos (<1 min) are processed normally but may have limited ingredient/step extraction
- What if OCR detects unrelated text (channel names, social media handles, ads)?
- How to distinguish ingredients from equipment/tools mentioned?

## Requirements

### Functional Requirements

- **FR-001**: System MUST accept YouTube and Instagram video URLs as input
- **FR-002**: System MUST download/stream video content for processing (using open-source tools like yt-dlp)
- **FR-003**: System MUST extract video frames at 1 frame per second (configurable) for visual analysis
- **FR-004**: System MUST perform object detection on frames to identify visible ingredients (using open-source CV models)
- **FR-005**: System MUST perform OCR on frames to extract on-screen text containing ingredients and steps (using open-source OCR)
- **FR-006**: System MUST transcribe audio to text for spoken ingredient/step extraction (using open-source speech-to-text)
- **FR-007**: System MUST parse extracted text (visual and audio) to identify ingredients with quantities and units
- **FR-008**: System MUST identify key cooking steps from transcribed audio and visual cues
- **FR-009**: System MUST associate timestamps with extracted steps for video navigation
- **FR-010**: System MUST output structured data containing ingredients list and steps sequence
- **FR-011**: System MUST handle common video formats (MP4, WebM, etc.)
- **FR-012**: System MUST provide detailed error messages for download failures (invalid URLs, private videos, geo-restrictions, network errors) with actionable retry suggestions
- **FR-013**: System MUST support multiple output formats (JSON, Markdown, plain text)
- **FR-014**: System MUST log all processing steps and results to MLflow for experiment tracking (per constitution)
- **FR-015**: System MUST use only open-source, free models without API keys (per constitution)
- **FR-016**: System MUST cache downloaded videos for 24 hours to enable re-processing experiments, then auto-delete to manage disk space
- **FR-017**: System MUST reject videos longer than 30 minutes with a clear error message indicating the duration limit
- **FR-018**: System MUST handle ingredient substitutions (e.g., "butter or oil") by listing each alternative as a separate ingredient entry with notation indicating the relationship

### Key Entities

- **Video**: Represents the input recipe video
  - Attributes: URL, source platform (YouTube/Instagram), duration, title
  - Relationships: Contains multiple frames, has audio track

- **Frame**: Individual image extracted from video at specific timestamp
  - Attributes: timestamp, image data, detected objects, OCR text
  - Relationships: Belongs to Video, contains Ingredients (detected visually)

- **Ingredient**: A cooking ingredient identified in the video
  - Attributes: name, quantity (summed total), unit, source (visual/audio/text), confidence score, timestamps (array if mentioned multiple times), alternative_note (for substitutions like "or olive oil")
  - Relationships: Detected in Frame(s), mentioned in Transcript

- **Step**: A cooking instruction or action
  - Attributes: sequence number, description, timestamp, source (audio/visual), action verb
  - Relationships: Belongs to Video, may reference Ingredients

- **Transcript**: Text extracted from video audio
  - Attributes: full text, timestamp segments, language
  - Relationships: Belongs to Video, contains mentions of Ingredients and Steps

- **Recipe**: Final structured output
  - Attributes: title (if available), ingredients list, steps list, source URL, extraction date
  - Relationships: Aggregates Ingredients and Steps from Video

## Success Criteria

### Measurable Outcomes

- **SC-001**: System successfully extracts at least 80% of clearly visible or spoken ingredients from test recipe videos
- **SC-002**: System correctly identifies ingredient quantities and units with 70%+ accuracy when explicitly stated
- **SC-003**: System extracts key cooking steps with timestamps that allow navigation to within 10 seconds of actual action
- **SC-004**: System processes a typical 5-10 minute recipe video in under 5 minutes on local hardware; supports videos up to 30 minutes duration
- **SC-005**: System successfully downloads and processes videos from YouTube and Instagram without API keys or authentication
- **SC-006**: Output JSON/Markdown format is valid and parseable by standard tools
- **SC-007**: System handles at least 3 different video styles (professional cooking channels, home videos, social media clips) with consistent extraction quality
- **SC-008**: All experiments and model inference runs are logged to MLflow with hyperparameters, metrics, and sample outputs (constitution compliance)

## Technical Considerations

### Architecture Overview

The system follows a multi-stage pipeline:

1. **Video Download**: URL → Video file (yt-dlp for YouTube, Instagram downloaders)
2. **Frame Extraction**: Video → Frame sequence (OpenCV/ffmpeg)
3. **Visual Analysis**: Frames → Detected objects + OCR text (PyTorch models)
4. **Audio Processing**: Video audio → Transcript (Whisper or similar)
5. **NLP Extraction**: Text → Ingredients + Steps (rule-based + NLP)
6. **Aggregation**: All sources → Structured Recipe output
7. **MLflow Logging**: Track all processing steps, models used, metrics

### Open Source Models & Tools (Constitution Compliant)

**Video Processing:**
- yt-dlp (YouTube/Instagram download)
- OpenCV or ffmpeg (frame extraction)

**Computer Vision (Object Detection):**
- YOLOv8 or YOLOv5 from Ultralytics (free, no API key)
- DETR from HuggingFace Transformers (free)
- Potential: Fine-tune on food/ingredient dataset (Food-101, Recipe1M)

**OCR (Text Extraction):**
- EasyOCR (free, open source)
- Tesseract OCR (free, open source)
- PaddleOCR (free, open source)

**Speech-to-Text:**
- OpenAI Whisper (open source, runs locally, no API key)
- Vosk (free, lightweight)
- wav2vec 2.0 from HuggingFace (free)

**NLP (Ingredient/Step Parsing):**
- spaCy (free, open source) for entity recognition
- HuggingFace Transformers BERT/RoBERTa for text classification (free)
- Rule-based parsing with regex for quantities/units
- ingredient-parser library (open source Python)

**Experiment Tracking:**
- MLflow (free, open source)

### Data Pipeline

1. Input: Video URL
2. Download video to temporary storage
3. Extract frames at 1 fps (configurable) → save key frames
4. Run object detection on frames → detect bowls, ingredients, utensils
5. Run OCR on frames with text overlays
6. Extract audio and run speech-to-text
7. Parse transcript for ingredient mentions (NLP)
8. Combine visual + text + audio detections
9. Deduplicate and merge ingredients: sum quantities when same ingredient appears multiple times, preserve all timestamps for traceability
10. Identify steps from transcript using action verbs and temporal cues
11. Output structured format (JSON/Markdown)
12. Log to MLflow: models used, processing time, accuracy metrics, sample outputs

### Reproducibility (Constitution Requirement)

- Set random seeds for all model inference (PyTorch, NumPy)
- Version all models (e.g., YOLOv8n weights hash, Whisper base model)
- Log exact preprocessing parameters (frame rate, resize dimensions, etc.)
- Store config files for each experiment
- Use requirements.txt for Python dependencies

### Cost Efficiency (Constitution Requirement)

- All processing runs locally (no cloud API calls)
- Use lightweight model variants when possible (e.g., Whisper base, not large)
- Cache downloaded videos for 24 hours to avoid redundant downloads during experimentation, then auto-delete
- Use batch processing for frames when GPU available
- Consider mixed precision (FP16) for faster inference

### Assumptions

- Videos contain at least some visual or spoken reference to ingredients
- Audio quality is sufficient for basic transcription
- Ingredient names follow common English naming conventions (for initial version)
- Users have basic local compute resources (videos processed locally, not real-time)
- Video URLs are publicly accessible (no login required)
- Recipe videos are typically 5-20 minutes; maximum supported duration is 30 minutes

### Out of Scope (for initial version)

- Real-time processing or streaming
- Custom video uploads (only URLs supported initially)
- Automatic ingredient categorization (produce, dairy, spices, etc.)
- Nutritional information calculation
- Recipe rating or recommendation system
- Video editing or annotation features
- Multi-language support beyond English (future P3)
