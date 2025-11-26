# Tasks: Recipe Video Extraction

**Feature Branch**: `001-recipe-video-extraction`  
**Generated**: 2025-11-26  
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Overview

This document breaks down the implementation of the recipe video extraction system into actionable, dependency-ordered tasks. Tasks are organized by user story to enable independent implementation and testing.

**Total Tasks**: 58  
**MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1) = 30 tasks

## Task Organization

- **Phase 1**: Setup & Infrastructure (10 tasks)
- **Phase 2**: Foundational Prerequisites (8 tasks)
- **Phase 3**: User Story 1 - Basic Ingredient Extraction [P1 - MVP] (12 tasks)
- **Phase 4**: User Story 4 - Structured Output Formats [P2] (8 tasks)
- **Phase 5**: User Story 2 - Step Extraction with Timestamps [P2] (10 tasks)
- **Phase 6**: User Story 3 - Multi-Language Support [P3] (6 tasks)
- **Phase 7**: Polish & Cross-Cutting Concerns (4 tasks)

**Key**:
- `[P]` = Parallelizable (can be worked on simultaneously with other [P] tasks)
- `[US#]` = User Story number (maps to spec.md)
- No tests required per constitution (personal research project)

---

## Phase 1: Setup & Infrastructure

**Goal**: Initialize project structure, dependencies, and core utilities.

### Tasks

- [ ] T001 Create project directory structure per plan.md (src/, experiments/, outputs/, cache/)
- [ ] T002 Create requirements.txt with all dependencies from plan.md
- [ ] T003 Create .gitignore for Python project (cache/, outputs/, experiments/mlruns/, *.pyc, __pycache__)
- [ ] T004 Create experiments/configs/default_config.yaml with configuration from plan.md
- [ ] T005 [P] Implement device detection in src/utils/device.py (MPS/CUDA/CPU)
- [ ] T006 [P] Implement configuration loader in src/utils/config.py (YAML parsing)
- [ ] T007 [P] Implement MLflow utilities in src/utils/mlflow_utils.py (logging helpers)
- [ ] T008 [P] Implement video cache manager in src/utils/cache.py (24h TTL, cleanup)
- [ ] T009 [P] Implement JSON schema validator in src/utils/validators.py
- [ ] T010 Create README.md with project overview, setup instructions, and constitution reference

**Validation**: Project structure exists, all utilities importable, config loads successfully.

---

## Phase 2: Foundational Prerequisites

**Goal**: Build core infrastructure needed by all user stories (blocking dependencies).

### Tasks

- [ ] T011 Define all data model dataclasses in src/entities/data_models.py (Video, Frame, DetectedObject, Ingredient, Step, Transcript, Recipe)
- [ ] T012 [P] Implement base downloader interface in src/downloaders/base.py (abstract class with error handling)
- [ ] T013 [P] Implement YouTube downloader in src/downloaders/youtube.py (yt-dlp wrapper, duration validation <30min, detailed errors)
- [ ] T014 [P] Implement Instagram downloader in src/downloaders/instagram.py (yt-dlp wrapper, duration validation <30min)
- [ ] T015 [P] Implement frame extractor in src/extractors/frame_extractor.py (OpenCV, 1 fps default, configurable)
- [ ] T016 [P] Implement audio extractor in src/extractors/audio_extractor.py (ffmpeg wrapper)
- [ ] T017 Initialize MLflow experiment in experiments/ directory with tracking URI configuration
- [ ] T018 Create CLI skeleton in src/cli.py (argparse, subcommands for extract/config)

**Validation**: Can download test video, extract frames and audio, MLflow logs basic run data.

**Parallel Execution Example**:
```bash
# Can develop simultaneously (different files):
T012 + T015 + T016 + T017  # All independent modules
```

---

## Phase 3: User Story 1 - Basic Ingredient Extraction [P1 - MVP]

**Story Goal**: Extract ingredients list (with quantities) from YouTube/Instagram recipe videos.

**Independent Test**: Given a YouTube/Instagram URL with visible/spoken ingredients, system returns structured list with quantities (e.g., "2 cups flour", "3 eggs").

**Acceptance Criteria**:
- ✅ Extract ingredients from visual analysis (objects in frames)
- ✅ Extract ingredients from on-screen text (OCR)
- ✅ Extract ingredients from spoken audio (transcription)
- ✅ Merge duplicates (sum quantities, preserve timestamps per clarification)
- ✅ Handle substitutions (list alternatives separately per clarification)
- ✅ Output JSON format with ingredients array
- ✅ Log all processing to MLflow

### Tasks

