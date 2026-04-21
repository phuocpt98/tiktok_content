---
title: graphify-novel Repository Analysis Report
date: 2026-04-13
type: research
status: complete
---

# graphify-novel: Comprehensive Repository Analysis

## Executive Summary

**graphify-novel** is a specialized AI writing assistant that uses knowledge graphs to automate manuscript management. Created April 11, 2026, by Anshler (27 stars, 9 forks, MIT license). The project is a CLI-based skill designed for AI coding assistants (Claude, Copilot, etc.) that tracks characters, plot threads, and world-building consistency across full novels using dual complementary systems: a structured "story bible" (canonical state) and an auto-generated knowledge graph (relationship discovery).

---

## Project Core Purpose

**What It Does:**
- Eliminates manuscript tracking overhead by automating character state management, plot thread continuity, and world-building consistency tracking
- Generates "story bibles" (structured YAML/Markdown documentation) from premises or existing chapters
- Detects contradictions, continuity gaps, and unresolved plot setups within draft chapters
- Maps implicit relationships between narrative elements (characters, locations, events, themes) across the full manuscript
- Enables cross-chapter queries to trace connections not visible in individual files

**Key Innovation:**
Separates canonical reference data (bible) from relationship discovery (graph). Bible answers factual questions ("Where is character X?"), while graph surfaces structural patterns ("How does character X connect to location Y?")

---

## Technology Stack & Dependencies

### Core Architecture
- **Language-Agnostic Skill**: Deployed as CLI tool via `npx skills add Anshler/graphify-novel`
- **Primary Dependency**: `graphify` (pip-installable: `graphifyy`)
- **Interface**: Command-line skill for AI coding assistants (Claude, GitHub Copilot, etc.)

### Tech Choices
- **YAML + Markdown**: Story bible uses YAML frontmatter + Markdown for human-readable, version-controllable documentation
- **JSON-based Graph**: Knowledge graph stored as `graph.json` with optional HTML visualization
- **Sub-agent Architecture**: Uses sub-agents for batch processing to overcome context window limits in init phase
- **File System I/O**: Direct read/write operations on project directory structure

### External Integration Points
- **graphify library**: Handles graph extraction, visualization, and query processing (BFS/DFS traversal)
- **GitHub Actions**: PR-review workflow using Claude Sonnet 4.6 for automated code review (pr-review.yml)
- **AI Coding Assistants**: Designed as a skill layer for Claude Code, GitHub Copilot

---

## Repository Structure

```
graphify-novel/
├── .github/
│   └── workflows/
│       └── pr-review.yml          # GitHub Actions: Claude-powered PR review bot
├── .gitignore                      # Standard Git ignore patterns
├── LICENSE                         # MIT License
├── README.md                       # English documentation (6.3 KB)
├── README.vi.md                    # Vietnamese documentation (7.6 KB)
└── SKILL.md                        # Technical specification (27.2 KB) ← primary technical doc
```

**Total Size**: 73 KB
**Files**: 6 items in root
**Language**: Python-based (requires graphify dependency)

### Project Directory Structure (User-Facing)

When initialized, graphify-novel creates this structure:

```
<project>/
├── chapters/                       # Canonical manuscript (.txt or .md)
├── draft/                          # WIP files (excluded from graph)
├── static/                         # Images & assets (excluded from graph)
├── bible/
│   ├── premise.md                  # Title, genre, POV, themes, core conflict
│   ├── timeline.md                 # Events with chapter refs, threads, characters
│   ├── characters/
│   │   ├── <slug>.md               # YAML state + arc log per character
│   │   └── _index.md               # Roster table
│   ├── threads/
│   │   ├── <slug>.md               # Setup/payoff, event IDs, status
│   │   └── _index.md               # Thread index
│   └── world/
│       ├── <topic>.md              # Location/faction/rule/artifact detail
│       └── _index.md               # Topic index
├── graphify-out/                   # Auto-generated (do not edit)
│   ├── graph.json                  # Knowledge graph representation
│   ├── graph.html                  # Visualization
│   ├── node-aliases.json           # Entity deduplication map
│   └── GRAPH_REPORT.md             # Graph analysis report
└── .graphifyignore                 # Exclude patterns
```

---

## Command Structure & API

### Primary Commands

| Command | Purpose | Modes |
|---------|---------|-------|
| `init` | Scaffold bible from premise | `--from <file>`, `--from-chapters [--batch N]` |
| `review` | Check passage against bible for contradictions/gaps | file, `--passage`, `--intent` |
| `update` | Commit changes to bible after review | file, `--manual`, `--lore` |
| `status` | Snapshot of open threads, character states, unresolved setups | None |
| `query` | Relationship search across graph | `--dfs` for DFS, `path` for shortest connection |
| `thread` | Manage plot threads | `new`, `resolve`, `list` |

### Installation
```bash
npx skills add Anshler/graphify-novel
```

**Prerequisite**: graphify library must be installed
```bash
pip install graphifyy && graphify install
```

---

## Key Data Schemas

