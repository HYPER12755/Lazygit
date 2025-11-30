import curses
import json
import os
from typing import List, Tuple, Optional


class Theme:
    def __init__(self, config_path: str = "config.json"):
        self.pairs = {}
        self.load_config(config_path)
    
    def load_config(self, config_path: str):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                self.colors = config.get('theme', {}).get('colors', {})
        except (FileNotFoundError, json.JSONDecodeError):
            self.colors = self._default_colors()
    
    def _default_colors(self):
        return {
            "header_fg": 0, "header_bg": 6,
            "footer_fg": 7, "footer_bg": 0,
            "selected_fg": 0, "selected_bg": 3,
            "normal_fg": 2, "normal_bg": -1,
            "success_fg": 2, "success_bg": -1,
            "error_fg": 1, "error_bg": -1,
            "warning_fg": 3, "warning_bg": -1,
            "info_fg": 6, "info_bg": -1
        }
    
    def setup(self):
        curses.start_color()
        curses.use_default_colors()
        
        if not curses.has_colors():
            return
        
        curses.init_pair(1, self.colors['header_fg'], self.colors['header_bg'])
        curses.init_pair(2, self.colors['footer_fg'], self.colors['footer_bg'])
        curses.init_pair(3, self.colors['selected_fg'], self.colors['selected_bg'])
        curses.init_pair(4, self.colors['normal_fg'], self.colors['normal_bg'])
        curses.init_pair(5, self.colors['success_fg'], self.colors['success_bg'])
        curses.init_pair(6, self.colors['error_fg'], self.colors['error_bg'])
        curses.init_pair(7, self.colors['warning_fg'], self.colors['warning_bg'])
        curses.init_pair(8, self.colors['info_fg'], self.colors['info_bg'])
        
        self.pairs = {
            'header': curses.color_pair(1) | curses.A_BOLD,
            'footer': curses.color_pair(2),
            'selected': curses.color_pair(3) | curses.A_BOLD,
            'normal': curses.color_pair(4),
            'success': curses.color_pair(5),
            'error': curses.color_pair(6),
            'warning': curses.color_pair(7),
            'info': curses.color_pair(8)
        }
    
    def get(self, style: str):
        return self.pairs.get(style, curses.A_NORMAL)


class ScrollableWindow:
    def __init__(self, stdscr, lines: List[str], title: str = "Output"):
        self.stdscr = stdscr
        self.lines = lines
        self.title = title
        self.scroll_pos = 0
        self.theme = Theme()
        self.theme.setup()
    
    def show(self):
        curses.curs_set(0)
        max_y, max_x = self.stdscr.getmaxyx()
        visible_lines = max_y - 4
        
        while True:
            self.stdscr.clear()
            
            self.stdscr.addstr(0, 0, f" {self.title} ".ljust(max_x), self.theme.get('header'))
            
            for i in range(visible_lines):
                line_num = self.scroll_pos + i
                if line_num < len(self.lines):
                    line = self.lines[line_num][:max_x - 2]
                    try:
                        self.stdscr.addstr(i + 2, 0, line, self.theme.get('normal'))
                    except curses.error:
                        pass
            
            status = f"Lines {self.scroll_pos + 1}-{min(self.scroll_pos + visible_lines, len(self.lines))} / {len(self.lines)}"
            self.stdscr.addstr(max_y - 2, 0, status, self.theme.get('info'))
            
            footer = "↑↓: Scroll | PgUp/PgDn: Page | Home/End: Jump | q/Esc: Back"
            self.stdscr.addstr(max_y - 1, 0, footer[:max_x - 1], self.theme.get('footer'))
            
            self.stdscr.refresh()
            
            key = self.stdscr.getch()
            
            if key == ord('q') or key == 27:
                break
            elif key == curses.KEY_DOWN:
                if self.scroll_pos < len(self.lines) - visible_lines:
                    self.scroll_pos += 1
            elif key == curses.KEY_UP:
                if self.scroll_pos > 0:
                    self.scroll_pos -= 1
            elif key == curses.KEY_NPAGE:
                self.scroll_pos = min(self.scroll_pos + 10, max(0, len(self.lines) - visible_lines))
            elif key == curses.KEY_PPAGE:
                self.scroll_pos = max(self.scroll_pos - 10, 0)
            elif key == curses.KEY_HOME:
                self.scroll_pos = 0
            elif key == curses.KEY_END:
                self.scroll_pos = max(0, len(self.lines) - visible_lines)


