# Complete Ingredient Extraction Flow

## Overview: How the System Extracts Ingredients

The system uses **FOUR different sources** to extract ingredients from a recipe video. Each source contributes different ingredients, and they're all merged at the end.

---

## 🎬 The Complete Pipeline

```
┌──────────────────────────────────────────────────────────────┐
│                    VIDEO URL INPUT                            │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│  Step 1: Download Video                                       │
│  - Downloads MP4 file                                         │
│  - Caches for 24 hours                                        │
│  - Extracts metadata (title, description)                     │
└──────────────────────────────────────────────────────────────┘
                            ↓
                ┌───────────┴───────────┐
                ↓                       ↓
┌──────────────────────────┐ ┌──────────────────────────┐
│  Step 2: Extract Frames  │ │  Step 3: Extract Audio   │
│  - 1 frame per second    │ │  - WAV format            │
│  - JPG format            │ │  - 16kHz sample rate     │
└──────────────────────────┘ └──────────────────────────┘
                ↓                       ↓
                ↓                       ↓
┌──────────────────────────┐ ┌──────────────────────────┐
│  Step 4A: Frame Analysis │ │  Step 5: Audio → Text    │
│  🔹 ROBOFLOW DETECTOR    │ │  🔹 WHISPER MODEL        │
│  - Detects 31 ingredients│ │  - Transcribes speech    │
│  - Raw visual detection  │ │  - Extracts segments     │
│  - carrot, ginger, tofu  │ │  - With timestamps       │
└──────────────────────────┘ └──────────────────────────┘
                ↓                       ↓
┌──────────────────────────┐           ↓
│  Step 4B: OCR Analysis   │           ↓
│  🔹 EASYOCR ENGINE       │           ↓
│  - Reads text on screen  │           ↓
│  - Recipe cards          │           ↓
│  - Ingredient lists      │           ↓
└──────────────────────────┘           ↓
                ↓                       ↓
                └───────────┬───────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│  Step 6: AGGREGATE & PARSE INGREDIENTS                        │
│  🔹 INGREDIENT PARSER                                          │
│  Extracts ingredients from FOUR sources:                      │
│                                                                │
│  SOURCE 1: Video Metadata (Title + Description)               │
│  SOURCE 2: Visual Detection (Roboflow on frames)              │
│  SOURCE 3: OCR Text (EasyOCR on frames)                       │
│  SOURCE 4: Audio Transcript (Whisper → Text Parser)           │
└──────────────────────────────────────────────────────────────┘
                            ↓
                            ↓
┌──────────────────────────────────────────────────────────────┐
│  Step 7: MERGE DUPLICATES                                     │
│  - Combines similar ingredients                               │
│  - Aggregates quantities                                      │
│  - Preserves timestamps                                       │
│  - Keeps highest confidence                                   │
└──────────────────────────────────────────────────────────────┘
                            ↓
                            ↓
┌──────────────────────────────────────────────────────────────┐
│                    FINAL RECIPE JSON                          │
│  - 7 unique ingredients                                       │
│  - Confidence scores                                          │
│  - Timestamps per ingredient                                  │
│  - Source tracking                                            │
└──────────────────────────────────────────────────────────────┘
```

---

## 📊 Four Sources of Ingredient Detection

### Source 1: 📝 Video Metadata (Title + Description)
**What it does:** Parses video title and description for ingredient keywords

**Example:**
```
Video Title: "Paneer Butter Masala Recipe | Creamy and Aromatic Indian Delight"
                 ↓
Detected: paneer, butter, masala
```

**Code Location:** `recipe_pipeline.py` lines 293-309
```python
# Extract from video title
title_ingredients = self.ingredient_parser.parse(
    video.title,
    source='metadata',
    confidence=0.9  # High confidence - title is reliable
)
```

**Advantages:**
- ✅ Very reliable (video creator wrote it)
- ✅ Catches key ingredients mentioned in title
- ✅ No API costs

**Limitations:**
- ❌ Only finds ingredients explicitly mentioned
- ❌ Doesn't capture quantities

---

### Source 2: 👁️ Visual Detection (Roboflow on Frames)
**What it does:** Uses computer vision to detect ingredients visible in video frames

**Example:**
```
Frame @ 2.0s: [person holding ginger root]
               ↓
Detected: ginger (45% confidence)

Frame @ 20.0s: [chopped carrots on cutting board]
                ↓
Detected: carrot (73% confidence)
```

**Code Location:** `recipe_pipeline.py` lines 188-196
```python
if self.roboflow_detector is not None:
    logger.info("Using Roboflow ingredient detection (31 ingredient classes)")
    frames = self.roboflow_detector.detect_batch(frames)
```

