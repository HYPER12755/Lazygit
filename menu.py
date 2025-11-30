import curses
from typing import List, Tuple, Callable, Optional
from utils.ui import Theme


class Menu:
    def __init__(self, stdscr, title: str, items: List[Tuple[str, Optional[Callable]]]):
        self.stdscr = stdscr
        self.title = title
        self.items = items
        self.selected = 0
        self.theme = Theme()
        self.theme.setup()
        
        self.stdscr.keypad(True)
        curses.cbreak()
        curses.noecho()
        curses.curs_set(0)
    
    def draw(self):
        self.stdscr.clear()
        max_y, max_x = self.stdscr.getmaxyx()
        
        header_text = f" {self.title} "
        self.stdscr.addstr(0, 0, header_text.ljust(max_x), self.theme.get('header'))
        
        start_y = 2
        for idx, (item_name, _) in enumerate(self.items):
            y = start_y + idx
            
            if idx == self.selected:
                prefix = "→ "
                attr = self.theme.get('selected')
            else:
                prefix = "  "
                attr = self.theme.get('normal')
            
            try:
                display_text = f"{prefix}{item_name}"
                self.stdscr.addstr(y, 2, display_text.ljust(max_x - 4)[:max_x - 4], attr)
            except curses.error:
                pass
        
        footer_text = "↑↓: Navigate | Enter: Select | q: Quit"
        try:
            self.stdscr.addstr(max_y - 1, 0, footer_text[:max_x - 1], self.theme.get('footer'))
        except curses.error:
            pass
        
        self.stdscr.refresh()
    
    def run(self):
        while True:
            self.draw()
            
            key = self.stdscr.getch()
            
            if key == curses.KEY_UP:
                if self.selected > 0:
                    self.selected -= 1
            
            elif key == curses.KEY_DOWN:
                if self.selected < len(self.items) - 1:
                    self.selected += 1
            
            elif key == 10 or key == curses.KEY_ENTER:
                item_name, action = self.items[self.selected]
                
                if action is None:
                    return
                
                if item_name == "Exit":
                    return
                
                try:
                    action()
                except Exception as e:
                    from utils.ui import show_message
                    show_message(self.stdscr, f"Error executing action:\n{str(e)}", "error")
            
            elif key == ord('q') or key == ord('Q'):
                return
            
            elif key == 27:
                return
