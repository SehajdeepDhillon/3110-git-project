# LHDiff Visualization Design

## Overview

This document describes the GUI design for visualizing line mapping information between file versions. The visualization helps users understand how lines from an old file version map to lines in a new file version.

## Design Principles

1. **Side-by-Side Comparison**: Display old and new files side-by-side for easy comparison
2. **Color-Coded Differences**: Use colors to indicate unchanged, changed, added, and deleted lines
3. **Visual Connections**: Draw lines connecting mapped lines across versions
4. **Interactive Navigation**: Allow users to scroll, search, and jump to specific mappings

## GUI Layout

### Main Window Structure

```
┌─────────────────────────────────────────────────────────────────┐
│  LHDiff - Line Mapping Visualization                            │
├──────────────────┬──────────────────────────────────────────────┤
│                  │                                              │
│   OLD FILE       │            NEW FILE                         │
│   (Left Panel)   │            (Right Panel)                    │
│                  │                                              │
│  Line 1  ────────┼───────────>  Line 1                         │
│  Line 2  ────────┼───────────>  Line 2                         │
│  Line 3  ────────┼───────────>  Line 4  (changed)             │
│  Line 4  ────────┼───────────>  Line 5                         │
│  Line 5  ────────┼───────────>  Line 6                         │
│  Line 6  ────────┼───────────>  Line 7                         │
│  Line 7  ────────┼───────────>  Line 8                         │
│  Line 8  ────────┼───────────>  Line 9                         │
│  Line 9  ────────┼───────────>  {Line 10, Line 11} (split)    │
│                  │                                              │
│  [DELETED]       │            Line 3  (added)                   │
│                  │                                              │
└──────────────────┴──────────────────────────────────────────────┘
│  Status Bar: 9 mappings | 1 deleted | 1 added | 1 split        │
└─────────────────────────────────────────────────────────────────┘
```

## Color Coding Scheme

### Line Status Colors

- **Green**: Unchanged lines (exact match)
- **Yellow**: Changed lines (modified but mapped)
- **Blue**: Added lines (new in right file)
- **Red**: Deleted lines (removed from left file)
- **Purple**: Split lines (one left line maps to multiple right lines)
- **Gray**: Unmapped lines

### Connection Lines

- **Solid Green Line**: Unchanged mapping
- **Dashed Yellow Line**: Changed mapping
- **Curved Purple Line**: Split mapping (one-to-many)

## Screen Views

### 1. Line Mapping View

**Purpose**: Primary view showing all line mappings

**Features**:
- Side-by-side file display
- Scrollable panels synchronized vertically
- Line numbers on both sides
- Connection lines between mapped lines
- Highlight on hover
- Click to select and show details

**Layout**:
```
┌──────────────┬──────────────┐
│ OLD FILE     │ NEW FILE     │
│              │              │
│ 1: int a;    │ 1: int a;    │
│ 2: int b;    │ 2: int b;    │
│ 3: int c;    │ 3: int x;    │
│              │              │
└──────────────┴──────────────┘
```

### 2. Split-Line Visualization

**Purpose**: Detailed view of line splits (one-to-many mappings)

**Features**:
- Highlight split lines prominently
- Show concatenated text
- Display similarity scores
- Allow expansion/collapse of split details

**Example**:
```
OLD Line 9: "return a + b + c;"
    ↓ (split into)
NEW Line 10: "return a +"
NEW Line 11: "    b +"
NEW Line 12: "    c;"
Similarity: 0.95
```

### 3. Change Summary View

**Purpose**: Overview statistics and summary

**Features**:
- Total lines in old file
- Total lines in new file
- Number of unchanged lines
- Number of changed lines
- Number of added lines
- Number of deleted lines
- Number of split lines
- Overall mapping accuracy (if ground truth available)

**Layout**:
```
┌─────────────────────────────┐
│ Change Summary              │
├─────────────────────────────┤
│ Total Old Lines:    100     │
│ Total New Lines:    105     │
│                             │
│ Unchanged:          85      │
│ Changed:            10      │
│ Added:               5      │
│ Deleted:             5      │
│ Split:               2      │
│                             │
│ Mapping Coverage:    90%    │
└─────────────────────────────┘
```

## Interactive Features

### Navigation
- **Scroll Synchronization**: Both panels scroll together
- **Jump to Line**: Enter line number to jump
- **Search**: Find text in either file
- **Zoom**: Adjust font size

### Selection
- **Click Line**: Select and highlight mapping
- **Hover**: Show connection line
- **Multi-select**: Select multiple mappings

### Filtering
- **Show Only Changed**: Hide unchanged lines
- **Show Only Splits**: Highlight split mappings
- **Show Unmapped**: Highlight lines without mappings

## Implementation Notes

### Technology Stack (Design Only)
- **Desktop Application**: Electron or PyQt
- **Web Application**: React/Vue.js with D3.js for connections
- **Visualization Library**: D3.js for line drawing

### Data Format
- Input: JSON mapping from LHDiff output
- Format: `{left_idx: right_idx}` or `{left_idx: [right_idx1, right_idx2, ...]}`

### Performance Considerations
- Virtual scrolling for large files
- Lazy rendering of connection lines
- Debounced search and filtering

## Mockups

See `visualization/mockups/` directory for:
- `main_view.png` - Main line mapping interface
- `split_view.png` - Split line detail view
- `summary_view.png` - Change summary dashboard

## Future Enhancements

1. **Diff Highlighting**: Show character-level differences within changed lines
2. **Timeline View**: Show evolution across multiple versions
3. **Export Options**: Export mappings to various formats
4. **Comparison Modes**: Side-by-side, unified, or inline diff views
5. **Annotation**: Allow users to add notes to mappings

