"""Quantity parser for ingredient amounts and units."""
import re
import logging
from typing import Optional, Tuple
from fractions import Fraction

logger = logging.getLogger(__name__)


class QuantityParser:
    """Parse quantities and units from text."""
    
    # Common unit mappings (normalize to standard forms)
    UNIT_MAPPINGS = {
        # Volume
        'cup': 'cup', 'cups': 'cup', 'c': 'cup',
        'tablespoon': 'tbsp', 'tablespoons': 'tbsp', 'tbsp': 'tbsp', 'tbs': 'tbsp', 'T': 'tbsp',
        'teaspoon': 'tsp', 'teaspoons': 'tsp', 'tsp': 'tsp', 't': 'tsp',
        'milliliter': 'ml', 'milliliters': 'ml', 'ml': 'ml', 'mL': 'ml',
        'liter': 'l', 'liters': 'l', 'l': 'l', 'L': 'l',
        'fluid ounce': 'fl oz', 'fluid ounces': 'fl oz', 'fl oz': 'fl oz', 'floz': 'fl oz',
        'pint': 'pint', 'pints': 'pint', 'pt': 'pint',
        'quart': 'quart', 'quarts': 'quart', 'qt': 'quart',
        'gallon': 'gallon', 'gallons': 'gallon', 'gal': 'gallon',
        
        # Weight
        'gram': 'g', 'grams': 'g', 'g': 'g', 'gr': 'g',
        'kilogram': 'kg', 'kilograms': 'kg', 'kg': 'kg', 'kilo': 'kg', 'kilos': 'kg',
        'ounce': 'oz', 'ounces': 'oz', 'oz': 'oz',
        'pound': 'lb', 'pounds': 'lb', 'lb': 'lb', 'lbs': 'lb',
        
        # Count
        'piece': 'piece', 'pieces': 'piece', 'pc': 'piece', 'pcs': 'piece',
        'clove': 'clove', 'cloves': 'clove',
        'slice': 'slice', 'slices': 'slice',
        'pinch': 'pinch', 'pinches': 'pinch',
        'dash': 'dash', 'dashes': 'dash',
        'bunch': 'bunch', 'bunches': 'bunch',
        'can': 'can', 'cans': 'can',
        'package': 'package', 'packages': 'package', 'pkg': 'package', 'pkgs': 'package',
    }
    
    # Patterns for parsing quantities
    QUANTITY_PATTERNS = [
        # Fractions: "1/2", "1 1/2"
        r'(\d+\s+)?(\d+)/(\d+)',
        # Decimals: "1.5", "0.5"
        r'(\d+\.?\d*)',
        # Word numbers: "one", "two", "three"
        r'\b(one|two|three|four|five|six|seven|eight|nine|ten|half|quarter)\b',
    ]
    
    WORD_TO_NUMBER = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
        'half': 0.5, 'quarter': 0.25,
    }
    
    def parse(self, text: str) -> Tuple[Optional[float], Optional[str], str]:
        """
        Parse quantity and unit from text.
        
        Args:
            text: Text containing quantity and unit (e.g., "2 cups flour")
            
        Returns:
            Tuple of (quantity, unit, remaining_text)
        """
        if not text:
            return None, None, text
        
        text_lower = text.lower().strip()
        quantity = None
        unit = None
        remaining = text
        
        # Try to extract quantity
        for pattern in self.QUANTITY_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                quantity = self._extract_number(match)
                if quantity is not None:
                    # Remove matched quantity from text
                    remaining = text[:match.start()] + text[match.end():]
                    break
        
        # Try to extract unit
        remaining_lower = remaining.lower().strip()
        for unit_pattern, normalized_unit in self.UNIT_MAPPINGS.items():
            # Match unit as whole word
            if re.search(r'\b' + re.escape(unit_pattern) + r'\b', remaining_lower):
                unit = normalized_unit
                # Remove unit from remaining text
                remaining = re.sub(
                    r'\b' + re.escape(unit_pattern) + r'\b',
                    '',
                    remaining,
                    flags=re.IGNORECASE
                ).strip()
                break
        
        # Clean up remaining text
        remaining = re.sub(r'\s+', ' ', remaining).strip()
        
        return quantity, unit, remaining
    
    def _extract_number(self, match: re.Match) -> Optional[float]:
        """Extract numeric value from regex match."""
        text = match.group(0).lower()
        
        # Try word numbers
        for word, value in self.WORD_TO_NUMBER.items():
            if word in text:
                return value
        
        # Try fractions
        if '/' in text:
            try:
                # Handle mixed fractions like "1 1/2"
                parts = text.split()
                if len(parts) == 2:
                    whole = float(parts[0])
                    frac = Fraction(parts[1])
                    return whole + float(frac)
                else:
                    frac = Fraction(text.strip())
                    return float(frac)
            except:
                pass
        
        # Try decimal
        try:
            return float(text.strip())
        except:
            return None
    
    def normalize_unit(self, unit: str) -> str:
        """
        Normalize unit to standard form.
        
        Args:
            unit: Unit string
            
        Returns:
            Normalized unit
        """
        if not unit:
            return unit
        
        return self.UNIT_MAPPINGS.get(unit.lower(), unit)
