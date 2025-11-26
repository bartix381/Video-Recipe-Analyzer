"""JSON schema validation utilities."""
import json
import jsonschema
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class SchemaValidator:
    """JSON schema validator for recipe output."""
    
    def __init__(self, schema_path: str):
        """
        Initialize validator with schema file.
        
        Args:
            schema_path: Path to JSON schema file
        """
        self.schema_path = Path(schema_path)
        self.schema = self._load_schema()
    
    def _load_schema(self) -> Dict[str, Any]:
        """Load JSON schema from file."""
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")
        
        with open(self.schema_path, 'r') as f:
            schema = json.load(f)
        
        logger.info(f"Loaded schema from {self.schema_path}")
        return schema
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate data against schema.
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid, False otherwise
            
        Raises:
            jsonschema.ValidationError: If validation fails
        """
        try:
            jsonschema.validate(instance=data, schema=self.schema)
            logger.debug("Schema validation passed")
            return True
        except jsonschema.ValidationError as e:
            logger.error(f"Schema validation failed: {e.message}")
            raise
    
    def validate_safe(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate data without raising exceptions.
        
        Args:
            data: Data to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            jsonschema.validate(instance=data, schema=self.schema)
            return True, None
        except jsonschema.ValidationError as e:
            return False, str(e.message)
        except Exception as e:
            return False, f"Validation error: {str(e)}"


def load_recipe_schema() -> SchemaValidator:
    """
    Load the recipe output schema.
    
    Returns:
        SchemaValidator for recipe schema
    """
    schema_path = Path(__file__).parent.parent.parent / "specs" / "001-recipe-video-extraction" / "contracts" / "recipe_schema.json"
    return SchemaValidator(str(schema_path))


def validate_recipe(recipe_data: Dict[str, Any]) -> bool:
    """
    Validate recipe data against schema.
    
    Args:
        recipe_data: Recipe dictionary to validate
        
    Returns:
        True if valid
        
    Raises:
        jsonschema.ValidationError: If validation fails
    """
    validator = load_recipe_schema()
    return validator.validate(recipe_data)
