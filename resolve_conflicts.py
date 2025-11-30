"""
resolve_conflicts.py
Step 4 of LHDiff:
"""

import math
import Levenshtein
import re
from collections import Counter


def levenshtein_similarity(a, b):

    #Compute normalized levenshtein similarity.
    max_len = max(len(a), len(b))

    #Two empty lines = identical
    if max_len == 0:
        return 1.0

    dist = Levenshtein.distance(a, b)

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

    #Magnitudes of the vectors
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



def resolve_conflicts(old_lines, new_lines, candidates, threshold=0.7):
    """
    For each old line:
    1 Compute content similarity using levenshtein
    2 Compute context similarity using cosine
    3 Compute combined similarity:0.6 * content + 0.4 * context
    4 Choose the best candidate
    5 Only keep if above the threshold 
    """

    final_mapping = {}

    for old_idx, cand_list in candidates.items():

        #Skip old lines with no candidates
        if not cand_list:
            continue

        old_line = old_lines[old_idx]
        old_ctx = get_context(old_lines, old_idx)

        best_score = -1
        best_match = None

        #Check each candidate new line
        for new_idx in cand_list:

            if new_idx < 0 or new_idx >= len(new_lines):
                continue

            new_line = new_lines[new_idx]
            new_ctx = get_context(new_lines, new_idx)

            content_sim = levenshtein_similarity(old_line, new_line)
            ctx_sim = cosine_similarity(old_ctx, new_ctx)

            combined = 0.6 * content_sim + 0.4 * ctx_sim

            #Choose the best match
            if combined > best_score:
                best_score = combined
                best_match = new_idx

        #Keep match only if similarity is strong enough
        if best_score >= threshold:
            final_mapping[old_idx] = best_match

    return final_mapping
