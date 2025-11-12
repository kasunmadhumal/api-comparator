import json
from typing import Dict, Any, List, Tuple
from deepdiff import DeepDiff

class ResponseComparator:
    def compare_responses(self, response1: Dict, response2: Dict) -> Dict[str, Any]:
        """
        Compare two JSON responses and identify differences
        
        Args:
            response1: First response (before change)
            response2: Second response (after change)
        
        Returns:
            Dictionary containing comparison results
        """
        # Check if responses are identical
        identical = response1 == response2
        
        if identical:
            return {
                "identical": True,
                "differences": [],
                "summary": "Responses are identical"
            }
        
        # Use DeepDiff for detailed comparison
        diff = DeepDiff(response1, response2, ignore_order=False, verbose_level=2)
        
        differences = []
        
        # Values changed
        if 'values_changed' in diff:
            for path, change in diff['values_changed'].items():
                differences.append(
                    f"Value changed at {path}: {change['old_value']} → {change['new_value']}"
                )
        
        # Items added
        if 'dictionary_item_added' in diff:
            for item in diff['dictionary_item_added']:
                differences.append(f"New field added: {item}")
        
        # Items removed
        if 'dictionary_item_removed' in diff:
            for item in diff['dictionary_item_removed']:
                differences.append(f"Field removed: {item}")
        
        # Type changes
        if 'type_changes' in diff:
            for path, change in diff['type_changes'].items():
                differences.append(
                    f"Type changed at {path}: {change['old_type']} → {change['new_type']}"
                )
        
        # Items added to lists
        if 'iterable_item_added' in diff:
            for item in diff['iterable_item_added']:
                differences.append(f"List item added: {item}")
        
        # Items removed from lists
        if 'iterable_item_removed' in diff:
            for item in diff['iterable_item_removed']:
                differences.append(f"List item removed: {item}")
        
        return {
            "identical": False,
            "differences": differences,
            "detailed_diff": diff,
            "summary": f"Found {len(differences)} difference(s)"
        }
    
    def compare_structure(self, response1: Dict, response2: Dict) -> Dict[str, Any]:
        """
        Compare only the structure (keys) of two responses, ignoring values
        """
        def get_structure(obj, prefix=""):
            """Recursively get all keys in nested structure"""
            keys = set()
            if isinstance(obj, dict):
                for key, value in obj.items():
                    full_key = f"{prefix}.{key}" if prefix else key
                    keys.add(full_key)
                    if isinstance(value, (dict, list)):
                        keys.update(get_structure(value, full_key))
            elif isinstance(obj, list) and obj:
                keys.update(get_structure(obj[0], f"{prefix}[0]"))
            return keys
        
        structure1 = get_structure(response1)
        structure2 = get_structure(response2)
        
        added_keys = structure2 - structure1
        removed_keys = structure1 - structure2
        common_keys = structure1 & structure2
        
        return {
            "structure_identical": structure1 == structure2,
            "added_keys": list(added_keys),
            "removed_keys": list(removed_keys),
            "common_keys": list(common_keys)
        }
    
    def get_key_differences(self, response1: Dict, response2: Dict, 
                           keys_to_check: List[str]) -> Dict[str, Any]:
        """
        Check specific keys for differences
        
        Args:
            response1: First response
            response2: Second response
            keys_to_check: List of keys to compare (supports nested keys with dot notation)
        
        Returns:
            Dictionary of differences for specified keys
        """
        def get_nested_value(obj, key_path):
            """Get value from nested dictionary using dot notation"""
            keys = key_path.split('.')
            value = obj
            for key in keys:
                if isinstance(value, dict):
                    value = value.get(key)
                else:
                    return None
            return value
        
        differences = {}
        for key in keys_to_check:
            value1 = get_nested_value(response1, key)
            value2 = get_nested_value(response2, key)
            
            if value1 != value2:
                differences[key] = {
                    "before": value1,
                    "after": value2,
                    "changed": True
                }
            else:
                differences[key] = {
                    "value": value1,
                    "changed": False
                }
        
        return differences
    
    def calculate_similarity_score(self, response1: Dict, response2: Dict) -> float:
        """
        Calculate a similarity score between 0 and 1
        
        Returns:
            Float between 0 (completely different) and 1 (identical)
        """
        if response1 == response2:
            return 1.0
        
        # Convert to JSON strings for comparison
        str1 = json.dumps(response1, sort_keys=True)
        str2 = json.dumps(response2, sort_keys=True)
        
        # Simple character-based similarity
        len1, len2 = len(str1), len(str2)
        max_len = max(len1, len2)
        
        if max_len == 0:
            return 1.0
        
        # Calculate Levenshtein distance (simplified)
        matching_chars = sum(c1 == c2 for c1, c2 in zip(str1, str2))
        similarity = matching_chars / max_len
        
        return round(similarity, 2)