class InputDialog:
    def __init__(self, stdscr, prompt: str, default: str = ""):
        self.stdscr = stdscr
        self.prompt = prompt
        self.default = default
        self.theme = Theme()
        self.theme.setup()
    
    def get_input(self) -> Optional[str]:
        max_y, max_x = self.stdscr.getmaxyx()
        
        curses.echo()
        curses.curs_set(1)
        
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, " Input Required ".ljust(max_x), self.theme.get('header'))
        
        prompt_y = max_y // 2 - 2
        self.stdscr.addstr(prompt_y, 2, self.prompt, self.theme.get('normal'))
        
        input_y = prompt_y + 2
        self.stdscr.addstr(input_y, 2, "> ", self.theme.get('selected'))
        
        footer = "Enter: Submit | Esc: Cancel"
        self.stdscr.addstr(max_y - 1, 0, footer[:max_x - 1], self.theme.get('footer'))
        
        self.stdscr.refresh()
        
        input_win = curses.newwin(1, max_x - 6, input_y, 4)
        input_win.keypad(True)
        
        if self.default:
            input_win.addstr(0, 0, self.default)
        
        try:
            curses.curs_set(1)
            user_input = input_win.getstr(0, 0, max_x - 8).decode('utf-8')
            curses.noecho()
            curses.curs_set(0)
            return user_input if user_input else self.default
        except KeyboardInterrupt:
            curses.noecho()
            curses.curs_set(0)
            return None
        except Exception:
            curses.noecho()
            curses.curs_set(0)
            return None


class ConfirmDialog:
    def __init__(self, stdscr, message: str):
        self.stdscr = stdscr
        self.message = message
        self.theme = Theme()
        self.theme.setup()
    
    def confirm(self) -> bool:
        max_y, max_x = self.stdscr.getmaxyx()
        
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, " Confirmation ".ljust(max_x), self.theme.get('warning'))
        
        msg_y = max_y // 2 - 1
        self.stdscr.addstr(msg_y, 2, self.message, self.theme.get('normal'))
        
        choice_y = msg_y + 2
        self.stdscr.addstr(choice_y, 2, "[Y]es / [N]o", self.theme.get('selected'))
        
        footer = "y: Confirm | n: Cancel"
        self.stdscr.addstr(max_y - 1, 0, footer[:max_x - 1], self.theme.get('footer'))
        
        self.stdscr.refresh()
        
        while True:
            key = self.stdscr.getch()
            if key in [ord('y'), ord('Y')]:
                return True
            elif key in [ord('n'), ord('N'), 27]:
                return False


def show_message(stdscr, message: str, msg_type: str = "info", wait: bool = True):
    theme = Theme()
    theme.setup()
    
    max_y, max_x = stdscr.getmaxyx()
    
    stdscr.clear()
    
    header_text = f" {msg_type.upper()} "
    if msg_type == "error":
        stdscr.addstr(0, 0, header_text.ljust(max_x), theme.get('error'))
    elif msg_type == "success":
        stdscr.addstr(0, 0, header_text.ljust(max_x), theme.get('success'))
    elif msg_type == "warning":
        stdscr.addstr(0, 0, header_text.ljust(max_x), theme.get('warning'))
    else:
        stdscr.addstr(0, 0, header_text.ljust(max_x), theme.get('info'))
    
    msg_y = max_y // 2
    lines = message.split('\n')
    for idx, line in enumerate(lines):
        try:
            stdscr.addstr(msg_y + idx, 2, line[:max_x - 4], theme.get('normal'))
        except curses.error:
            pass
    
    if wait:
        footer = "Press any key to continue..."
        stdscr.addstr(max_y - 1, 0, footer[:max_x - 1], theme.get('footer'))
        stdscr.refresh()
        stdscr.getch()
    else:
        stdscr.refresh()