- [ ] T019 [P] [US1] Implement YOLOv8 object detector in src/models/object_detector.py (load yolov8n.pt, batch inference, Metal/MPS)
- [ ] T020 [P] [US1] Implement EasyOCR engine in src/models/ocr_engine.py (English language, confidence thresholding)
- [ ] T021 [P] [US1] Implement Whisper transcriber in src/models/transcriber.py (whisper-base, Metal/MPS, timestamp segments)
- [ ] T022 [P] [US1] Implement quantity parser in src/parsers/quantity_parser.py (regex + ingredient-parser for amounts and units)
- [ ] T023 [P] [US1] Implement ingredient parser in src/parsers/ingredient_parser.py (spaCy + ingredient-parser, fuzzy matching 85%)
- [ ] T024 [US1] Implement visual analysis pipeline: detect objects in frames and map to ingredients in src/pipeline/recipe_pipeline.py (partial - visual only)
- [ ] T025 [US1] Implement OCR analysis pipeline: extract text from frames and parse ingredients in src/pipeline/recipe_pipeline.py (extend with OCR)
- [ ] T026 [US1] Implement audio analysis pipeline: transcribe audio and parse ingredients in src/pipeline/recipe_pipeline.py (extend with audio)
- [ ] T027 [US1] Implement aggregator in src/pipeline/aggregator.py (merge visual + OCR + audio, deduplicate with fuzzy matching, sum quantities, preserve timestamps)
- [ ] T028 [US1] Handle ingredient substitutions in aggregator: detect "or" patterns, create separate entries with alternative_note field
- [ ] T029 [US1] Implement JSON formatter in src/pipeline/recipe_pipeline.py (output Recipe entity as JSON)
- [ ] T030 [US1] Add MLflow logging for US1: log models used, processing time, ingredient count, confidence scores, sample frames with detections

**Validation**:
```bash
python src/cli.py extract "https://youtube.com/watch?v=SAMPLE_ID" --output test_recipe.json
# Verify JSON contains ingredients array with quantities, multiple sources merged
```

**Parallel Execution Example**:
```bash
# Models can be developed simultaneously:
T019 (object detector) + T020 (OCR) + T021 (transcriber)

# Parsers can be developed simultaneously:
T022 (quantity parser) + T023 (ingredient parser)
```

---

## Phase 4: User Story 4 - Structured Output Formats [P2]

**Story Goal**: Export extracted data in multiple formats (JSON, Markdown, plain text).

**Independent Test**: Given extracted recipe data (from US1), verify system outputs valid JSON, Markdown, and plain text formats.

**Acceptance Criteria**:
- ✅ JSON output with schema validation
- ✅ Markdown output with readable formatting
- ✅ Plain text output for easy copying
- ✅ Configurable output format via CLI

### Tasks

- [ ] T031 [P] [US4] Implement Markdown formatter in src/utils/formatters.py (Recipe → Markdown with headings, lists, timestamps)
- [ ] T032 [P] [US4] Implement plain text formatter in src/utils/formatters.py (Recipe → simple text list)
- [ ] T033 [US4] Add format selection to CLI in src/cli.py (--format json|markdown|text)
- [ ] T034 [US4] Implement JSON schema validation in output pipeline using contracts/recipe_schema.json
- [ ] T035 [US4] Add format examples to quickstart.md showing JSON, Markdown, and text outputs
- [ ] T036 [US4] Update MLflow logging to save sample outputs in all three formats as artifacts
- [ ] T037 [US4] Add error handling for invalid format selection with helpful message
- [ ] T038 [US4] Test all three formats with sample recipe data and verify schema compliance

**Validation**:
```bash
python src/cli.py extract "VIDEO_URL" --format json --output recipe.json
python src/cli.py extract "VIDEO_URL" --format markdown --output recipe.md
python src/cli.py extract "VIDEO_URL" --format text --output recipe.txt
# Verify all three files created with correct formatting
```

**Parallel Execution Example**:
```bash
# Formatters independent:
T031 (Markdown) + T032 (text)
```

---

## Phase 5: User Story 2 - Step Extraction with Timestamps [P2]

**Story Goal**: Extract sequential cooking steps with timestamps for video navigation.

**Independent Test**: Given a recipe video, verify system extracts steps with timestamps that match major cooking actions (within 10 seconds).

**Acceptance Criteria**:
- ✅ Extract steps from spoken instructions (audio transcription)
- ✅ Extract steps from on-screen text (OCR)
- ✅ Associate timestamps with each step
- ✅ Sequence steps in chronological order
- ✅ Identify action verbs (mix, bake, chop, etc.)
- ✅ Include steps in output alongside ingredients

