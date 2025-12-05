"""
Step 3 of LHDiff: Similarity scoring + SimHash-based candidate generation.
"""

import re
import hashlib
from typing import List, Dict
from collections import Counter


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


def content_similarity(line_a: str, line_b: str) -> float:
    """
    Return similarity between 0 and 1 using:
    sim = 1 - (lev_distance / max_length)
    """
    if not line_a and not line_b:
        return 1.0
    
    max_length = max(len(line_a), len(line_b))
    if max_length == 0:
        return 1.0
    
    lev_distance = levenshtein_distance(line_a, line_b)
    return 1.0 - (lev_distance / max_length)


def tokenize_line(line: str) -> List[str]:
    """
    Tokenize a line into tokens (words, operators, etc.).
    Simple tokenization: split on whitespace and punctuation.
    """
    # Split on whitespace and keep punctuation as separate tokens
    tokens = re.findall(r'\w+|[^\w\s]', line)
    return [token.lower() for token in tokens if token.strip()]


def build_bag_of_words(context: List[str]) -> Counter:
    """
    Build a bag-of-words vector from a context (list of lines).
    """
    all_tokens = []
    for line in context:
        tokens = tokenize_line(line)
        all_tokens.extend(tokens)
    return Counter(all_tokens)


def cosine_similarity(vec1: Counter, vec2: Counter) -> float:
    """
    Compute cosine similarity between two bag-of-words vectors.
    """
    # Get all unique tokens
    all_tokens = set(vec1.keys()) | set(vec2.keys())
    
    if not all_tokens:
        return 1.0
    
    # Compute dot product
    dot_product = sum(vec1[token] * vec2[token] for token in all_tokens)
    
    # Compute magnitudes
    magnitude1 = sum(count ** 2 for count in vec1.values()) ** 0.5
    magnitude2 = sum(count ** 2 for count in vec2.values()) ** 0.5
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)


def context_similarity(context_a: List[str], context_b: List[str]) -> float:
    """
    Tokenize each line, build bag-of-words vectors, 
    return cosine similarity (0–1).
    """
    vec_a = build_bag_of_words(context_a)
    vec_b = build_bag_of_words(context_b)
    return cosine_similarity(vec_a, vec_b)


def simhash(tokens: List[str], hashbits: int = 32) -> int:
    """
    Generate a SimHash integer from token list.
    
    Steps:
    1. Hash each token
    2. Build bit-weight vector
    3. Finalize signature
    """
    v = [0] * hashbits
    
    for token in tokens:
        # Hash the token
        h = int(hashlib.md5(token.encode('utf-8')).hexdigest(), 16)
        
        # Build bit-weight vector
        for i in range(hashbits):
            bitmask = 1 << i
            if h & bitmask:
                v[i] += 1
            else:
                v[i] -= 1
    
    # Finalize signature: set bit to 1 if weight > 0, else 0
    fingerprint = 0
    for i in range(hashbits):
        if v[i] > 0:
            fingerprint |= 1 << i
    
    return fingerprint


def hamming_distance(hash1: int, hash2: int) -> int:
    """
    Return number of differing bits between two integers.
    """
    xor = hash1 ^ hash2
    distance = 0
    while xor:
        distance += 1
        xor &= xor - 1  # Clear the least significant bit
    return distance


def combined_similarity(content_sim: float, context_sim: float) -> float:
    """
    Combined similarity score:
    combined = 0.6 * content_similarity + 0.4 * context_similarity
    """
    return 0.6 * content_sim + 0.4 * context_sim


def get_context(lines: List[str], index: int, top: int = 4, bottom: int = 4) -> List[str]:
    """
    Get context around a line: top N lines + bottom N lines.
    """
    start = max(0, index - top)
    end = min(len(lines), index + bottom + 1)
    return lines[start:end]


def generate_candidate_set(left_lines: List[str], right_lines: List[str], k: int = 15) -> Dict:
    """
    For each left-line, produce the top-k closest right-lines based on SimHash Hamming distance.
    
    Steps:
    1. Compute content SimHash for all left and right lines.
    2. For each left hash, compute Hamming distance to every right hash.
    3. Choose the k smallest distances.
    4. Output as dictionary.
    
    Returns:
    {
        left_index: [candidate_right_indices]
    }
    """
    # Tokenize and compute SimHash for all lines
    left_hashes = []
    right_hashes = []
    
    for line in left_lines:
        tokens = tokenize_line(line)
        left_hashes.append(simhash(tokens))
    
    for line in right_lines:
        tokens = tokenize_line(line)
        right_hashes.append(simhash(tokens))
    
    # Generate candidate sets
    candidates = {}
    
    for left_idx, left_hash in enumerate(left_hashes):
        # Compute Hamming distances to all right hashes
        distances = []
        for right_idx, right_hash in enumerate(right_hashes):
            dist = hamming_distance(left_hash, right_hash)
            distances.append((dist, right_idx))
        
        # Sort by distance and take top k
        distances.sort(key=lambda x: x[0])
        top_k_indices = [idx for _, idx in distances[:k]]
        candidates[left_idx] = top_k_indices
    
    return candidates

