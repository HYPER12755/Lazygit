"""Configuration schema and validation."""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class ColorPair:
    fg: int = 7
    bg: int = -1
    bold: bool = False
    underline: bool = False


@dataclass
class ThemeConfig:
    name: str = "default"
    colors: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "header": {"fg": 0, "bg": 6, "bold": True},
        "footer": {"fg": 7, "bg": 0},
        "selected": {"fg": 0, "bg": 3, "bold": True},
        "normal": {"fg": 2, "bg": -1},
        "success": {"fg": 2, "bg": -1},
        "error": {"fg": 1, "bg": -1},
        "warning": {"fg": 3, "bg": -1},
        "info": {"fg": 6, "bg": -1},
        "staged": {"fg": 2, "bg": -1},
        "unstaged": {"fg": 1, "bg": -1},
        "untracked": {"fg": 5, "bg": -1},
        "branch": {"fg": 6, "bg": -1, "bold": True},
        "commit_hash": {"fg": 3, "bg": -1},
        "commit_msg": {"fg": 7, "bg": -1},
        "diff_add": {"fg": 2, "bg": -1},
        "diff_del": {"fg": 1, "bg": -1},
        "diff_header": {"fg": 6, "bg": -1, "bold": True},
        "panel_border": {"fg": 4, "bg": -1},
        "panel_title": {"fg": 7, "bg": 4, "bold": True},
        "panel_focused": {"fg": 6, "bg": -1, "bold": True},
    })


@dataclass
class KeyBinding:
    action: str
    key: str
    description: str = ""


@dataclass
class KeybindingsConfig:
    global_keys: Dict[str, str] = field(default_factory=lambda: {
        "quit": "q",
        "help": "?",
        "refresh": "r",
        "focus_next": "tab",
        "focus_prev": "shift+tab",
        "panel_1": "1",
        "panel_2": "2",
        "panel_3": "3",
        "panel_4": "4",
    })
    navigation: Dict[str, str] = field(default_factory=lambda: {
        "up": "k",
        "down": "j",
        "left": "h",
        "right": "l",
        "page_up": "ctrl+u",
        "page_down": "ctrl+d",
        "top": "g",
        "bottom": "G",
        "select": "enter",
        "back": "escape",
    })
    files: Dict[str, str] = field(default_factory=lambda: {
        "stage": "space",
        "stage_all": "a",
        "unstage_all": "u",
        "discard": "d",
        "edit": "e",
        "open": "o",
    })
    commits: Dict[str, str] = field(default_factory=lambda: {
        "commit": "c",
        "amend": "A",
        "reword": "r",
        "fixup": "f",
        "squash": "s",
    })
    branches: Dict[str, str] = field(default_factory=lambda: {
        "checkout": "enter",
        "new_branch": "n",
        "delete": "d",
        "rename": "r",
        "merge": "m",
        "rebase": "R",
    })
    stash: Dict[str, str] = field(default_factory=lambda: {
        "stash": "s",
        "pop": "p",
        "apply": "a",
        "drop": "d",
    })


@dataclass
class CustomCommand:
    name: str
    command: str
    description: str = ""
    key: Optional[str] = None
    confirm: bool = False
    show_output: bool = True
    category: str = "custom"


@dataclass
class CommandsConfig:
    custom: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "name": "Push Force",
            "command": "git push --force-with-lease",
            "key": "P",
            "confirm": True,
            "description": "Force push with lease"
        },
        {
            "name": "Pull Rebase",
            "command": "git pull --rebase",
            "key": "p",
            "description": "Pull with rebase"
        },
        {
            "name": "Log Graph",
            "command": "git log --oneline --graph --all -20",
            "key": "L",
            "description": "Show log graph"
        },
    ])


@dataclass
class LayoutConfig:
    panels: List[str] = field(default_factory=lambda: [
        "status", "files", "commits", "command"
    ])
    default_focus: str = "files"
    split_ratio: List[float] = field(default_factory=lambda: [0.3, 0.7])
    show_borders: bool = True
    show_panel_titles: bool = True


@dataclass
class GeneralConfig:
    git_path: str = "git"
    refresh_interval: float = 2.0
    mouse_enabled: bool = False
    confirm_destructive: bool = True
    auto_refresh: bool = True
    max_log_entries: int = 100
    diff_context_lines: int = 3


@dataclass 
class Config:
    general: GeneralConfig = field(default_factory=GeneralConfig)
    theme: ThemeConfig = field(default_factory=ThemeConfig)
    keybindings: KeybindingsConfig = field(default_factory=KeybindingsConfig)
    commands: CommandsConfig = field(default_factory=CommandsConfig)
    layout: LayoutConfig = field(default_factory=LayoutConfig)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        config = cls()
        
        if "general" in data:
            for key, value in data["general"].items():
                if hasattr(config.general, key):
                    setattr(config.general, key, value)
        
        if "theme" in data:
            if "name" in data["theme"]:
                config.theme.name = data["theme"]["name"]
            if "colors" in data["theme"]:
                config.theme.colors.update(data["theme"]["colors"])
        
        if "keybindings" in data:
            for section, bindings in data["keybindings"].items():
                if hasattr(config.keybindings, section):
                    getattr(config.keybindings, section).update(bindings)
        
        if "commands" in data:
            if "custom" in data["commands"]:
                config.commands.custom = data["commands"]["custom"]
        
        if "layout" in data:
            for key, value in data["layout"].items():
                if hasattr(config.layout, key):
                    setattr(config.layout, key, value)
        
        return config
