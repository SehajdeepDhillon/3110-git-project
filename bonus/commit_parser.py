"""
Bonus Feature: Commit Parser
Identifies bug-fix commits by analyzing commit messages.
"""

import re
from typing import List, Tuple, Optional


# Keywords that indicate a bug fix
BUG_FIX_KEYWORDS = [
    'fix', 'bug', 'error', 'issue', 'defect', 'fault',
    'crash', 'exception', 'fail', 'broken', 'wrong',
    'correct', 'repair', 'resolve', 'patch'
]


def is_bugfix_commit(message: str) -> bool:
    """
    Determine if a commit message indicates a bug fix.
    
    Args:
        message: Commit message string
    
    Returns:
        True if message contains bug-fix indicators, False otherwise
    """
    if not message:
        return False
    
    message_lower = message.lower()
    
    # Check for bug-fix keywords
    for keyword in BUG_FIX_KEYWORDS:
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, message_lower):
            return True
    
    # Check for common bug-fix patterns
    bug_patterns = [
        r'fix\s+#?\d+',  # "fix #123" or "fix 123"
        r'bug\s+#?\d+',  # "bug #456"
        r'issue\s+#?\d+',  # "issue #789"
        r'resolves?\s+#?\d+',  # "resolves #123"
    ]
    
    for pattern in bug_patterns:
        if re.search(pattern, message_lower):
            return True
    
    return False


def extract_bug_id(message: str) -> Optional[str]:
    """
    Extract bug/issue ID from commit message if present.
    
    Args:
        message: Commit message
    
    Returns:
        Bug ID string or None
    """
    patterns = [
        r'#(\d+)',  # #123
        r'issue\s+#?(\d+)',  # issue #123 or issue 123
        r'bug\s+#?(\d+)',  # bug #123
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message.lower())
        if match:
            return match.group(1)
    
    return None


def parse_commit_message(message: str) -> dict:
    """
    Parse commit message and extract information.
    
    Returns:
        Dictionary with parsed information
    """
    return {
        'is_bugfix': is_bugfix_commit(message),
        'bug_id': extract_bug_id(message),
        'message': message
    }


if __name__ == "__main__":
    # Test cases
    test_messages = [
        "Fix bug in login validation",
        "Add new feature",
        "Fix issue #123 with null pointer",
        "Refactor code structure",
        "Resolve bug #456 in authentication",
        "Update documentation",
        "Fix crash when loading file",
        "Improve performance",
    ]
    
    print("Testing commit parser:")
    for msg in test_messages:
        result = parse_commit_message(msg)
        print(f"  '{msg}' -> Bug fix: {result['is_bugfix']}")

