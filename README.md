# LHDiff - Language-Independent Hybrid Line Mapping

A language-independent approach for tracking source code lines across file versions.

## Overview

LHDiff implements a 5-step pipeline to map lines between old and new file versions:
1. **Preprocessing**: Normalize lines (lowercase, collapse whitespace, standardize formatting)
2. **Detect Unchanged Lines**: Use Unix diff/LCS to find exact matches
3. **Generate Candidates**: Use SimHash to find top-k similar lines (k=15)
4. **Resolve Conflicts**: Evaluate candidates using content + context similarity
5. **Detect Line Splits**: Identify when one line splits into multiple lines

## Installation

No external dependencies required. Uses only Python standard library (Python 3.7+).

**Requirements:**
- Python 3.7 or higher

## Usage

### Method 1: Command-Line Interface

Run LHDiff on two files:

```bash
python main.py <old_file> <new_file>
```

**Example:**
```bash
python main.py datasets/custom/file01/old.java datasets/custom/file01/new.java
```

**Output Format:**
The tool prints a mapping in the format `old_line-new_line` (1-indexed):
```
1-1 3-3 4-8 5-4 6-6 7-7 9-9 10-10
```

For line splits (one-to-many mappings), the format is:
```
5-{8,9,10}  # Line 5 maps to lines 8, 9, and 10
```

### Method 2: Evaluation on Dataset

Run evaluation on a dataset directory:

```bash
python evaluation/evaluate.py <dataset_path> [output_csv]
```

**Example:**
```bash
python evaluation/evaluate.py datasets/custom results.csv
```

**Output:**
- Prints metrics for each file pair
- Exports results to CSV file (default: `results.csv`)
- Shows summary statistics (average %Correct, %Change, %Spurious, %Eliminate)

**Metrics Explained:**
- **%Correct**: Percentage of ground truth pairs correctly predicted
- **%Change**: Percentage of predicted pairs that differ from truth
- **%Spurious**: Percentage of predicted pairs not in ground truth
- **%Eliminate**: Percentage of ground truth pairs not predicted

## Project Structure

```
3110_project/
├── Core Implementation
│   ├── preprocess.py              # Step 1: Preprocessing
│   ├── detect_unchanged.py        # Step 2: Detect unchanged lines
│   ├── generate_candidates.py     # Step 3: Candidate generation
│   ├── resolve_conflicts.py       # Step 4: Resolve conflicts
│   ├── detect_line_splits.py     # Step 5: Detect line splits
│   ├── main.py                    # Main pipeline (CLI entry point)
│   └── similarity_examples.txt   # Step 3 test examples
│
├── Evaluation
│   └── evaluation/evaluate.py     # Evaluation module
│
├── Dataset
│   └── datasets/custom/            # 24 file pairs with ground truth
│       └── <file_pair>/
│           ├── old.java
│           ├── new.java
│           └── mapping.txt         # Ground truth (0-indexed)
│
├── Visualization
│   └── visualization/design.md     # GUI design mockups
│
└── Bonus
    ├── bonus/commit_parser.py      # Bug-fix commit detection
    └── bonus/bic_detector.py       # Bug-introducing change detection
```

## Algorithm Details

### Step 1: Preprocessing
- Lowercase all text
- Normalize identifiers
- Collapse whitespace
- Remove excess indentation
- Standardize brackets, spacing, punctuation

### Step 2: Detect Unchanged Lines
- Uses Longest Common Subsequence (LCS) algorithm
- Identifies unchanged, deleted, and added lines

### Step 3: Generate Candidate List
- **Content Similarity**: Normalized Levenshtein distance
  - Formula: `sim = 1 - (lev_distance / max_length)`
- **Context Similarity**: Cosine similarity of bag-of-words
  - Uses top 4 + bottom 4 lines around target
- **Combined Score**: `0.6 × content + 0.4 × context`
- **SimHash**: 32-bit hash for efficient comparison (k=15 candidates)

### Step 4: Resolve Conflicts
- For each candidate, compute content + context similarity
- Choose highest similarity above threshold (default: 0.6)
- Returns: `{left_idx: right_idx}` mapping

### Step 5: Detect Line Splits
- Incremental concatenation algorithm
- Compute normalized Levenshtein distance
- Continue adding lines while similarity increases
- Stop when similarity decreases
- Returns: `{left_idx: [right_idx1, right_idx2, ...]}` for splits

### Dataset Format

The `datasets/custom/` directory contains 24 file pairs with ground truth mappings:
- Each subdirectory contains:
  - `old.java`: Old version of the file
  - `new.java`: New version of the file
  - `mapping.txt`: Ground truth mapping (0-indexed, format: `left_idx:right_idx`)

## Visualization

See `visualization/design.md` for GUI design mockups showing:
- Side-by-side file comparison
- Color-coded line differences
- Visual connections between mapped lines
- Line split visualization
- Change summary statistics
- Step-by-step pipeline visualization
- Evaluation metrics display

**Note**: Design mockups only (no implementation required per assignment).

## Bonus Feature: Bug-Introducing Change Detection

### Usage

```python
from bonus.commit_parser import is_bugfix_commit
from bonus.bic_detector import detect_bug_introducing_change

# Check if commit is a bug-fix
if is_bugfix_commit("Fix bug in login validation #123"):
    print("Bug-fix commit detected")

# Find bug-introducing commit
bic = detect_bug_introducing_change("/path/to/repo", "commit_hash")
```

### Features
- Identifies bug-fix commits from commit messages using keyword patterns
- Traces back through git history to find the introducing commit
- Output: `bug_fix_commit → bug_introducing_commit`

## Quick Start Examples

### Example 1: Compare Two Files (CLI)
```bash
python main.py datasets/custom/file01/old.java datasets/custom/file01/new.java
```

### Example 2: Evaluate Dataset
```bash
python evaluation/evaluate.py datasets/custom
```

## Requirements Met

✅ **Core Implementation**: All 5 steps implemented  
✅ **Output Format**: `old_line-new_line` mapping  
✅ **Dataset**: 24 file pairs with ground truth  
✅ **Evaluation**: Metrics calculation on datasets  
✅ **Visualization**: GUI design mockups provided  
✅ **Bonus**: Bug-introducing change detection

## License

Part of COMP-3110 course project.