### Tasks

- [ ] T039 [P] [US2] Implement step parser in src/parsers/step_parser.py (detect action verbs, extract descriptions from text)
- [ ] T040 [P] [US2] Define action verb taxonomy in step parser (mix, stir, bake, chop, add, pour, heat, cool, blend, simmer, boil, fry)
- [ ] T041 [US2] Extend audio pipeline to extract steps from transcript using temporal cues and action verbs
- [ ] T042 [US2] Extend OCR pipeline to extract steps from on-screen text overlays
- [ ] T043 [US2] Implement step sequencing in aggregator: merge audio + OCR steps, sort by timestamp, assign sequence numbers
- [ ] T044 [US2] Add step confidence scoring based on clarity of action verb and context
- [ ] T045 [US2] Update Recipe entity output to include steps array with sequence, description, timestamp, action
- [ ] T046 [US2] Update formatters (JSON, Markdown, text) to include steps section
- [ ] T047 [US2] Add MLflow logging for US2: log step count, timestamp accuracy, action verb distribution
- [ ] T048 [US2] Test with videos containing clear step instructions and verify timestamps within 10 seconds of actual actions

**Validation**:
```bash
python src/cli.py extract "VIDEO_URL" --output recipe.json
# Verify steps array contains sequential steps with timestamps and action verbs
```

**Parallel Execution Example**:
```bash
# Parser and OCR extension independent:
T039 (step parser) + T042 (OCR extension)
```

---

## Phase 6: User Story 3 - Multi-Language Support [P3]

**Story Goal**: Support recipe extraction from non-English videos (Spanish, French, Italian, etc.).

**Independent Test**: Given a Spanish recipe video, verify system extracts ingredients and steps in Spanish (optionally translated to English).

**Acceptance Criteria**:
- ✅ Transcribe audio in multiple languages
- ✅ Detect text in multiple languages via OCR
- ✅ Parse ingredient names in target language
- ✅ Optional translation to English
- ✅ Configurable language parameter

### Tasks

- [ ] T049 [P] [US3] Update Whisper transcriber to support multilingual mode (detect language automatically or via config)
- [ ] T050 [P] [US3] Update EasyOCR to support multiple languages (Spanish, French, Italian via config)
- [ ] T051 [P] [US3] Download and configure spaCy multilingual models (es_core_news_sm, fr_core_news_sm, it_core_news_sm)
- [ ] T052 [US3] Update ingredient parser to handle multilingual ingredient names (language-specific patterns)
- [ ] T053 [US3] Implement optional translation layer using free translation models (optional feature, deferred if complexity high)
- [ ] T054 [US3] Add --language parameter to CLI for explicit language selection

**Validation**:
```bash
python src/cli.py extract "SPANISH_VIDEO_URL" --language es --output receta.json
# Verify extraction works with Spanish ingredients and steps
```

**Parallel Execution Example**:
```bash
# All model updates can be done simultaneously:
T049 (Whisper multilingual) + T050 (EasyOCR multilingual) + T051 (spaCy models)
```

---

## Phase 7: Polish & Cross-Cutting Concerns

**Goal**: Refine UX, documentation, error handling, and performance.

### Tasks

- [ ] T055 Add comprehensive error handling: detailed messages for download failures, processing errors, invalid inputs per clarification
- [ ] T056 Add progress indicators to CLI for long-running operations (download, frame extraction, model inference)
- [ ] T057 Performance optimization: batch frame processing, cache tuning, FP16 inference on Metal where applicable
- [ ] T058 Update README.md and quickstart.md with complete usage examples, troubleshooting guide, and MLflow instructions

**Validation**: End-to-end system runs smoothly with clear error messages, progress updates, and comprehensive documentation.

---

## Dependencies & Execution Order

### User Story Dependencies

```
Setup (Phase 1) ──→ Foundational (Phase 2)
                          │
                          ├──→ US1 [P1] (Phase 3) ──┐
                          │                          │
                          ├──→ US4 [P2] (Phase 4) ──┤──→ Polish (Phase 7)
                          │                          │
                          ├──→ US2 [P2] (Phase 5) ──┤
                          │                          │
                          └──→ US3 [P3] (Phase 6) ──┘

Legend:
──→ : Sequential dependency (must complete before starting next)
─┐
 ├──→ : Parallel independent paths (can work simultaneously)
 └──→
```

**Critical Path**: Phase 1 → Phase 2 → Phase 3 (US1) = **MVP**

