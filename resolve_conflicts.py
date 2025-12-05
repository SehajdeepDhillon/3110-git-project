"""
resolve_conflicts.py
Step 4 of LHDiff: Resolve Conflicts using textual similarity refinement.
"""
import math
import re
from collections import Counter
from typing import List, Dict


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Compute Levenshtein distance between two strings.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def levenshtein_similarity(a, b):
    """Compute normalized levenshtein similarity."""
    max_len = max(len(a), len(b))
    # Two empty lines = identical
    if max_len == 0:
        return 1.0
    dist = levenshtein_distance(a, b)
    return 1 - (dist / max_len)

def cosine_similarity(ctx1, ctx2):
    #Compute cosine similarity between two context windows.
    def tokenize(lines):
    #Convert multiple lines into individual tokens
        words = []
        for line in lines:
            tokens = re.findall(r"\w+|[^\w\s]", line)
            words.extend(tokens)
        return words
    words1 = tokenize(ctx1)
    words2 = tokenize(ctx2)
    #if either context is empty then similarity is low
    if not words1 or not words2:
        return 0.0
    #convert word lists
    c1 = Counter(words1)
    c2 = Counter(words2)
    dot = sum(c1[w] * c2[w] for w in c1)
    mag1 = math.sqrt(sum(v*v for v in c1.values()))
    mag2 = math.sqrt(sum(v*v for v in c2.values()))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)


def get_context(lines, index, top=4, bottom=4):
    #take up to 4 lines above and 4 lines below the target line.
    start = max(0, index - top)
    end = min(len(lines), index + bottom + 1)
    return lines[start:index] + lines[index+1:end]


def resolve_conflicts(left_lines: List[str], right_lines: List[str], candidate_set: Dict[int, List[int]], threshold: float = 0.6) -> Dict[int, int]:
    """
    For each old line:
    1 Compute content similarity using levenshtein
    2 Compute context similarity using cosine
    3 Compute combined similarity:0.6 * content + 0.4 * context
    4 Choose the best candidate
    5 Only keep if above the threshold 
    """
    """
    For each left line:
    1. Evaluate all candidates using actual content + context similarity
    2. Choose the one with highest score above threshold
    3. Return mapping dict: { left_idx: right_idx }
    
    Args:
        left_lines: List of lines from old file
        right_lines: List of lines from new file
        candidate_set: Dictionary {left_idx: [candidate_right_indices]}
        threshold: Minimum similarity score (default 0.5)
    
    Returns:
        Dictionary mapping {left_idx: right_idx}
    """
    final_mapping = {}
    for left_idx, cand_list in candidate_set.items():
        # Skip left lines with no candidates
        if not cand_list:
            continue
        left_line = left_lines[left_idx]
        left_ctx = get_context(left_lines, left_idx)
        best_score = -1
        best_match = None
        # Check each candidate right line
        for right_idx in cand_list:
            if right_idx < 0 or right_idx >= len(right_lines):
                continue
            right_line = right_lines[right_idx]
            right_ctx = get_context(right_lines, right_idx)
            content_sim = levenshtein_similarity(left_line, right_line)
            ctx_sim = cosine_similarity(left_ctx, right_ctx)
            combined = 0.6 * content_sim + 0.4 * ctx_sim
            # Choose the best match
            if combined > best_score:
                best_score = combined
                best_match = right_idx
        # Keep match only if similarity is strong enough
        if best_score >= threshold:
            final_mapping[left_idx] = best_match
    return final_mapping