### Timeline Entry Format
```
[E001] ch.00 — <event> | threads: [slug] | characters: [Name]
[E002] ch.01 · chapter1.txt — <event> | threads: [] | characters: [Name]
```
- Event IDs reflect insertion order
- Pre-story events use `ch.00`; unknown chapters use `ch.?`
- Chapter refs anchor events to specific manuscript nodes

### Character Schema (YAML + Markdown)
```yaml
---
name: Full Name
slug: unique-lowercase-hyphenated-id
status: alive | dead | missing | unknown
location: Current Location
goal: Driving Goal
relationships:
  other-slug: <nature, first appeared ch.X>
---
## Arc Log
- ch.01: <state change>
```

### Thread Schema
```yaml
---
title: Thread Title
slug: thread-slug
status: open | resolved | abandoned
type: main | subplot | character_arc | mystery | promise
introduced: ch.XX
resolved: null
events: [E001, E042]
---
## Summary / Setup / Current State / Payoff
```

---

## Workflow: Core Operations

### 1. Initialization (`init`)
- Creates folder structure
- Populates bible from premise or chapters
- For `--from-chapters`: spawns sub-agents in batches of N to overcome context limits
- Each sub-agent reads current bible state before processing its chapters
- Flags ambiguities with `[?]` tags rather than blocking
- Rebuilds knowledge graph after completion

### 2. Review (`review`)
- Loads passage without modifying files
- Extracts entities/events
- Cross-references against bible and graph
- Flags: **contradictions** (must fix), **gaps** (should address), **opportunities** (thread hooks)
- Requires graphify for entity extraction

### 3. Update (`update`)
- Mandates prior review pass in current context
- Commits changes to timeline, character arc logs, thread event lists
- Creates new world/thread entries as needed
- Rebuilds knowledge graph

### 4. Query (`query` / `path`)
- Uses rebuilt graph for relationship traversal
- Applies deduplication via `graphify-out/node-aliases.json`
- Entity priority: dedicated files > index stubs > cross-references > chapter nodes
- BFS (default) or DFS traversal modes

---

## Critical Implementation Details

### Prerequisite Verification
Before any command, verifies graphify is installed. If missing, requests user permission for `pip install graphifyy && graphify install`.

### Batch Processing Strategy (`init --from-chapters`)
- Sub-agents process chapters independently without accumulation across batches
- Each reads current bible state from disk before processing
- Prevents context overflow for large manuscripts
- Ambiguities flagged inline rather than requiring synchronization

### Entity Merging & Deduplication
Before presenting graph results, applies `node-aliases.json` to deduplicate nodes:
1. Dedicated entity files (highest priority)
2. Index stubs
3. Cross-references
4. Chapter nodes (lowest priority)
5. Concept nodes checked for label overlap

### Review Validation
Update mode mandates prior review to ensure contradictions were resolved. If missing, asks writer whether to run review before proceeding.

### Graph Rebuild Triggers
Required after: `init`, `update`, and thread operations
- Triggers `/graphify --update`
- Rebuilds alias map from graph.json using source_file priority

---

## CI/CD & Automation

### GitHub Actions: pr-review.yml
**Purpose**: Automated code review on pull requests using Claude Sonnet

**Trigger**: Comment with `@claude-review` on PR

**Job Steps**:
1. PR metadata retrieval (base/head branches, title, description)
2. Repository checkout to feature branch
3. Unified diff generation (100KB max for token limits)
4. Claude Sonnet 4.6 analysis (correctness, bugs, security, code quality)
5. Comment publication with formatted review

**Configuration**:
- Model: `claude-sonnet-4-6`
- Max response: 2048 tokens
- Permissions: write to PR, read repository
- Error handling for API failures

---

## Development Activity

### Repository Metrics (as of April 13, 2026)
- **Created**: April 11, 2026
- **Last Updated**: April 13, 2026 (2 days old)
- **Stars**: 28
- **Forks**: 9
- **Size**: 73 KB
- **Status**: Active, not archived

