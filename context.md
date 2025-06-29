# Semantic File Clustering System - Design Document

## Problem Statement
Traditional file organization requires constant decision-making about "where does this content belong?" This breaks the writing flow and creates organizational overhead. Users want to write freely without thinking about file structure.

## Relationship to Obsidian
This system shares Obsidian's core philosophy of interconnected knowledge management but with key differences:
- **Similar to Obsidian**: Graph visualization of connected notes, focus on linking ideas, knowledge exploration
- **Different from Obsidian**: Manual linking vs automatic semantic clustering, file creation friction vs zero-friction writing
- **Enhancement**: Obsidian's graph shows manual connections; this shows semantic similarity automatically

## Solution Overview
A system where users write content in files that automatically cluster in 2D space based on semantic similarity. Each file finds its natural position among related content without manual organization. Think "Obsidian graph view but semantic and automatic."

## Core User Flow
1. User presses Ctrl+N to create new file
2. User writes stream-of-consciousness content
3. System automatically embeds file content into vector space
4. File appears in 2D graph view positioned near semantically similar files
5. User can navigate 2D space to discover related content (like Obsidian graph but semantic)

## Key Requirements

### Functional Requirements
- **File Creation**: One-key file creation (Ctrl+N) with immediate writing capability
- **Semantic Embedding**: Convert each file's full content into vector representation
- **2D Positioning**: Map high-dimensional vectors to 2D coordinates using dimensionality reduction
- **Real-time Updates**: Files reposition automatically when content changes
- **Visual Clustering**: Similar files appear closer together in 2D space (like Obsidian graph layout)
- **Interactive Navigation**: Pan, zoom, click to select files (similar to Obsidian graph navigation)
- **Connection Visualization**: Show similarity connections between selected file and related files

### Technical Requirements
- **Processing Unit**: Entire file content (not individual paragraphs)
- **Embedding Model**: Local sentence transformer (no API dependencies)
- **Dimensionality Reduction**: UMAP for stable 2D projection
- **Performance**: <200ms update time for file changes
- **Storage**: Local file system + vector database
- **Platform**: Desktop application (Electron) or web app

## System Architecture

### Components
1. **File Watcher**: Monitors file system changes
2. **Embedding Service**: Generates vectors from text content using local transformer
3. **Vector Store**: Stores and indexes file embeddings
4. **Clustering Engine**: Calculates file similarities and positions
5. **2D Graph Renderer**: D3.js or Canvas-based visualization (similar to Obsidian graph)
6. **UI Layer**: Minimal writing interface + 2D graph navigation

### Data Flow
```
File Change → Text Extraction → Embedding Generation → Vector Storage → 
Similarity Calculation → 2D Positioning → Graph Visualization Update
```

## Key Design Decisions

### Embedding Strategy
- **Model**: all-MiniLM-L6-v2 (384 dimensions, local inference)
- **Scope**: Full file content as single embedding
- **Update**: Regenerate embedding on file save

### 2D Positioning
- **Algorithm**: UMAP reduction to 2D coordinates
- **Stability**: Seeded reduction for consistent positioning
- **Layout**: Bounded canvas space with force-directed layout refinement
- **Future**: 3D visualization planned for later implementation

### Visualization
- **File Representation**: Nodes/circles sized by content length (like Obsidian nodes)
- **Clustering**: Visual proximity indicates semantic similarity
- **Connections**: Lines between highly similar files (similarity > 0.7)
- **Selection**: Highlight selected file and show all connections
- **Navigation**: Pan and zoom like Obsidian graph view

## User Interface Specifications

### Writing Interface
- Clean, distraction-free text editor
- Auto-save every 2 seconds
- Minimal chrome, focus on content creation
- No file naming required (auto-generated)

### 2D Graph Navigation
- Pan controls (drag to move around)
- Zoom controls (scroll wheel)
- File selection (click to select)
- Hover tooltips with file preview
- Similar interaction patterns to Obsidian graph view

### Information Display
- Selected file details panel
- File count and status indicators
- Similarity connection visualization
- Search functionality (semantic, not keyword)

## Implementation Priorities

### Phase 1 (MVP)
- Basic file creation and editing
- Simple embedding generation
- 2D graph visualization with manual positioning
- File selection and preview

### Phase 2 (Core Features)
- Automatic semantic positioning
- Real-time clustering updates
- Connection line visualization
- Smooth navigation controls (Obsidian-like)

### Phase 3 (Enhanced Experience)
- Semantic search
- Temporal filtering
- Export capabilities
- Performance optimizations
- **Future**: 3D visualization upgrade

## Success Metrics
- **Writing Flow**: Zero-friction file creation (Ctrl+N to writing in <1 second)
- **Clustering Accuracy**: Semantically similar files cluster visually together
- **Performance**: Smooth navigation with 1000+ files (like Obsidian graph performance)
- **Discovery**: Users find unexpected connections between their content

## Technical Constraints
- **Local-first**: No cloud dependencies
- **Real-time**: Updates visible within 200ms
- **Scalable**: Handle 10,000+ files efficiently
- **Cross-platform**: Windows, macOS, Linux support

## Expected User Behavior Change
**Before**: "Where should I save this? What should I name it? Which folder?"
**After**: Ctrl+N → start writing → system handles organization automatically

## Core Value Proposition
Transform the anxiety of "I need to organize this properly" into the excitement of "I wonder where this will cluster and what connections I'll discover."