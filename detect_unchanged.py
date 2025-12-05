"""
Step 2 of LHDiff: Detect Unchanged Lines using Unix diff algorithm.
Uses Longest Common Subsequence (LCS) via difflib.
"""

import difflib
from typing import List, Tuple


def detect_unchanged(left_lines: List[str], right_lines: List[str]) -> Tuple[List[Tuple[int, int]], List[int], List[int]]:
    """
    Detect unchanged lines between two file versions using Unix diff algorithm.
    
    Uses Longest Common Subsequence to find matching lines.
    
    Args:
        left_lines: List of lines from old file
        right_lines: List of lines from new file
    
    Returns:
        Tuple containing:
        - unchanged: list of (left_idx, right_idx) pairs for unchanged lines
        - deleted: list of left_idx for deleted lines
        - added: list of right_idx for added lines
    """
    # Use difflib SequenceMatcher to find LCS
    matcher = difflib.SequenceMatcher(None, left_lines, right_lines, autojunk=False)
    
    unchanged = []
    deleted = []
    added = []
    
    # Track which right indices have been matched
    matched_right = set()
    
    # Process all opcodes from the diff
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            # These lines are unchanged
            for offset in range(i2 - i1):
                left_idx = i1 + offset
                right_idx = j1 + offset
                unchanged.append((left_idx, right_idx))
                matched_right.add(right_idx)
        
        elif tag == 'delete':
            # Lines deleted from left file
            for left_idx in range(i1, i2):
                deleted.append(left_idx)
        
        elif tag == 'insert':
            # Lines added to right file
            for right_idx in range(j1, j2):
                if right_idx not in matched_right:
                    added.append(right_idx)
        
        elif tag == 'replace':
            # Lines replaced (treated as delete + insert)
            for left_idx in range(i1, i2):
                deleted.append(left_idx)
            for right_idx in range(j1, j2):
                if right_idx not in matched_right:
                    added.append(right_idx)
    
    return unchanged, deleted, added

