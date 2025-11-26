"""Ingredient parser for extracting ingredient names from text."""
import re
import logging
from typing import List, Optional
from thefuzz import fuzz
from ..entities import Ingredient

logger = logging.getLogger(__name__)


class IngredientParser:
    """Parse ingredient names from text."""
    
    # Common ingredient keywords for detection
    COMMON_INGREDIENTS = [
        # Staples
        'flour', 'sugar', 'salt', 'pepper', 'oil', 'butter', 'ghee', 'eggs', 'milk',
        'water', 'cream', 'cheese', 'bread', 'rice', 'pasta',
        
        # Vegetables
        'onion', 'garlic', 'tomato', 'potato', 'carrot', 'celery', 'bell pepper',
        'mushroom', 'spinach', 'lettuce', 'cucumber', 'broccoli', 'zucchini',
        
        # Proteins
        'chicken', 'beef', 'pork', 'fish', 'shrimp', 'bacon', 'sausage',
        'turkey', 'lamb', 'tofu', 'paneer',
        
        # Indian Ingredients
        'paneer', 'ghee', 'masala', 'curry', 'turmeric', 'cumin', 'coriander',
        'garam masala', 'cardamom', 'cloves', 'bay leaf', 'kasuri methi',
        'fenugreek', 'mustard seeds', 'curry leaves', 'asafoetida', 'hing',
        'chili', 'chilli', 'red chili', 'green chili', 'ginger paste', 'garlic paste',
        
        # Herbs & Spices
        'basil', 'oregano', 'thyme', 'rosemary', 'parsley', 'cilantro',
        'paprika', 'cumin', 'cinnamon', 'vanilla', 'ginger',
        
        # Baking
        'baking powder', 'baking soda', 'yeast', 'cocoa', 'chocolate',
        'honey', 'maple syrup', 'vanilla extract',
        
        # Condiments
        'soy sauce', 'vinegar', 'mustard', 'ketchup', 'mayonnaise',
        'hot sauce', 'worcestershire sauce',
        
        # Fruits
        'lemon', 'lime', 'orange', 'apple', 'banana', 'strawberry',
        'blueberry', 'raspberry', 'avocado',
    ]
    
    # Words to remove from ingredient names
    STOP_WORDS = {
        'fresh', 'dried', 'frozen', 'canned', 'chopped', 'diced', 'sliced',
        'minced', 'grated', 'shredded', 'whole', 'ground', 'crushed',
        'optional', 'to taste', 'as needed', 'for serving', 'for garnish',
        'large', 'small', 'medium', 'extra', 'about', 'approximately',
    }
    
    def __init__(self, fuzzy_threshold: int = 85):
        """
        Initialize ingredient parser.
        
        Args:
            fuzzy_threshold: Threshold for fuzzy matching (0-100)
        """
        self.fuzzy_threshold = fuzzy_threshold
        logger.info(f"Initialized IngredientParser with fuzzy_threshold={fuzzy_threshold}")
    
    def parse(self, text: str, source: str = "unknown", confidence: float = 0.0) -> List[Ingredient]:
        """
        Parse ingredients from text.
        
        Args:
            text: Text containing ingredient mentions
            source: Source of the text (visual, ocr, audio)
            confidence: Confidence score for the extraction
            
        Returns:
            List of Ingredient entities
        """
        if not text:
            return []
        
        ingredients = []
        text_lower = text.lower()
        
        # Look for common ingredients in text
        for ingredient_name in self.COMMON_INGREDIENTS:
            if ingredient_name in text_lower:
                # Extract context around the ingredient
                pattern = rf'.{{0,50}}\b{re.escape(ingredient_name)}\b.{{0,50}}'
                matches = re.finditer(pattern, text_lower)
                
                for match in matches:
                    context = match.group(0).strip()
                    
                    # Create ingredient entry
                    ingredients.append(Ingredient(
                        name=ingredient_name,
                        source=source,
                        confidence=confidence,
                        raw_text=context,
                    ))
        
        return ingredients
    
    def normalize_name(self, name: str) -> str:
        """
        Normalize ingredient name.
        
        Args:
            name: Ingredient name
            
        Returns:
            Normalized name
        """
        if not name:
            return name
        
        # Convert to lowercase
        name = name.lower().strip()
        
        # Remove stop words
        words = name.split()
        filtered_words = [w for w in words if w not in self.STOP_WORDS]
        
        # Rejoin
        name = ' '.join(filtered_words) if filtered_words else name
        
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def are_similar(self, name1: str, name2: str) -> bool:
        """
        Check if two ingredient names are similar using fuzzy matching.
        
        Args:
            name1: First ingredient name
            name2: Second ingredient name
            
        Returns:
            True if names are similar
        """
        if not name1 or not name2:
            return False
        
        # Normalize both names
        norm1 = self.normalize_name(name1)
        norm2 = self.normalize_name(name2)
        
        # Check exact match
        if norm1 == norm2:
            return True
        
        # Fuzzy match
        ratio = fuzz.ratio(norm1, norm2)
        return ratio >= self.fuzzy_threshold
    
    def detect_substitution(self, text: str) -> Optional[str]:
        """
        Detect ingredient substitutions (e.g., "butter or oil").
        
        Args:
            text: Text to check for substitutions
            
        Returns:
            Substitution note if found, None otherwise
        """
        text_lower = text.lower()
        
        # Look for "or" patterns
        or_pattern = r'\b(\w+)\s+or\s+(\w+)\b'
        match = re.search(or_pattern, text_lower)
        
        if match:
            alt1, alt2 = match.groups()
            return f"or {alt2}"
        
        return None
