"""Main recipe extraction pipeline."""
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import List
from collections import defaultdict

from ..entities import Recipe, Ingredient, Video
from ..utils import Config, MLflowTracker, VideoCache, get_device
from ..downloaders import YouTubeDownloader, InstagramDownloader, DownloadError
from ..extractors import FrameExtractor, AudioExtractor
from ..models import ObjectDetector, OCREngine, Transcriber, FoodClassifier
from ..parsers import QuantityParser, IngredientParser

logger = logging.getLogger(__name__)


class RecipePipeline:
    """End-to-end pipeline for recipe extraction from videos."""
    
    def __init__(self, config: Config):
        """
        Initialize pipeline with configuration.
        
        Args:
            config: Configuration object
        """
        self.config = config
        
        # Initialize cache
        cache_dir = Path("cache")
        cache_ttl = config.get('video.cache_ttl', 86400) // 3600
        self.cache = VideoCache(str(cache_dir), cache_ttl)
        
        # Initialize downloaders
        max_duration = config.get('video.max_duration', 1800)
        timeout = config.get('video.download_timeout', 300)
        self.youtube_downloader = YouTubeDownloader(str(cache_dir), max_duration, timeout)
        self.instagram_downloader = InstagramDownloader(str(cache_dir), max_duration, timeout)
        
        # Initialize extractors
        fps = config.get('frame_extraction.fps', 1.0)
        format = config.get('frame_extraction.format', 'jpg')
        quality = config.get('frame_extraction.quality', 95)
        self.frame_extractor = FrameExtractor(fps, "outputs/frames", format, quality)
        self.audio_extractor = AudioExtractor("outputs/audio", "wav")
        
        # Initialize ML models (lazy loading)
        self._object_detector = None
        self._food_classifier = None
        self._ocr_engine = None
        self._transcriber = None
        
        # Initialize parsers
        fuzzy_threshold = config.get('ingredient_parsing.fuzzy_match_threshold', 85)
        self.quantity_parser = QuantityParser()
        self.ingredient_parser = IngredientParser(fuzzy_threshold)
        
        # Initialize MLflow
        self.mlflow = MLflowTracker(
            config.get('mlflow.experiment_name', 'recipe-video-extraction'),
            config.get('mlflow.tracking_uri', './experiments/mlruns')
        )
        
        logger.info("RecipePipeline initialized")
    
    @property
    def object_detector(self):
        """Lazy load object detector."""
        if self._object_detector is None:
            cfg = self.config.get_section('object_detection')
            device = get_device(cfg.get('device', 'auto'))
            self._object_detector = ObjectDetector(
                model_name=cfg.get('model', 'yolov8n.pt'),
                conf_threshold=cfg.get('conf_threshold', 0.25),
                iou_threshold=cfg.get('iou_threshold', 0.45),
                max_det=cfg.get('max_det', 300),
                device=str(device),
                fp16=cfg.get('fp16', True),
            )
        return self._object_detector
    
    @property
    def food_classifier(self):
        """Lazy load food classifier."""
        if self._food_classifier is None:
            cfg = self.config.get_section('food_classification')
            if cfg.get('enabled', False):
                device = get_device(cfg.get('device', 'auto'))
                self._food_classifier = FoodClassifier(
                    model_name=cfg.get('model', 'nateraw/food'),
                    conf_threshold=cfg.get('conf_threshold', 0.10),
                    device=str(device),
                )
        return self._food_classifier
    
    @property
    def ocr_engine(self):
        """Lazy load OCR engine."""
        if self._ocr_engine is None:
            cfg = self.config.get_section('ocr')
            self._ocr_engine = OCREngine(
                languages=cfg.get('languages', ['en']),
                gpu=True,  # EasyOCR handles device detection
                confidence_threshold=cfg.get('confidence_threshold', 0.4),
                paragraph=cfg.get('paragraph', False),
                batch_size=cfg.get('batch_size', 1),
            )
        return self._ocr_engine
    
    @property
    def transcriber(self):
        """Lazy load transcriber."""
        if self._transcriber is None:
            cfg = self.config.get_section('transcription')
            device = get_device(cfg.get('device', 'auto'))
            self._transcriber = Transcriber(
                model_name=cfg.get('model', 'base'),
                language=cfg.get('language'),
                device=str(device),
                fp16=cfg.get('fp16', True),
                condition_on_previous_text=cfg.get('condition_on_previous_text', True),
            )
        return self._transcriber
    
    def process(self, url: str) -> Recipe:
        """
        Process video and extract recipe.
        
        Args:
            url: Video URL (YouTube or Instagram)
            
        Returns:
            Recipe entity
        """
        start_time = time.time()
        run_id = self.mlflow.start_run(f"extract_{int(start_time)}")
        
        try:
            # Log parameters
            self.mlflow.log_params({
                'url': url,
                'fps': self.config.get('frame_extraction.fps'),
                'yolo_model': self.config.get('object_detection.model'),
                'whisper_model': self.config.get('transcription.model'),
            })
            
            # Step 1: Download video
            logger.info("Step 1/6: Downloading video...")
            video = self._download_video(url)
            
            # Step 2: Extract frames
            logger.info("Step 2/6: Extracting frames...")
            frames = self.frame_extractor.extract(video.local_path)
            self.mlflow.log_metric('frame_count', len(frames))
            
            # Step 3: Extract audio
            logger.info("Step 3/6: Extracting audio...")
            audio_path = self.audio_extractor.extract(video.local_path)
            
            # Step 4: Analyze frames (food classification or object detection + OCR)
            logger.info("Step 4/6: Analyzing frames...")
            if self.food_classifier is not None:
                logger.info("Using HuggingFace food classifier")
                frames = self.food_classifier.classify_batch(frames)
            else:
                logger.info("Using YOLOv8 object detector")
                frames = self.object_detector.detect_batch(frames)
            frames = self.ocr_engine.extract_batch(frames)
            
            # Step 5: Transcribe audio
            logger.info("Step 5/6: Transcribing audio...")
            transcript = self.transcriber.transcribe(audio_path)
            self.mlflow.log_metric('transcript_segments', len(transcript.segments))
            
            # Step 6: Aggregate ingredients
            logger.info("Step 6/6: Aggregating ingredients...")
            ingredients = self._aggregate_ingredients(video, frames, transcript)
            
            # Create recipe
            recipe = Recipe(
                source_url=url,
                title=video.title,
                ingredients=ingredients,
                steps=[],  # Will be added in Phase 5
                extraction_date=datetime.now().isoformat(),
                processing_time=time.time() - start_time,
                metadata={
                    'models_used': {
                        'object_detection': self.config.get('object_detection.model'),
                        'ocr': 'easyocr',
                        'transcription': self.config.get('transcription.model'),
                    },
                    'config': {
                        'fps': self.config.get('frame_extraction.fps'),
                        'yolo_conf': self.config.get('object_detection.conf_threshold'),
                    }
                }
            )
            
            # Log metrics
            self.mlflow.log_metrics({
                'ingredient_count': len(ingredients),
                'processing_time': recipe.processing_time,
            })
            
            # Log sample output
            self.mlflow.log_dict(recipe.to_dict(), 'recipe_output.json')
            
            logger.info(f"✓ Extraction complete: {len(ingredients)} ingredients in {recipe.processing_time:.1f}s")
            
            return recipe
        
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            self.mlflow.set_tag('status', 'failed')
            self.mlflow.set_tag('error', str(e))
            raise
        
        finally:
            self.mlflow.end_run()
            # Cleanup cache
            self.cache.cleanup()
    
    def _download_video(self, url: str) -> Video:
        """Download video from URL."""
        # Check cache first
        cached_path = self.cache.get(url)
        if cached_path:
            logger.info(f"Using cached video: {cached_path}")
            # Determine platform from URL
            if 'youtube.com' in url or 'youtu.be' in url:
                platform = 'youtube'
            elif 'instagram.com' in url:
                platform = 'instagram'
            else:
                platform = 'unknown'
            
            return Video(
                url=url,
                platform=platform,
                local_path=cached_path,
            )
        
        # Download new video
        if 'youtube.com' in url or 'youtu.be' in url:
            video = self.youtube_downloader.download(url)
        elif 'instagram.com' in url:
            video = self.instagram_downloader.download(url)
        else:
            raise DownloadError(f"Unsupported platform. URL must be YouTube or Instagram. URL: {url}")
        
        # Add to cache
        self.cache.put(url, video.local_path)
        
        return video
    
    def _aggregate_ingredients(self, video, frames, transcript) -> List[Ingredient]:
        """Aggregate ingredients from all sources."""
        all_ingredients = []
        
        # Extract from video title and description (NEW!)
        if video.title:
            logger.info(f"Parsing ingredients from title: {video.title}")
            title_ingredients = self.ingredient_parser.parse(
                video.title,
                source='metadata',
                confidence=0.9  # High confidence for title
            )
            all_ingredients.extend(title_ingredients)
        
        if video.description:
            logger.info("Parsing ingredients from description")
            desc_ingredients = self.ingredient_parser.parse(
                video.description[:500],  # First 500 chars
                source='metadata',
                confidence=0.85
            )
            all_ingredients.extend(desc_ingredients)
        
        # Extract from visual detections
        for frame in frames:
            for obj in frame.detected_objects:
                # Map object labels to ingredients
                # Simple mapping - in production, this would be more sophisticated
                label_lower = obj.label.lower()
                if any(ing in label_lower for ing in self.ingredient_parser.COMMON_INGREDIENTS):
                    ing = Ingredient(
                        name=obj.label.lower(),
                        source='visual',
                        confidence=obj.confidence,
                        timestamps=[obj.timestamp],
                    )
                    all_ingredients.append(ing)
        
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
                    ing.timestamps = [frame.timestamp]
                    # Try to parse quantity
                    qty, unit, remaining = self.quantity_parser.parse(frame.ocr_text)
                    if qty:
                        ing.quantity = qty
                        ing.unit = unit
                all_ingredients.extend(text_ingredients)
        
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
            all_ingredients.extend(text_ingredients)
        
        # Merge duplicates
        merged = self._merge_ingredients(all_ingredients)
        
        logger.info(f"Aggregated {len(all_ingredients)} raw → {len(merged)} merged ingredients")
        
        return merged
    
    def _merge_ingredients(self, ingredients: List[Ingredient]) -> List[Ingredient]:
        """Merge duplicate ingredients."""
        if not ingredients:
            return []
        
        # Group by similar names
        groups = defaultdict(list)
        processed = set()
        
        for i, ing in enumerate(ingredients):
            if i in processed:
                continue
            
            # Normalize name
            norm_name = self.ingredient_parser.normalize_name(ing.name)
            group_key = norm_name
            
            # Find similar ingredients
            for j, other in enumerate(ingredients[i+1:], start=i+1):
                if j in processed:
                    continue
                
                if self.ingredient_parser.are_similar(ing.name, other.name):
                    group_key = norm_name
                    processed.add(j)
            
            groups[group_key].append(ing)
            processed.add(i)
        
        # Merge groups
        merged = []
        for group_name, group_ingredients in groups.items():
            if not group_ingredients:
                continue
            
            # Combine quantities if present
            total_qty = sum(ing.quantity for ing in group_ingredients if ing.quantity)
            
            # Use most common unit
            units = [ing.unit for ing in group_ingredients if ing.unit]
            common_unit = max(set(units), key=units.count) if units else None
            
            # Combine timestamps
            all_timestamps = []
            for ing in group_ingredients:
                all_timestamps.extend(ing.timestamps)
            
            # Use highest confidence
            max_conf = max(ing.confidence for ing in group_ingredients)
            
            # Prefer non-visual source
            sources = [ing.source for ing in group_ingredients]
            if 'audio' in sources:
                source = 'merged'
            elif 'ocr' in sources:
                source = 'merged'
            else:
                source = group_ingredients[0].source
            
            # Create merged ingredient
            merged_ing = Ingredient(
                name=group_name,
                quantity=total_qty if total_qty > 0 else None,
                unit=common_unit,
                source=source,
                confidence=max_conf,
                timestamps=sorted(set(all_timestamps)),
                alternative_note=next((ing.alternative_note for ing in group_ingredients if ing.alternative_note), None),
            )
            merged.append(merged_ing)
        
        return sorted(merged, key=lambda x: x.name)
    
    def save_output(self, recipe: Recipe, output_path: str, format: str = 'json'):
        """
        Save recipe to file.
        
        Args:
            recipe: Recipe to save
            output_path: Output file path
            format: Output format (json, markdown, text)
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == 'json':
            with open(output_path, 'w') as f:
                json.dump(recipe.to_dict(), f, indent=2)
            logger.info(f"Saved recipe as JSON: {output_path}")
        
        elif format == 'markdown':
            # Will implement in Phase 4
            raise NotImplementedError("Markdown format not yet implemented")
        
        elif format == 'text':
            # Will implement in Phase 4
            raise NotImplementedError("Text format not yet implemented")
        
        else:
            raise ValueError(f"Unknown format: {format}")
