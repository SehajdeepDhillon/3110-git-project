"""
Step 5 of LHDiff: Detect Line Splits.
If a line from left file is matched to multiple lines in right file,
check if concatenating right lines improves similarity.
"""

from typing import List, Dict, Union
from generate_candidates import content_similarity


def detect_line_splits(mapping: Dict[int, int], left_lines: List[str], right_lines: List[str]) -> Dict[int, Union[int, List[int]]]:
    """
    Detect line splits by checking if concatenating multiple right lines
    improves similarity to a left line.
    
    Algorithm:
    - For each left line that maps to a right line, check if concatenating
      adjacent right lines improves similarity
    - Compute normalized Levenshtein distance incrementally
    - If similarity increases → keep adding lines
    - If similarity decreases → stop
    
    Args:
        mapping: Dictionary {left_idx: right_idx} from Step 4
        left_lines: List of lines from old file
        right_lines: List of lines from new file
    
    Returns:
        Updated mapping allowing one left line to map to multiple right lines:
        {left_idx: right_idx} or {left_idx: [right_idx1, right_idx2, ...]}
    """
    final_mapping = {}
    
    # Group mappings by left index (in case of duplicates, take first)
    left_to_rights = {}
    for left_idx, right_idx in mapping.items():
        if left_idx not in left_to_rights:
            left_to_rights[left_idx] = []
        left_to_rights[left_idx].append(right_idx)
    
    for left_idx, right_indices in left_to_rights.items():
        if left_idx >= len(left_lines):
            continue
        
        left_line = left_lines[left_idx]
        
        # Start with the first candidate right line
        if not right_indices:
            continue
        
        start_right_idx = right_indices[0]
        best_similarity = -1
        best_end_idx = start_right_idx
        
        # Try concatenating lines starting from start_right_idx
        # Check forward (increasing indices)
        current_text = ""
        for end_idx in range(start_right_idx, len(right_lines)):
            if end_idx == start_right_idx:
                current_text = right_lines[end_idx]
            else:
                current_text += " " + right_lines[end_idx]
            
            # Compute similarity with concatenated text
            sim = content_similarity(left_line, current_text)
            
            # If similarity increases, keep this as best
            if sim > best_similarity:
                best_similarity = sim
                best_end_idx = end_idx
            # If similarity decreases, stop (we've found the optimal split)
            elif sim < best_similarity:
                break
        
        # Determine the final mapping
        if best_end_idx == start_right_idx:
            # Single line match
            final_mapping[left_idx] = start_right_idx
        else:
            # Multiple line match
            final_mapping[left_idx] = list(range(start_right_idx, best_end_idx + 1))
    
    return final_mapping