### Development Patterns
- **Author**: Anshler (huynhminhtriet2002@gmail.com)
- **Commit Frequency**: Intensive (dozens over 2-day period)
- **Focus Areas**: Documentation (README updates), skill features, workflow optimization
- **Languages Supported**: English + Vietnamese documentation
- **Code Review**: Pull request process in place (#1, #2 merged)

### Documentation Quality
- Comprehensive SKILL.md (27.2 KB) with technical specs
- Dual-language README support (English + Vietnamese)
- Focus on clarity over brevity

---

## Key Features & Patterns

### 1. Dual-System Design
- **Story Bible**: Canonical source of truth; explicitly updated
- **Knowledge Graph**: Emergent relationship discovery; auto-generated
- Systems complement rather than replace each other

### 2. Smart Entity Tracking
- Characters: status (alive/dead/missing), location, goals, relationships
- Threads: setup/payoff, event linkage, resolution status
- Timeline: events [E###] with chapter refs, character/thread mentions

### 3. Consistency Checking
- Detects contradictions (flagged for mandatory fix)
- Identifies continuity gaps (flagged for consideration)
- Surface implicit connections through graph traversal

### 4. Context-Aware Batch Processing
- Sub-agent architecture for scaling to large manuscripts
- No accumulation errors across batches
- Inline ambiguity marking instead of blocking

### 5. Relationship Discovery
- Cross-chapter pattern detection
- Chekhov's gun identification
- Theme connections across manuscript
- Shortest-path queries between story elements

---

## Integration Model

### For AI Coding Assistants
- Deployed as CLI skill via skills marketplace
- Installed once per project: `npx skills add Anshler/graphify-novel`
- Commands invoked as chat directives: `/graphify-novel init "premise"`

### For Writers/Developers
- Skill provides prompts and workflows
- Guides through init → review → update → query pipeline
- Maintains markdown/YAML docs in version control
- Graph outputs in .gitignore (auto-generated, not committed)

### Dependencies
- `graphify` (Python library for graph extraction/visualization)
- File system access
- AI assistant with markdown/YAML parsing

---

## Architecture Patterns

### Separation of Concerns
1. **Writing Layer**: chapters/, draft/ (user content)
2. **Reference Layer**: bible/ (structured metadata)
3. **Analysis Layer**: graphify-out/ (computed relationships)

### Data Flow
```
Premise/Chapters
      ↓
   [init]
      ↓
Story Bible (YAML/Markdown)
      ↓
  [review] → Contradictions/Gaps/Opportunities
      ↓
   [update]
      ↓
Knowledge Graph (graph.json)
      ↓
  [query] → Relationship Answers
```

### State Management
- Bible is authoritative until explicitly changed
- Graph is disposable (rebuilt after init/update)
- .gitignore excludes graphify-out/ (regenerable)
- Committed files: chapters/, bible/, .graphifyignore

---

## Notable Design Decisions

### Why Not Direct-to-Graph?
Dual-system approach avoids losing canonical data. Graph shows relationships but doesn't store ground truth (e.g., "Where is character X?" answered by bible, not graph).

### Why Batch Processing?
LLM context windows (even large models) insufficient for full manuscript processing. Sub-agents in batches + disk-based state persistence prevents context overflow.

### Why YAML Frontmatter?
Separates structured metadata (parseable by code) from natural-language narrative (readable by writers). Git-diff friendly.

### Why Entity Deduplication Map?
Same character might be referenced differently across chapters ("Elara", "the Queen", "she"). Node-aliases.json prioritizes source, preventing graph bloat.

---

## Development Context & Purpose

### Target Users
- Fiction writers using AI coding assistants (Claude, Copilot)
- Authors wanting manuscript consistency automation
- Novel developers building story documentation

### Positioning
Part of the broader AI writing toolkit ecosystem; complements graphify (graph library) by providing novel-specific workflows and story-bible scaffolding.

### Recent Focus
- Documentation polish (Vietnamese translation)
- Workflow automation (pr-review.yml)
- Skill feature expansion ("update skill" commits)

---

## Repository Assets

### Documentation
- **README.md**: Features, installation, quick-start (6.3 KB, English)
- **README.vi.md**: Vietnamese translation with usage examples (7.6 KB)
- **SKILL.md**: Comprehensive technical specification (27.2 KB)
  - Architecture, schemas, workflows, implementation details
  - Prerequisite checks, batch processing, entity merging
  - Integration points, conflict resolution

### Automation
- **pr-review.yml**: GitHub Actions workflow for Claude-powered code reviews

### Configuration
- **.gitignore**: Standard patterns
- **LICENSE**: MIT

---

## Unresolved Questions

1. **Python vs. Other Languages**: Is the skill exclusively Python, or is it language-agnostic and the graphify dependency happens to be Python?

2. **Graphify Integration Depth**: How tightly coupled is graphify-novel to graphify? Can it work with other graph libraries or is graphify required?

3. **Sub-agent Implementation**: How are sub-agents spawned for batch processing? Is this baked into the skill or delegated to the host AI assistant?

4. **Version Stability**: No releases yet (0 tags); when is v1.0 planned? Is the API stable for production use?

5. **LLM Model Flexibility**: Is Claude-Sonnet hardcoded in workflows, or can users swap models?

6. **Manuscript Scale**: What's the tested maximum manuscript size (chapters/word count) before performance degrades?

7. **Graph Library Version**: Which graphify version is recommended? Any known compatibility issues?

8. **Offline Capability**: Does the skill require API access (beyond the AI assistant) or is it fully local?

---

## Summary Assessment

**graphify-novel** is a focused, well-designed tool addressing a specific pain point: manuscript consistency tracking. The dual-system architecture (bible + graph) is clever and avoids the common trap of trying to make a single system do both canonical storage and relationship discovery.

Key strengths:
- Clear separation of concerns
- Pragmatic batch processing for large manuscripts
- Integration with existing AI coding assistant workflows
- Comprehensive documentation (SKILL.md is exemplary)

Key observation:
- Very new (2 days old); no releases yet
- Heavy reliance on graphify (prerequisite dependency)
- GitHub Actions automation shows production-readiness intention

The project targets a niche but underserved use case and executes cleanly.