**Independent User Stories**:
- US1 (P1): Independent - Can be tested and deployed standalone
- US4 (P2): Depends on US1 - Requires extracted data to format
- US2 (P2): Independent - Can be developed/tested separately from US1
- US3 (P3): Independent - Can be developed/tested separately

### Blocking vs Non-Blocking Tasks

**Blocking** (must complete before user stories):
- T001-T010: Setup infrastructure
- T011-T018: Foundational prerequisites (downloaders, extractors, CLI skeleton)

**Non-Blocking** (can develop in parallel):
- All [P] tasks within a phase can be developed simultaneously
- Different user story phases (3, 5, 6) are independent after Phase 2

---

## Parallel Execution Examples

### Maximum Parallelism (Phase 3 - US1)

```bash
# 5 developers can work simultaneously:
Dev 1: T019 (YOLOv8 detector)
Dev 2: T020 (EasyOCR engine)
Dev 3: T021 (Whisper transcriber)
Dev 4: T022 (Quantity parser)
Dev 5: T023 (Ingredient parser)

# Then sequentially integrate:
T024 → T025 → T026 → T027 → T028 → T029 → T030
```

### Cross-Story Parallelism (Post-US1)

```bash
# After US1 complete, can work on multiple stories:
Team A: Phase 4 (US4 - Output formats)
Team B: Phase 5 (US2 - Step extraction)
Team C: Phase 6 (US3 - Multi-language)
```

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**Phases**: 1 + 2 + 3 = 30 tasks  
**Timeline Estimate**: 2-3 weeks (single developer)  
**Deliverable**: Extract ingredients from YouTube/Instagram videos with JSON output

**MVP Success Criteria** (from spec.md SC-001 to SC-008):
- ✅ SC-001: Extract 80%+ visible/spoken ingredients
- ✅ SC-002: 70%+ accuracy on quantities
- ✅ SC-004: Process 5-10 min video in <5 min
- ✅ SC-005: YouTube/Instagram download without auth
- ✅ SC-006: Valid JSON output
- ✅ SC-007: Handle 3+ video styles
- ✅ SC-008: MLflow logs all experiments

### Incremental Delivery

1. **Iteration 1** (MVP): Phase 1 + 2 + 3
   - Ingredient extraction only
   - JSON output only
   - English only
   - Validate with 3-5 test videos

2. **Iteration 2** (Enhanced): Phase 4 + 5
   - Multiple output formats
   - Step extraction with timestamps
   - Validate success criteria SC-003 (step timestamp accuracy)

3. **Iteration 3** (Expanded): Phase 6
   - Multi-language support
   - Broader test coverage

4. **Iteration 4** (Polish): Phase 7
   - Performance optimization
   - Error handling refinement
   - Documentation completion

### Testing Strategy

**No formal tests required** per constitution (personal research project). Validation through:

1. **Manual Testing**: Run on diverse videos (professional, home, social media)
2. **MLflow Review**: Inspect logged metrics, sample outputs, processing times
3. **Visual Validation**: Review MLflow artifacts (annotated frames, detected objects)
4. **Success Criteria**: Verify SC-001 through SC-008 against test video set

**Test Video Set** (suggested):
- Professional cooking channel (clear audio, good lighting)
- Home video (moderate quality, some background noise)
- Social media clip (fast-paced, overlay text)
- Long video (20-30 min to test duration limits)
- Non-English video (for US3 validation)

---

## Risk Mitigation

| Risk | Mitigation Tasks |
|------|------------------|
| Poor object detection | T019: Use YOLOv8n; consider fine-tuning if accuracy <80% |
| Audio quality issues | T021: Whisper base handles noise; document limitations in T058 |
| OCR false positives | T020: Confidence thresholding; T055: Error handling |
| Processing time exceeds target | T057: Optimize batch sizes, FP16 inference, caching |
| Download failures | T013, T014: Detailed error messages per clarification |

---

## Next Steps

1. **Start with MVP**: Complete Phase 1 → Phase 2 → Phase 3 (30 tasks)
2. **Validate Early**: Test after Phase 3 with 3-5 sample videos
3. **Iterate**: Add Phase 4 and 5 based on MVP learnings
4. **Expand**: Add Phase 6 if multilingual need emerges
5. **Polish**: Phase 7 for production readiness

**First Task**: T001 - Create project directory structure

```bash
mkdir -p src/{downloaders,extractors,models,parsers,pipeline,utils,entities}
mkdir -p experiments/configs
mkdir -p outputs/recipes
mkdir -p cache/videos
```

---

**Status**: Ready for implementation  
**Suggested Command**: Start with `T001` and work sequentially through Phase 1, then Phase 2, then Phase 3 for MVP.
