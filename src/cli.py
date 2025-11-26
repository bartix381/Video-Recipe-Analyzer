"""Command-line interface for recipe video extraction."""
import click
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Recipe Video Extraction - Extract ingredients and steps from recipe videos."""
    pass


@cli.command()
@click.argument('url')
@click.option('--output', '-o', default='recipe.json', help='Output file path')
@click.option('--format', '-f', type=click.Choice(['json', 'markdown', 'text']), default='json', help='Output format')
@click.option('--config', '-c', help='Path to custom config file')
@click.option('--fps', type=float, help='Frame extraction rate (overrides config)')
@click.option('--whisper-model', type=click.Choice(['tiny', 'base', 'small', 'medium', 'large']), help='Whisper model size')
@click.option('--detector', type=click.Choice(['yolov8n', 'yolov8s', 'yolov8m', 'yolov8l', 'yolov8x']), help='YOLO model')
def extract(url, output, format, config, fps, whisper_model, detector):
    """Extract recipe from video URL."""
    logger.info(f"Extracting recipe from: {url}")
    logger.info(f"Output: {output} (format: {format})")
    
    try:
        from .utils import load_config
        from .pipeline import RecipePipeline
        
        # Load configuration
        cfg = load_config(config)
        
        # Apply CLI overrides
        if fps:
            cfg.set('frame_extraction.fps', fps)
        if whisper_model:
            cfg.set('transcription.model', whisper_model)
        if detector:
            cfg.set('object_detection.model', f'{detector}.pt')
        
        # Initialize and run pipeline
        pipeline = RecipePipeline(cfg)
        recipe = pipeline.process(url)
        
        # Save output
        pipeline.save_output(recipe, output, format)
        
        logger.info(f"✓ Recipe extracted successfully: {output}")
        logger.info(f"  - Found {len(recipe.ingredients)} ingredients")
        logger.info(f"  - Found {len(recipe.steps)} steps")
        logger.info(f"  - Processing time: {recipe.processing_time:.1f}s")
        
    except Exception as e:
        logger.error(f"✗ Failed to extract recipe: {str(e)}")
        sys.exit(1)


@cli.command()
@click.option('--config', '-c', help='Path to config file to view')
def show_config(config):
    """Show current configuration."""
    try:
        from .utils import load_config
        import yaml
        
        cfg = load_config(config)
        print("\n=== Configuration ===\n")
        print(yaml.dump(cfg.to_dict(), default_flow_style=False))
    
    except Exception as e:
        logger.error(f"Failed to load config: {str(e)}")
        sys.exit(1)


@cli.command()
def cache_info():
    """Show video cache information."""
    try:
        from .utils import load_config, VideoCache
        
        cfg = load_config()
        cache_dir = Path("cache")
        cache_ttl = cfg.get('video.cache_ttl', 86400) // 3600
        
        cache = VideoCache(str(cache_dir), cache_ttl)
        stats = cache.get_stats()
        
        print("\n=== Video Cache Statistics ===\n")
        print(f"Cache directory: {stats['cache_dir']}")
        print(f"Files: {stats['file_count']}")
        print(f"Total size: {stats['total_size_mb']:.1f} MB")
        print(f"TTL: {stats['ttl_hours']:.0f} hours")
    
    except Exception as e:
        logger.error(f"Failed to get cache info: {str(e)}")
        sys.exit(1)


@cli.command()
@click.confirmation_option(prompt='Clear all cached videos?')
def cache_clear():
    """Clear video cache."""
    try:
        from .utils import load_config, VideoCache
        
        cfg = load_config()
        cache_dir = Path("cache")
        cache_ttl = cfg.get('video.cache_ttl', 86400) // 3600
        
        cache = VideoCache(str(cache_dir), cache_ttl)
        count = cache.clear()
        
        print(f"✓ Cleared cache: removed {count} files")
    
    except Exception as e:
        logger.error(f"Failed to clear cache: {str(e)}")
        sys.exit(1)


@cli.command()
def device_info():
    """Show available compute devices."""
    try:
        from .utils import get_device_info
        import json
        
        info = get_device_info()
        
        print("\n=== Available Devices ===\n")
        print(json.dumps(info, indent=2))
        
        # Recommend device
        if info['mps']:
            print("\n✓ Recommended: MPS (Apple Metal)")
        elif info['cuda']:
            print(f"\n✓ Recommended: CUDA ({info['cuda_devices'][0]})")
        else:
            print("\n• Using: CPU")
    
    except Exception as e:
        logger.error(f"Failed to get device info: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    cli()
