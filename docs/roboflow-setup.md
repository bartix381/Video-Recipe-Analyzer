# Roboflow Ingredient Detection Setup

## Getting Your API Key

1. **Go to Roboflow**: https://app.roboflow.com/
2. **Sign up/Login** (free account works!)
3. **Go to Settings**: https://app.roboflow.com/settings/api
4. **Copy your API key**

## Set the API Key

### Option 1: Environment Variable (Recommended)
```bash
export ROBOFLOW_API_KEY="your_api_key_here"
```

### Option 2: Update config file
Edit `experiments/configs/default_config.yaml`:
```yaml
roboflow_detection:
  enabled: true
  api_key: "your_api_key_here"  # Paste your key here
  ...
```

## Model Information

**Dataset**: `python-wfiwe/ingredients-mqhxf`
- **9,272 images** trained
- **31 ingredient classes** (raw ingredients, not dishes!)
- Trained on Roboflow's Snap model

### Classes Detected:
```
bay_leaf, bell_pepper, broccoli, cabbage, carrot, cauliflower, 
chicken, chickpeas, cucumber, egg, eggplant, fish, garlic, ginger, 
lemon, onion, potato, pumpkin, shrimp, tomato, bay_leaf, bell_pepper, 
capsicum, corn, coriander, drumstick, lentil, mushroom, okra, radish, tofu
```

## Why Roboflow Instead of Food-101?

✅ **Raw Ingredients** (carrot, onion, garlic) - what you cook with  
❌ Food-101 detects **Dishes** (apple_pie, cheesecake, spaghetti) - final products

Roboflow is perfect for recipe extraction because it identifies the **ingredients you need**, not what you're making!

## Usage

Once configured, the pipeline will automatically use Roboflow:

```bash
python -m src.cli extract "https://youtube.com/..." --output recipe.json
```

The system will:
1. Extract frames from video
2. **Send frames to Roboflow API** for ingredient detection
3. Detect ingredients like "tomato", "garlic", "onion", etc.
4. Extract text from frames (recipe cards)
5. Transcribe audio narration
6. Combine all sources into final ingredient list

## API Limits

- **Free tier**: 1,000 predictions/month
- **Paid tiers**: More predictions + faster inference
- Check: https://roboflow.com/pricing

For large-scale processing (hundreds of videos), consider caching or downloading the model for local inference.
