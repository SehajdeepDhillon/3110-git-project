"""
Evaluation module for LHDiff.
Calculates metrics: %Correct, %Change, %Spurious, %Eliminate
Supports Reiss benchmark, Eclipse benchmark, NetBeans benchmark.
"""

import csv
import os
from pathlib import Path
from typing import Dict, List, Tuple
import sys

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import lhdiff


def calculate_metrics(ground_truth: Dict[int, int], predicted: Dict[int, int]) -> Dict[str, float]:
    """
    Calculate evaluation metrics: %Correct, %Change, %Spurious, %Eliminate
    
    Args:
        ground_truth: Dictionary {left_idx: right_idx} from ground truth
        predicted: Dictionary {left_idx: right_idx} from LHDiff prediction
    
    Returns:
        Dictionary with metrics: {'correct': float, 'change': float, 'spurious': float, 'eliminate': float}
    """
    # Convert to sets for easier comparison
    # Handle both single values and lists in predicted
    predicted_pairs = set()
    for left_idx, right_val in predicted.items():
        if isinstance(right_val, list):
            # For line splits, consider all pairs
            for right_idx in right_val:
                predicted_pairs.add((left_idx, right_idx))
        else:
            predicted_pairs.add((left_idx, right_val))
    
    truth_pairs = set(ground_truth.items())
    
    # Calculate metrics
    correct = len(predicted_pairs & truth_pairs)
    total_truth = len(truth_pairs)
    total_predicted = len(predicted_pairs)
    
    # %Correct: percentage of ground truth pairs correctly predicted
    pct_correct = (correct / total_truth * 100) if total_truth > 0 else 0.0
    
    # %Change: percentage of predicted pairs that differ from truth
    changed = total_predicted - correct
    pct_change = (changed / total_predicted * 100) if total_predicted > 0 else 0.0
    
    # %Spurious: percentage of predicted pairs not in truth
    spurious = len(predicted_pairs - truth_pairs)
    pct_spurious = (spurious / total_predicted * 100) if total_predicted > 0 else 0.0
    
    # %Eliminate: percentage of truth pairs not predicted
    eliminated = len(truth_pairs - predicted_pairs)
    pct_eliminate = (eliminated / total_truth * 100) if total_truth > 0 else 0.0
    
    return {
        'correct': pct_correct,
        'change': pct_change,
        'spurious': pct_spurious,
        'eliminate': pct_eliminate
    }


def load_ground_truth(mapping_file: str) -> Dict[int, int]:
    """
    Load ground truth mapping from file.
    Expected format: one mapping per line, "left_idx:right_idx" or "left_idx:right_idx1,right_idx2,..."
    """
    mapping = {}
    if not os.path.exists(mapping_file):
        return mapping
    
    with open(mapping_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if ':' in line:
                left_str, right_str = line.split(':', 1)
                try:
                    left_idx = int(left_str.strip())
                    # Handle both single values and lists
                    if ',' in right_str:
                        # Multiple right indices (line split)
                        right_indices = [int(x.strip()) for x in right_str.split(',')]
                        # For ground truth, use first index (or could use all)
                        mapping[left_idx] = right_indices[0]
                    else:
                        mapping[left_idx] = int(right_str.strip())
                except ValueError:
                    continue
    return mapping


def run_evaluation(dataset_path: str) -> List[Dict]:
    """
    Run LHDiff evaluation on a dataset.
    
    Args:
        dataset_path: Path to dataset directory containing file pairs
    
    Returns:
        List of result dictionaries, each containing file info and metrics
    """
    results = []
    dataset_dir = Path(dataset_path)
    
    # Find all file pairs (looking for old.java/new.java or old_file/new_file patterns)
    file_pairs = []
    
    # Look for directories with old/new file pairs
    for item in dataset_dir.iterdir():
        if item.is_dir():
            # Check for old/new files in subdirectory
            old_files = list(item.glob("old*"))
            new_files = list(item.glob("new*"))
            if old_files and new_files:
                file_pairs.append((old_files[0], new_files[0], item / "mapping.txt"))
        elif item.is_file() and "old" in item.name.lower():
            # Look for corresponding new file
            new_name = item.name.replace("old", "new").replace("Old", "New")
            new_file = item.parent / new_name
            mapping_file = item.parent / "mapping.txt"
            if new_file.exists():
                file_pairs.append((item, new_file, mapping_file))
    
    print(f"Found {len(file_pairs)} file pairs in {dataset_path}")
    
    for old_file, new_file, mapping_file in file_pairs:
        print(f"\nEvaluating: {old_file.name} → {new_file.name}")
        
        try:
            # Run LHDiff
            predicted = lhdiff(str(old_file), str(new_file))
            
            # Load ground truth
            ground_truth = load_ground_truth(str(mapping_file))
            
            # Calculate metrics
            metrics = calculate_metrics(ground_truth, predicted)
            
            result = {
                'file': old_file.name,
                'correct': metrics['correct'],
                'change': metrics['change'],
                'spurious': metrics['spurious'],
                'eliminate': metrics['eliminate']
            }
            results.append(result)
            
            print(f"  %Correct: {metrics['correct']:.2f}%")
            print(f"  %Change: {metrics['change']:.2f}%")
            print(f"  %Spurious: {metrics['spurious']:.2f}%")
            print(f"  %Eliminate: {metrics['eliminate']:.2f}%")
            
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({
                'file': old_file.name,
                'error': str(e)
            })
    
    return results


def export_results_to_csv(results: List[Dict], output_path: str = "results.csv") -> None:
    """
    Export evaluation results to CSV file.
    
    Args:
        results: List of result dictionaries
        output_path: Path to output CSV file
    """
    if not results:
        print("No results to export")
        return
    
    fieldnames = ['file', 'correct', 'change', 'spurious', 'eliminate']
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            if 'error' not in result:
                writer.writerow(result)
    
    print(f"\nResults exported to {output_path}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python evaluate.py <dataset_path> [output_csv]")
        sys.exit(1)
    
    dataset_path = sys.argv[1]
    output_csv = sys.argv[2] if len(sys.argv) > 2 else "results.csv"
    
    results = run_evaluation(dataset_path)
    export_results_to_csv(results, output_csv)
    
    # Print summary
    if results:
        valid_results = [r for r in results if 'error' not in r]
        if valid_results:
            avg_correct = sum(r['correct'] for r in valid_results) / len(valid_results)
            avg_change = sum(r['change'] for r in valid_results) / len(valid_results)
            avg_spurious = sum(r['spurious'] for r in valid_results) / len(valid_results)
            avg_eliminate = sum(r['eliminate'] for r in valid_results) / len(valid_results)
            
            print(f"\n=== SUMMARY ===")
            print(f"Files evaluated: {len(valid_results)}")
            print(f"Average %Correct: {avg_correct:.2f}%")
            print(f"Average %Change: {avg_change:.2f}%")
            print(f"Average %Spurious: {avg_spurious:.2f}%")
            print(f"Average %Eliminate: {avg_eliminate:.2f}%")

