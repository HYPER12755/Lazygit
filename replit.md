# Overview

Git TUI is a fast, terminal-based user interface for Git operations built with Python's curses module. It provides an interactive menu system for executing common Git commands with arrow-key navigation, colorful theming, and scrollable output windows. The application is designed to be lightweight with zero external dependencies beyond Python's standard library.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Terminal UI Framework

**Problem**: Provide a responsive, keyboard-driven interface for Git operations in the terminal.

**Solution**: Built using Python's curses library with a modular menu system that supports navigation, selection, and scrolling.

**Architecture**:
- **Menu System**: Core navigation component (`menu.py`) that handles item selection and keyboard input
- **Theme Engine**: Configurable color schemes loaded from JSON (`utils/ui.py`)
- **UI Components**: Reusable widgets including ScrollableWindow, InputDialog, and ConfirmDialog for user interaction

**Design Rationale**: Curses provides native terminal capabilities without external dependencies, ensuring the application runs on any Unix-like system with Python.

## Git Command Execution

**Problem**: Execute Git commands safely and capture output for display.

**Solution**: Subprocess-based command execution with timeout protection and error handling (`actions/git.py`).

**Architecture**:
- Commands run in isolated subprocesses with 30-second timeout
- Output captured as text streams (stdout/stderr)
- Repository validation before executing Git operations
- Return tuple structure: (success_boolean, stdout_string, stderr_string)

**Alternatives Considered**: Using GitPython library was considered but rejected to maintain zero-dependency design.

**Pros**: Complete control over command execution, no external dependencies, works with any Git version
**Cons**: Must manually construct Git commands, no built-in Git object model

## Configuration System

**Problem**: Allow users to customize UI appearance without code changes.

**Solution**: JSON-based configuration file (`config.json`) for theme and UI settings.

**Architecture**:
- Theme colors defined with foreground/background pairs
- UI behavior settings (scroll speed, animations)
- Fallback to default values if config is missing or invalid

**Design Rationale**: JSON provides human-readable configuration that's easy to edit and parse with Python's standard library.

## Error Handling Strategy

**Problem**: Gracefully handle Git errors, missing repositories, and user interruptions.

**Solution**: Multi-layer error handling with user-friendly messages.

**Architecture**:
- Command-level: Subprocess error catching and timeout handling
- Repository-level: Pre-execution validation with `check_git_repo()`
- UI-level: Message dialogs for errors, warnings, and success states
- Application-level: Keyboard interrupt handling and fatal error display

**Design Rationale**: Defensive programming ensures the application doesn't crash from common user errors or edge cases.

## Modular Action System

**Problem**: Organize Git operations in an extensible, maintainable structure.

**Solution**: Action-based architecture with `GitActions` class containing all Git operations (`actions/git.py`).

**Architecture**:
- Each Git operation is a method on the `GitActions` class
- Actions receive stdscr reference for UI interaction
- Main menu maps menu items to action methods
- Actions package structure allows easy addition of new operation categories

**Pros**: Clear separation of concerns, easy to add new Git commands, testable methods
**Cons**: Potential code duplication for similar operations (mitigated by helper functions)

# External Dependencies

## Git

**Purpose**: Version control system that the TUI interfaces with

**Integration**: Command-line execution via subprocess module

**Requirements**: Git must be installed and available in system PATH

**Validation**: Application checks for Git installation and valid repository status before operations

## Python Standard Library

The application uses only Python's standard library:

- **curses**: Terminal UI rendering and input handling
- **subprocess**: Git command execution
- **json**: Configuration file parsing
- **os**: File system operations
- **sys**: System-level error handling

**Note**: No third-party packages required - application is completely self-contained.

## Terminal Environment

**Requirements**:
- Unix-like terminal with curses support
- Color terminal capability (optional, degrades gracefully)
- Minimum Python 3.6+

**Constraints**: Not compatible with Windows Command Prompt (requires WSL or Unix-like terminal)