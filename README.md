# Git TUI - Fast Terminal Interface for Git

A fast, colorful terminal-based user interface for Git operations using Python's curses module.

## Features

- **Arrow-key navigation** (↑↓) with instant response
- **Colorful theme** with customizable colors
- **Comprehensive Git operations**:
  - Status, Add, Commit, Push, Pull, Fetch
  - Branch Management (create, switch, delete, list)
  - Checkout, Merge, Rebase
  - Log (with graph), Diff, Remote management
  - Clone and Init repositories
- **Safe operations** with confirmation dialogs for destructive commands
- **Scrollable output** for long command results
- **Modular architecture** for easy extension

## Requirements

- Python 3.6+
- Git installed on your system
- Unix-like terminal with curses support

## Installation

No dependencies required beyond Python's standard library!

## Usage

Run the TUI with:

```bash
python3 main.py
```

## Navigation

- **↑↓**: Navigate menu items
- **Enter**: Select/Execute option
- **q**: Quit/Go back
- **Esc**: Cancel/Go back

## Configuration

Edit `config.json` to customize the color theme:

```json
{
  "theme": {
    "colors": {
      "header_fg": 0,
      "header_bg": 6,
      "selected_fg": 0,
      "selected_bg": 3,
      ...
    }
  }
}
```

Color values:
- 0: Black
- 1: Red
- 2: Green
- 3: Yellow
- 4: Blue
- 5: Magenta
- 6: Cyan
- 7: White
- -1: Terminal default

## Project Structure

```
.
├── main.py           # Entry point
├── menu.py           # Menu navigation system
├── config.json       # Theme configuration
├── actions/
│   ├── __init__.py
│   └── git.py        # Git operations
└── utils/
    ├── __init__.py
    └── ui.py         # UI utilities (dialogs, scrolling, themes)
```

## Extending

To add a new Git command:

1. Add a method to `GitActions` class in `actions/git.py`
2. Add a menu item in `main.py`
3. The TUI framework handles the rest!

## Error Handling

The TUI is designed to never crash:
- All Git commands have timeout protection
- User confirmations for destructive operations
- Graceful error messages with scroll support
- Safe terminal cleanup on exit

## License

MIT License - Feel free to use and modify!
