import os
import difflib
import xml.etree.ElementTree as ET
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set


#Import Normalizer

class DiffAnalyzer:
    """Analyze differences between two files using difflib."""
    
    def __init__(self, file1_path: str, file2_path: str, normalizer=None):
        self.file1_path = file1_path
        self.file2_path = file2_path
        self.lines1 = []
        self.lines2 = []
        self.normalizer = normalizer
        self._read_files()
    
    def _read_files(self):
        """Read both files into line arrays."""
        with open(self.file1_path, 'r', encoding='utf-8', errors='ignore') as f:
            self.lines1 = f.readlines()
        
        with open(self.file2_path, 'r', encoding='utf-8', errors='ignore') as f:
            self.lines2 = f.readlines()
        
        # Apply normalization once implented / configure later
        if self.normalizer:
            self.lines1 = self.normalizer.normalize_lines(self.lines1)
            self.lines2 = self.normalizer.normalize_lines(self.lines2)
    
    def find_unchanged_lines(self) -> Dict[int, int]:
        """
        Find unchanged lines between two files.
        Returns dict mapping original line numbers to new line numbers.
        Line numbers are 1-indexed to match XML format.
        """
        matcher = difflib.SequenceMatcher(None, self.lines1, self.lines2)
        unchanged_mapping = {}
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal': #match exactly
                for offset in range(i2 - i1):
                    orig_line = i1 + offset + 1  # Convert to 1-indexed
                    new_line = j1 + offset + 1   
                    unchanged_mapping[orig_line] = new_line
        
        return unchanged_mapping
    
    def find_all_mappings(self) -> Dict[int, int]:
        """
        Find all line mappings including deletions.
        Returns dict where deleted lines map to -1.
        """
        matcher = difflib.SequenceMatcher(None, self.lines1, self.lines2)
        all_mappings = {}
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # Unchanged lines
                for offset in range(i2 - i1):
                    orig_line = i1 + offset + 1
                    new_line = j1 + offset + 1
                    all_mappings[orig_line] = new_line
            elif tag == 'delete':
                # Deleted lines
                for line_num in range(i1 + 1, i2 + 1):
                    all_mappings[line_num] = -1
            elif tag == 'replace':
                # Modified/replaced lines - treat as deletions for now
                for line_num in range(i1 + 1, i2 + 1):
                    all_mappings[line_num] = -1
        
        return all_mappings