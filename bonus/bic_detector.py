"""
Bonus Feature: Bug-Introducing Change Detector
Traces back from bug-fix commits to find the commit that introduced the bug.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, List
from commit_parser import is_bugfix_commit


def get_commit_files(repo_path: str, commit_id: str) -> Dict[str, str]:
    """
    Get list of files changed in a commit.
    
    Args:
        repo_path: Path to git repository
        commit_id: Commit hash
    
    Returns:
        Dictionary mapping file paths to their content at that commit
    """
    files = {}
    
    try:
        # Get list of changed files
        result = subprocess.run(
            ['git', 'show', '--name-only', '--pretty=format:', commit_id],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return files
        
        changed_files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
        
        # Get content of each file at this commit
        for file_path in changed_files:
            try:
                file_result = subprocess.run(
                    ['git', 'show', f'{commit_id}:{file_path}'],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if file_result.returncode == 0:
                    files[file_path] = file_result.stdout
            except Exception:
                continue
                
    except Exception as e:
        print(f"Error getting commit files: {e}")
    
    return files


def get_parent_commit(repo_path: str, commit_id: str) -> Optional[str]:
    """
    Get parent commit of given commit.
    
    Args:
        repo_path: Path to git repository
        commit_id: Commit hash
    
    Returns:
        Parent commit hash or None
    """
    try:
        result = subprocess.run(
            ['git', 'rev-parse', f'{commit_id}^'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    
    return None


def get_commit_message(repo_path: str, commit_id: str) -> str:
    """
    Get commit message for a commit.
    
    Args:
        repo_path: Path to git repository
        commit_id: Commit hash
    
    Returns:
        Commit message
    """
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--pretty=format:%s', commit_id],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    
    return ""


def detect_bug_introducing_change(repo_path: str, commit_id: str, max_depth: int = 10) -> Optional[str]:
    """
    Detect the commit that introduced a bug by tracing back from a bug-fix commit.
    
    Algorithm:
    1. Start from bug-fix commit
    2. For each file changed in bug-fix:
       a. Get file content at bug-fix commit
       b. Get file content at parent commit
       c. Use LHDiff to find which lines were fixed
       d. Trace back to find when those lines were last changed
    3. Return the commit that introduced the bug
    
    Args:
        repo_path: Path to git repository
        commit_id: Bug-fix commit hash
        max_depth: Maximum number of commits to trace back
    
    Returns:
        Commit hash of bug-introducing change, or None if not found
    """
    # Verify this is a bug-fix commit
    message = get_commit_message(repo_path, commit_id)
    if not is_bugfix_commit(message):
        return None
    
    # Get files changed in bug-fix commit
    bug_fix_files = get_commit_files(repo_path, commit_id)
    
    if not bug_fix_files:
        return None
    
    # For each changed file, find the bug-introducing commit
    bug_introducing_commits = []
    
    for file_path, bug_fix_content in bug_fix_files.items():
        # Get parent commit
        parent_commit = get_parent_commit(repo_path, commit_id)
        if not parent_commit:
            continue
        
        # Get file content at parent (before fix)
        parent_files = get_commit_files(repo_path, parent_commit)
        if file_path not in parent_files:
            continue
        
        parent_content = parent_files[file_path]
        
        # Use LHDiff to find changed lines
        # For simplicity, we'll trace back commits that modified this file
        # In a full implementation, we'd use LHDiff to identify specific lines
        
        # Trace back through commit history
        current_commit = parent_commit
        depth = 0
        
        while current_commit and depth < max_depth:
            # Check if this commit modified the file
            try:
                result = subprocess.run(
                    ['git', 'log', '--oneline', '-1', '--', file_path],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                # Get commits that modified this file before the bug-fix
                log_result = subprocess.run(
                    ['git', 'log', f'{current_commit}..{commit_id}', '--oneline', '--', file_path],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if log_result.returncode == 0 and log_result.stdout.strip():
                    # Found commits that modified this file
                    # For simplicity, return the most recent one before the bug-fix
                    lines = log_result.stdout.strip().split('\n')
                    if lines:
                        # Extract commit hash from first line
                        commit_hash = lines[0].split()[0]
                        bug_introducing_commits.append(commit_hash)
                        break
                
                # Move to parent
                current_commit = get_parent_commit(repo_path, current_commit)
                depth += 1
                
            except Exception:
                break
    
    # Return the most likely bug-introducing commit
    if bug_introducing_commits:
        # Return the most recent one (first in list)
        return bug_introducing_commits[0]
    
    return None


def find_bug_introducing_changes(repo_path: str, limit: int = 10) -> List[Dict]:
    """
    Find all bug-fix commits and their corresponding bug-introducing commits.
    
    Args:
        repo_path: Path to git repository
        limit: Maximum number of bug-fix commits to analyze
    
    Returns:
        List of dictionaries: [{'bug_fix': commit_id, 'bug_introducing': commit_id}, ...]
    """
    results = []
    
    try:
        # Get recent commits
        result = subprocess.run(
            ['git', 'log', f'--max-count={limit}', '--pretty=format:%H|%s'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return results
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if '|' in line:
                commit_id, message = line.split('|', 1)
                if is_bugfix_commit(message):
                    commits.append((commit_id, message))
        
        # For each bug-fix commit, find bug-introducing commit
        for commit_id, message in commits:
            bic = detect_bug_introducing_change(repo_path, commit_id)
            if bic:
                results.append({
                    'bug_fix': commit_id,
                    'bug_fix_message': message,
                    'bug_introducing': bic
                })
    
    except Exception as e:
        print(f"Error finding bug-introducing changes: {e}")
    
    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python bic_detector.py <repo_path> [commit_id]")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    
    if len(sys.argv) >= 3:
        # Analyze specific commit
        commit_id = sys.argv[2]
        bic = detect_bug_introducing_change(repo_path, commit_id)
        if bic:
            print(f"Bug-fix commit: {commit_id}")
            print(f"Bug-introducing commit: {bic}")
        else:
            print(f"Could not find bug-introducing commit for {commit_id}")
    else:
        # Find all bug-introducing changes
        results = find_bug_introducing_changes(repo_path, limit=20)
        print(f"Found {len(results)} bug-fix → bug-introducing pairs:")
        for r in results:
            print(f"  {r['bug_fix'][:8]} → {r['bug_introducing'][:8]}")

