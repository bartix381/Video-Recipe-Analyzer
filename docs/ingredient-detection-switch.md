# 🎯 Ingredient Detection Model Switch

## Problem
Food-101 model (`nateraw/food`) detects **finished dishes** (apple_pie, cheesecake, spaghetti_carbonara) instead of **raw ingredients** (flour, eggs, butter). This is not useful for recipe extraction where we need to identify the ingredients used.

## Solution
Switched to **Roboflow's ingredient detection model** which detects **31 raw ingredient classes**:

### Roboflow Model: `python-wfiwe/ingredients-mqhxf`
- **9,272 training images**
- **31 classes**: tomato, onion, garlic, carrot, potato, chicken, egg, broccoli, cabbage, etc.
- **Use case**: Recipe ingredient extraction ✅
- **Detection type**: Raw ingredients you cook with

vs.

### Food-101 (Previous)
- **101 classes**: apple_pie, cheesecake, chicken_curry, spaghetti_carbonara, etc.
- **Use case**: Dish classification ❌
- **Detection type**: Finished meals/dishes

## Setup Instructions

### 1. Get Roboflow API Key (Free!)
1. Go to https://app.roboflow.com/
2. Sign up (free tier: 1,000 predictions/month)
3. Get API key from https://app.roboflow.com/settings/api

### 2. Set Environment Variable
```bash
export ROBOFLOW_API_KEY="your_api_key_here"
```

### 3. Run Extraction
```bash
python -m src.cli extract "https://youtube.com/..." --output recipe.json
```

## Configuration

Edit `experiments/configs/default_config.yaml`:

```yaml
# Disable Food-101 (dish classification)
food_classification:
  enabled: false

# Enable Roboflow (ingredient detection)
roboflow_detection:
  enabled: true
  api_key: ""  # Or set via ROBOFLOW_API_KEY env var
  workspace: "python-wfiwe"
  project: "ingredients-mqhxf"
  version: 1
  conf_threshold: 0.40
```

## Testing

Test on existing frames:
```bash
python test_roboflow.py
```

## Implementation Details

### New Files
- `src/models/roboflow_detector.py` - Roboflow API client
- `docs/roboflow-setup.md` - Detailed setup guide
- `test_roboflow.py` - Quick test script

### Modified Files
- `experiments/configs/default_config.yaml` - Added roboflow_detection section
- `src/pipeline/recipe_pipeline.py` - Added Roboflow support with priority
- `src/models/__init__.py` - Exported RoboflowDetector

### Detection Priority
1. **Roboflow** (if enabled and API key provided) ← Best for ingredients!
2. Food-101 (if enabled) ← For dish classification
3. YOLOv8 COCO (fallback) ← Generic objects

## 31 Ingredient Classes Detected

```
bay_leaf, bell_pepper, broccoli, cabbage, carrot, cauliflower,
chicken, chickpeas, cucumber, egg, eggplant, fish, garlic, ginger,
lemon, onion, potato, pumpkin, shrimp, tomato, capsicum, corn,
coriander, drumstick, lentil, mushroom, okra, radish, tofu
```

## Benefits

✅ **Accurate**: Detects actual cooking ingredients  
✅ **Fast**: Hosted API, no local model loading  
✅ **Scalable**: 1,000 free predictions/month  
✅ **Maintained**: Roboflow handles updates  
✅ **Easy**: No model downloads, just API key  

## Next Steps

1. Get your Roboflow API key
2. Set `ROBOFLOW_API_KEY` environment variable  
3. Run extraction on recipe videos
4. See actual ingredients like "tomato", "onion", "garlic" instead of "pizza" or "curry"!

## Troubleshooting

**Q: "No API key provided" error?**  
A: Set `export ROBOFLOW_API_KEY="your_key"` or add to config.yaml

**Q: "No ingredients detected"?**  
A: Lower `conf_threshold` in config (try 0.30 or 0.25)

**Q: API rate limit exceeded?**  
A: Free tier has 1,000 predictions/month. Upgrade plan or wait for reset.

**Q: Want to use offline?**  
A: Download dataset and train YOLOv8 locally (see `download_roboflow_model.py`)