**Code Location:** `recipe_pipeline.py` lines 312-323
```python
# Extract from visual detections
for frame in frames:
    for obj in frame.detected_objects:
        label_lower = obj.label.lower()
        if any(ing in label_lower for ing in self.ingredient_parser.COMMON_INGREDIENTS):
            ing = Ingredient(
                name=obj.label.lower(),
                source='visual',
                confidence=obj.confidence,
                timestamps=[obj.timestamp],
            )
            all_ingredients.append(ing)
```

**Advantages:**
- ✅ Detects ingredients even if not mentioned in audio
- ✅ Timestamps show when ingredient appears
- ✅ 31 specific ingredient classes (tomato, onion, garlic, etc.)

**Limitations:**
- ❌ API cost (1,000 free calls/month)
- ❌ Can miss ingredients not in training set
- ❌ Can confuse similar items (paneer vs tofu)

---

### Source 3: 🔤 OCR Text Detection (EasyOCR on Frames)
**What it does:** Reads text overlays on video (ingredient lists, recipe cards, on-screen text)

**Example:**
```
Frame @ 5.0s: [Text overlay: "2 cups flour"]
               ↓
OCR reads: "2 cups flour"
               ↓
Parsed: flour (quantity: 2, unit: cups)
```

**Code Location:** `recipe_pipeline.py` lines 325-340
```python
# Extract from OCR text
for frame in frames:
    if frame.ocr_text:
        # Parse text for ingredients and quantities
        text_ingredients = self.ingredient_parser.parse(
            frame.ocr_text,
            source='ocr',
            confidence=0.7
        )
        for ing in text_ingredients:
            # Try to parse quantity
            qty, unit, remaining = self.quantity_parser.parse(frame.ocr_text)
            if qty:
                ing.quantity = qty
                ing.unit = unit
```

**Advantages:**
- ✅ Captures **quantities** and **units** (2 cups, 1 tbsp)
- ✅ Perfect for videos with on-screen ingredient lists
- ✅ No API costs (runs locally)

**Limitations:**
- ❌ Only works if video has text overlays
- ❌ OCR can misread text
- ❌ Many cooking videos don't show text

**Note:** In the Paneer test, OCR found **0 text frames** because this video has no on-screen text overlays.

---

### Source 4: 🎤 Audio Transcript (Whisper → Text Parser)
**What it does:** Transcribes what the chef says, then parses the transcript for ingredient mentions

**Example:**
```
Audio @ 3.5s: "First, we'll add one tablespoon of butter"
               ↓
Whisper transcribes: "First, we'll add one tablespoon of butter"
               ↓
Parser extracts: butter (quantity: 1, unit: tablespoon)
               ↓
Ingredient(name='butter', quantity=1, unit='tbsp', timestamp=3.5)
```

**Code Location:** `recipe_pipeline.py` lines 342-360
```python
# Extract from transcript
for segment in transcript.segments:
    text_ingredients = self.ingredient_parser.parse(
        segment.text,
        source='audio',
        confidence=0.8
    )
    for ing in text_ingredients:
        ing.timestamps = [segment.start]
        # Try to parse quantity
        qty, unit, remaining = self.quantity_parser.parse(segment.text)
        if qty:
            ing.quantity = qty
            ing.unit = unit
        # Check for substitutions
        substitution = self.ingredient_parser.detect_substitution(segment.text)
        if substitution:
            ing.alternative_note = substitution
```

**How the Parser Works:**
```python
# ingredient_parser.py lines 60-65
COMMON_INGREDIENTS = [
    'flour', 'sugar', 'salt', 'butter', 'onion', 'garlic', 'tomato',
    'paneer', 'ginger', 'curry', 'masala', 'chicken', 'beef', ...
]

# Searches transcript for these keywords
if ingredient_name in text_lower:
    ingredients.append(Ingredient(name=ingredient_name, ...))
```

**Advantages:**
- ✅ Captures **ALL** ingredients chef mentions verbally
- ✅ Gets **quantities** and **units** from speech ("2 tablespoons", "half a cup")
- ✅ Detects **substitutions** ("or use olive oil instead")
- ✅ Most cooking videos have audio narration

