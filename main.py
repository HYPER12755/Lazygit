#!/usr/bin/env python3
import curses
import sys
from menu import Menu
from actions.git import GitActions


def main(stdscr):
    try:
        git = GitActions(stdscr)
        
        main_menu_items = [
            ("Git Status", git.git_status),
            ("Git Add", git.git_add),
            ("Git Commit", git.git_commit),
            ("Git Push", git.git_push),
            ("Git Pull", git.git_pull),
            ("Git Fetch", git.git_fetch),
            ("Git Branch Management", git.git_branch_management),
            ("Git Checkout", git.git_checkout),
            ("Git Merge", git.git_merge),
            ("Git Rebase", git.git_rebase),
            ("Git Log", git.git_log),
            ("Git Diff", git.git_diff),
            ("Git Remote", git.git_remote),
            ("Clone Repository", git.clone_repository),
            ("Init Repository", git.init_repository),
            ("Exit", None)
        ]
        
        main_menu = Menu(stdscr, "Git TUI - Fast Git Operations", main_menu_items)
        main_menu.run()
    
    except KeyboardInterrupt:
        pass
    except Exception as e:
        stdscr.clear()
        stdscr.addstr(0, 0, f"Fatal Error: {str(e)}")
        stdscr.addstr(1, 0, "Press any key to exit...")
        stdscr.refresh()
        stdscr.getch()


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
