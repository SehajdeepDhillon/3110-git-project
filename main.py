"""
Main LHDiff pipeline: Runs all 5 steps to map lines between file versions.

Function: lhdiff(old_file, new_file) -> dict
    Returns final mapping: {left_idx: right_idx} or {left_idx: [right_idx1, right_idx2, ...]}
"""

from preprocess import preprocess_lines  
from detect_unchanged import detect_unchanged        
from generate_candidates import generate_candidate_set 
from resolve_conflicts import resolve_conflicts     
from detect_line_splits import detect_line_splits   

#Load lines from file
def load_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.readlines()

def lhdiff(old_file: str, new_file: str) -> dict:
    # Load file contents
    old_raw = load_file(old_file)
    new_raw = load_file(new_file)

    print("\nStep 1: Preprocessing...")
    old = preprocess_lines(old_raw)
    new = preprocess_lines(new_raw)
    print(f"Preprocessed: {len(old)} old lines, {len(new)} new lines")

    print("\nStep 2: Detect unchanged lines")
    unchanged, deleted, added = detect_unchanged(old, new)
    print(f"Unchanged: {len(unchanged)} pairs")
    print(f"Deleted: {len(deleted)} lines")
    print(f"Added: {len(added)} lines")

    print("\nStep 3: Generate candidate sets")
    candidates = generate_candidate_set(old, new, k=15)
    print(f"Generated {len(candidates)} candidate sets")

    print("\nStep 4: Resolve conflicts")
    resolved = resolve_conflicts(old, new, candidates, threshold=0.5)
    print(f"Resolved: {len(resolved)} matches")

    print("\nStep 5: Detect line splits")
    final_map = detect_line_splits(resolved, old, new)

    print("\nFINAL MAPPING:")
    for left_idx in sorted(final_map.keys()):
        right_val = final_map[left_idx]
        if isinstance(right_val, list):
            # Multiple right lines (line split)
            right_str = "{" + ",".join(map(str, right_val)) + "}"
        else:
            # Single right line
            right_str = str(right_val)
        print(f"  {left_idx} → {right_str}")

    return final_map


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 3:
        old_file = sys.argv[1]
        new_file = sys.argv[2]
    else:
        print("Usage: python main.py <old_file> <new_file>")
        print("Example: python main.py datasets/custom/file01/old.java datasets/custom/file01/new.java")
        sys.exit(1)
    
    print(f"\nRunning LHDiff:")
    print(f"  OLD → {old_file}")
    print(f"  NEW → {new_file}")
    
    result = lhdiff(old_file, new_file)