**Limitations:**
- ❌ Depends on chef actually mentioning ingredients
- ❌ Some videos are silent (ASMR, no commentary)
- ❌ Whisper may misunderstand speech
- ❌ Requires keyword matching (won't find unknown ingredients)

**Note:** In the Paneer test, the video was **Romanian language ASMR** (no speech), so transcript was **empty** (0 segments).

---

## 🔄 Merging Process

After extracting from all 4 sources, the system merges duplicates:

```python
# Example: Same ingredient from multiple sources
[
  Ingredient(name='butter', source='metadata', confidence=0.9),   # From title
  Ingredient(name='butter', source='audio', confidence=0.8, quantity=2, unit='tbsp'),  # From speech
]
           ↓ MERGE ↓
Ingredient(
  name='butter',
  source='merged',      # Combined source
  confidence=0.9,       # Highest confidence
  quantity=2,           # From audio
  unit='tbsp',          # From audio
  timestamps=[3.5],     # When mentioned
)
```

**Code Location:** `recipe_pipeline.py` lines 371-444

---

## 📝 Paneer Butter Masala Example Breakdown

### Video: https://www.youtube.com/shorts/ckSdRrgnbQI

#### Final Result: 7 Ingredients
```json
{
  "ingredients": [
    {"name": "butter", "source": "metadata", "confidence": 0.9},     // From title
    {"name": "carrot", "source": "visual", "confidence": 0.73},      // Roboflow @ 20s
    {"name": "ginger", "source": "visual", "confidence": 0.45},      // Roboflow @ 2s
    {"name": "masala", "source": "metadata", "confidence": 0.9},     // From title
    {"name": "paneer", "source": "metadata", "confidence": 0.9},     // From title
    {"name": "tofu", "source": "visual", "confidence": 0.41},        // Roboflow @ 1s (misclassified paneer)
    {"name": "tomato", "source": "metadata", "confidence": 0.85}     // From description parsing
  ]
}
```

#### Source Breakdown:
- **Metadata (3):** butter, masala, paneer, tomato
- **Visual (3):** carrot, ginger, tofu
- **OCR (0):** None (no text overlays)
- **Audio (0):** None (silent ASMR video)

---

## 🎯 Key Takeaways

### Why Multiple Sources?
Different videos have different formats:
- **Cooking shows:** Heavy audio narration → Audio source wins
- **Recipe cards:** Text overlays → OCR source wins
- **Silent cooking:** Visual only → Roboflow wins
- **Shorts/TikTok:** Title is key → Metadata wins

### Current Strengths:
✅ **Visual detection works perfectly** (Roboflow detects carrot, ginger)  
✅ **Metadata parsing works** (extracts butter, paneer from title)  
✅ **Multi-source approach is robust**

### Current Gaps:
❌ Audio not working on this video (Romanian language, ASMR = no speech)  
❌ OCR not helpful (no text overlays)  
⚠️ Need more videos with English narration to test audio extraction

### Next Steps for Audio:
1. Test on videos with **English narration** (not silent ASMR)
2. Verify Whisper correctly transcribes ingredient mentions
3. Validate quantity parsing ("2 cups", "1 tablespoon")
4. Test substitution detection ("or use olive oil instead")

---

## 🔧 Configuration

All sources can be enabled/disabled in config:

```yaml
# experiments/configs/default_config.yaml

roboflow_detection:
  enabled: true        # ✅ Visual detection

food_classification:
  enabled: false       # ❌ Disabled (wrong model type)

ocr:
  languages: ["en"]    # ✅ OCR text extraction
  confidence_threshold: 0.4

transcription:
  model: "base"        # ✅ Audio transcription
  device: "cpu"        # Fixed for stability
  language: null       # Auto-detect language
```

---

## 📚 Code References

| Component | File | Purpose |
|-----------|------|---------|
| **Pipeline Orchestrator** | `src/pipeline/recipe_pipeline.py` | Coordinates all 6 steps |
| **Roboflow Detector** | `src/models/roboflow_detector.py` | Visual ingredient detection |
| **OCR Engine** | `src/models/ocr_engine.py` | Text extraction from frames |
| **Transcriber** | `src/models/transcriber.py` | Speech-to-text (Whisper) |
| **Ingredient Parser** | `src/parsers/ingredient_parser.py` | Keyword extraction from text |
| **Quantity Parser** | `src/parsers/quantity_parser.py` | Parse amounts ("2 cups") |

---

## 🧪 Testing Audio Extraction

To properly test audio ingredient extraction, we need a video with:
- ✅ English narration (not Romanian/silent)
- ✅ Chef verbally mentioning ingredients
- ✅ Clear audio quality

**Suggested test videos:**
- Babish Culinary Universe
- Gordon Ramsay tutorials
- America's Test Kitchen
- Bon Appétit recipe videos

Would you like me to test on one of these to validate the audio extraction pipeline?
