"""
Runs the LHDiff pipeline (Steps 1–5) on one pair of files:
    dataset/sample/old_file1.txt
    dataset/sample/new_file1.txt

This simplified version is only for testing the pipeline.
"""


from preprocess import preproc_lines  
from detect_unchanged import detect_unchanged        
from generate_candidates import generate_candidate_set 
from resolve_conflicts import resolve_conflicts     
from detect_line_splits import detect_line_splits   


#Load lines from file

def load_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.readlines()


def run_lhdiff(old_path, new_path):
    print(f"\nRunning LHDiff on sample files:")
    print(f"  OLD → {old_path}")
    print(f"  NEW → {new_path}")

    #Load file contents
    old_raw = load_file(old_path)
    new_raw = load_file(new_path)

    print("\nStep 1: Preprocessing...")
    old = preproc_lines(old_raw)
    new = preproc_lines(new_raw)
    print("Old preprocessed:", old)
    print("New preprocessed:", new)

    print("\nStep 2: Detect unchanged lines")
    unchanged = detect_unchanged(old, new)
    print("Unchanged lines:", unchanged)

    print("\nStep 3: Generate candidate sets")
    candidates = generate_candidate_set(old, new)
    print("Candidate sets:", candidates)

    print("\nStep 4: Resolve conflicts")
    resolved = resolve_conflicts(old, new, candidates)
    print("Resolved matches:", resolved)

    print("\nStep 5: Detect line splits")
    final_map = detect_line_splits(old, new, resolved)

    print("\nFINAL MAPPING:")
    for old_idx, new_idx in final_map.items():
        print(f"  {old_idx} → {new_idx}")

    return final_map


if __name__ == "__main__":
    #Using sample dataset
    old_file = "dataset/sample/old_file1.txt"
    new_file = "dataset/sample/new_file1.txt"

    run_lhdiff(old_file, new_file)
