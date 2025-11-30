import subprocess
import os
from typing import Tuple, List, Optional
from utils.ui import ScrollableWindow, InputDialog, ConfirmDialog, show_message
from menu import Menu


def run_git_command(command: List[str], cwd: str = ".") -> Tuple[bool, str, str]:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except FileNotFoundError:
        return False, "", "Git is not installed or not in PATH"
    except Exception as e:
        return False, "", str(e)


def check_git_repo() -> bool:
    success, _, _ = run_git_command(['git', 'rev-parse', '--git-dir'])
    return success


class GitActions:
    def __init__(self, stdscr):
        self.stdscr = stdscr
    
    def git_status(self):
        if not check_git_repo():
            show_message(self.stdscr, "Not a git repository!", "error")
            return
        
        success, stdout, stderr = run_git_command(['git', 'status'])
        
        if success:
            lines = stdout.split('\n')
            ScrollableWindow(self.stdscr, lines, "Git Status").show()
        else:
            show_message(self.stdscr, f"Error:\n{stderr}", "error")
    
    def git_add(self):
        if not check_git_repo():
            show_message(self.stdscr, "Not a git repository!", "error")
            return
        
        success, stdout, stderr = run_git_command(['git', 'status', '--short'])
        
        if not success:
            show_message(self.stdscr, f"Error:\n{stderr}", "error")
            return
        
        if not stdout.strip():
            show_message(self.stdscr, "No changes to add!", "info")
            return
        
        dialog = InputDialog(self.stdscr, "Enter files to add (or . for all):", ".")
        files = dialog.get_input()
        
        if files is None:
            show_message(self.stdscr, "Add cancelled.", "info")
            return
        
        success, stdout, stderr = run_git_command(['git', 'add'] + files.split())
        
        if success:
            show_message(self.stdscr, f"Successfully added: {files}", "success")
        else:
            show_message(self.stdscr, f"Error:\n{stderr}", "error")
    
    def git_commit(self):
        if not check_git_repo():
            show_message(self.stdscr, "Not a git repository!", "error")
            return
        
        success, stdout, stderr = run_git_command(['git', 'diff', '--cached', '--name-only'])
        
        if not success or not stdout.strip():
            show_message(self.stdscr, "No staged changes to commit!\nUse 'Git Add' first.", "warning")
            return
        
        dialog = InputDialog(self.stdscr, "Enter commit message:")
        message = dialog.get_input()
        
        if not message:
            show_message(self.stdscr, "Commit cancelled (empty message).", "info")
            return
        
        success, stdout, stderr = run_git_command(['git', 'commit', '-m', message])
        
        if success:
            show_message(self.stdscr, f"Commit successful!\n{stdout}", "success")
        else:
            show_message(self.stdscr, f"Error:\n{stderr}", "error")
    
    def git_push(self):
        if not check_git_repo():
            show_message(self.stdscr, "Not a git repository!", "error")
            return
        
        success, stdout, stderr = run_git_command(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
        
        if not success:
            show_message(self.stdscr, f"Error getting branch:\n{stderr}", "error")
            return
        
        branch = stdout.strip()
        
        confirm = ConfirmDialog(self.stdscr, f"Push branch '{branch}' to remote?")
        if not confirm.confirm():
            show_message(self.stdscr, "Push cancelled.", "info")
            return
        
        show_message(self.stdscr, f"Pushing to remote...", "info", wait=False)
        
        success, stdout, stderr = run_git_command(['git', 'push'])
        
        if success:
            show_message(self.stdscr, f"Push successful!\n{stdout}", "success")
        else:
            show_message(self.stdscr, f"Push failed:\n{stderr}", "error")
    
    def git_pull(self):
        if not check_git_repo():
            show_message(self.stdscr, "Not a git repository!", "error")
            return
        
        show_message(self.stdscr, "Pulling from remote...", "info", wait=False)
        
        success, stdout, stderr = run_git_command(['git', 'pull'])
        
        if success:
            show_message(self.stdscr, f"Pull successful!\n{stdout}", "success")
        else:
            show_message(self.stdscr, f"Pull failed:\n{stderr}", "error")
    
    def git_fetch(self):
        if not check_git_repo():
            show_message(self.stdscr, "Not a git repository!", "error")
            return
        
        show_message(self.stdscr, "Fetching from remote...", "info", wait=False)
        
        success, stdout, stderr = run_git_command(['git', 'fetch', '--all'])
        
        if success:
            show_message(self.stdscr, f"Fetch successful!\n{stdout if stdout else 'All refs up to date.'}", "success")
        else:
            show_message(self.stdscr, f"Fetch failed:\n{stderr}", "error")
    
    def git_branch_management(self):
        if not check_git_repo():
            show_message(self.stdscr, "Not a git repository!", "error")
            return
        
        branch_menu = Menu(self.stdscr, "Branch Management", [
            ("List Branches", self.git_list_branches),
            ("Create Branch", self.git_create_branch),
            ("Switch Branch", self.git_switch_branch),
            ("Delete Branch", self.git_delete_branch),
            ("Back", None)
        ])
        branch_menu.run()
    
    def git_list_branches(self):
        success, stdout, stderr = run_git_command(['git', 'branch', '-a'])
        
        if success:
            lines = stdout.split('\n')
            ScrollableWindow(self.stdscr, lines, "All Branches").show()
        else:
            show_message(self.stdscr, f"Error:\n{stderr}", "error")
    
    def git_create_branch(self):
        dialog = InputDialog(self.stdscr, "Enter new branch name:")
        branch_name = dialog.get_input()
        
        if not branch_name:
            show_message(self.stdscr, "Branch creation cancelled.", "info")
            return
        
        success, stdout, stderr = run_git_command(['git', 'branch', branch_name])
        
        if success:
            show_message(self.stdscr, f"Branch '{branch_name}' created successfully!", "success")
        else:
            show_message(self.stdscr, f"Error:\n{stderr}", "error")
    
    def git_switch_branch(self):
        success, stdout, stderr = run_git_command(['git', 'branch'])
        
        if not success:
            show_message(self.stdscr, f"Error:\n{stderr}", "error")
            return
        
        branches = [b.strip().lstrip('* ') for b in stdout.split('\n') if b.strip()]
        
        if not branches:
            show_message(self.stdscr, "No branches available!", "warning")
            return
        
        dialog = InputDialog(self.stdscr, f"Available: {', '.join(branches)}\nEnter branch to switch to:")
        branch_name = dialog.get_input()
        
        if not branch_name:
            show_message(self.stdscr, "Switch cancelled.", "info")
            return
        
        success, stdout, stderr = run_git_command(['git', 'checkout', branch_name])
        
        if success:
            show_message(self.stdscr, f"Switched to branch '{branch_name}'", "success")
        else:
            show_message(self.stdscr, f"Error:\n{stderr}", "error")
    
    def git_delete_branch(self):
        success, stdout, stderr = run_git_command(['git', 'branch'])
        
        if not success:
            show_message(self.stdscr, f"Error:\n{stderr}", "error")
            return
        
        branches = [b.strip().lstrip('* ') for b in stdout.split('\n') if b.strip() and not b.startswith('*')]
        
        if not branches:
            show_message(self.stdscr, "No branches available to delete!", "warning")
            return
        
        dialog = InputDialog(self.stdscr, f"Available: {', '.join(branches)}\nEnter branch to delete:")
        branch_name = dialog.get_input()
        
        if not branch_name:
            show_message(self.stdscr, "Delete cancelled.", "info")
            return
        
        confirm = ConfirmDialog(self.stdscr, f"Delete branch '{branch_name}'?\nThis cannot be undone!")
        if not confirm.confirm():
            show_message(self.stdscr, "Delete cancelled.", "info")
            return
        
        success, stdout, stderr = run_git_command(['git', 'branch', '-d', branch_name])
        
        if success:
            show_message(self.stdscr, f"Branch '{branch_name}' deleted successfully!", "success")
        else:
            show_message(self.stdscr, f"Error:\n{stderr}\n\nUse 'git branch -D' manually for force delete.", "error")
    
    def git_checkout(self):
        if not check_git_repo():
            show_message(self.stdscr, "Not a git repository!", "error")
            return
        
        dialog = InputDialog(self.stdscr, "Enter branch/commit to checkout:")
        target = dialog.get_input()
        
        if not target:
            show_message(self.stdscr, "Checkout cancelled.", "info")
            return
        
        success, stdout, stderr = run_git_command(['git', 'checkout', target])
        
        if success:
            show_message(self.stdscr, f"Checked out: {target}\n{stdout}", "success")
        else:
            show_message(self.stdscr, f"Error:\n{stderr}", "error")
    
    def git_merge(self):
        if not check_git_repo():
            show_message(self.stdscr, "Not a git repository!", "error")
            return
        
        dialog = InputDialog(self.stdscr, "Enter branch to merge into current branch:")
        branch = dialog.get_input()
        
        if not branch:
            show_message(self.stdscr, "Merge cancelled.", "info")
            return
        
        confirm = ConfirmDialog(self.stdscr, f"Merge '{branch}' into current branch?")
        if not confirm.confirm():
            show_message(self.stdscr, "Merge cancelled.", "info")
            return
        
        success, stdout, stderr = run_git_command(['git', 'merge', branch])
        
        if success:
            show_message(self.stdscr, f"Merge successful!\n{stdout}", "success")
        else:
            show_message(self.stdscr, f"Merge failed:\n{stderr}\n\nResolve conflicts manually.", "error")
    
    def git_rebase(self):
        if not check_git_repo():
            show_message(self.stdscr, "Not a git repository!", "error")
            return
        
        dialog = InputDialog(self.stdscr, "Enter branch to rebase onto:")
        branch = dialog.get_input()
        
        if not branch:
            show_message(self.stdscr, "Rebase cancelled.", "info")
            return
        
        confirm = ConfirmDialog(self.stdscr, f"Rebase current branch onto '{branch}'?\nThis rewrites history!")
        if not confirm.confirm():
            show_message(self.stdscr, "Rebase cancelled.", "info")
            return
        
        success, stdout, stderr = run_git_command(['git', 'rebase', branch])
        
        if success:
            show_message(self.stdscr, f"Rebase successful!\n{stdout}", "success")
        else:
            show_message(self.stdscr, f"Rebase failed:\n{stderr}\n\nResolve conflicts or abort with 'git rebase --abort'.", "error")
    
    def git_log(self):
        if not check_git_repo():
            show_message(self.stdscr, "Not a git repository!", "error")
            return
        
        success, stdout, stderr = run_git_command(['git', 'log', '--oneline', '--graph', '--decorate', '--all', '-30'])
        
        if success:
            lines = stdout.split('\n')
            ScrollableWindow(self.stdscr, lines, "Git Log (Last 30 commits)").show()
        else:
            show_message(self.stdscr, f"Error:\n{stderr}", "error")
    
    def git_diff(self):
        if not check_git_repo():
            show_message(self.stdscr, "Not a git repository!", "error")
            return
        
        success, stdout, stderr = run_git_command(['git', 'diff'])
        
        if success:
            if not stdout.strip():
                show_message(self.stdscr, "No differences found in working directory.\n\nTry 'git diff --cached' for staged changes.", "info")
            else:
                lines = stdout.split('\n')
                ScrollableWindow(self.stdscr, lines, "Git Diff").show()
        else:
            show_message(self.stdscr, f"Error:\n{stderr}", "error")
    
    def git_remote(self):
        if not check_git_repo():
            show_message(self.stdscr, "Not a git repository!", "error")
            return
        
        remote_menu = Menu(self.stdscr, "Remote Management", [
            ("List Remotes", self.git_list_remotes),
            ("Add Remote", self.git_add_remote),
            ("Remove Remote", self.git_remove_remote),
            ("Set Remote URL", self.git_set_remote_url),
            ("Show Remote Info", self.git_show_remote),
            ("Back", None)
        ])
        remote_menu.run()
    
    def git_list_remotes(self):
        success, stdout, stderr = run_git_command(['git', 'remote', '-v'])
        
        if success:
            if not stdout.strip():
                show_message(self.stdscr, "No remotes configured.\n\nUse 'Add Remote' to add one.", "info")
            else:
                lines = stdout.split('\n')
                ScrollableWindow(self.stdscr, lines, "Git Remotes").show()
        else:
            show_message(self.stdscr, f"Error:\n{stderr}", "error")
    
    def git_add_remote(self):
        name_dialog = InputDialog(self.stdscr, "Enter remote name (e.g., origin):")
        remote_name = name_dialog.get_input()
        
        if not remote_name:
            show_message(self.stdscr, "Add remote cancelled.", "info")
            return
        
        url_dialog = InputDialog(self.stdscr, f"Enter URL for remote '{remote_name}':")
        remote_url = url_dialog.get_input()
        
        if not remote_url:
            show_message(self.stdscr, "Add remote cancelled.", "info")
            return
        
        success, stdout, stderr = run_git_command(['git', 'remote', 'add', remote_name, remote_url])
        
        if success:
            show_message(self.stdscr, f"Remote '{remote_name}' added successfully!\nURL: {remote_url}", "success")
        else:
            show_message(self.stdscr, f"Error:\n{stderr}", "error")
    
    def git_remove_remote(self):
        success, stdout, stderr = run_git_command(['git', 'remote'])
        
        if not success:
            show_message(self.stdscr, f"Error:\n{stderr}", "error")
            return
        
        remotes = [r.strip() for r in stdout.split('\n') if r.strip()]
        
        if not remotes:
            show_message(self.stdscr, "No remotes configured!", "warning")
            return
        
        dialog = InputDialog(self.stdscr, f"Available: {', '.join(remotes)}\nEnter remote to remove:")
        remote_name = dialog.get_input()
        
        if not remote_name:
            show_message(self.stdscr, "Remove cancelled.", "info")
            return
        
        confirm = ConfirmDialog(self.stdscr, f"Remove remote '{remote_name}'?\nThis cannot be undone!")
        if not confirm.confirm():
            show_message(self.stdscr, "Remove cancelled.", "info")
            return
        
        success, stdout, stderr = run_git_command(['git', 'remote', 'remove', remote_name])
        
        if success:
            show_message(self.stdscr, f"Remote '{remote_name}' removed successfully!", "success")
        else:
            show_message(self.stdscr, f"Error:\n{stderr}", "error")
    
    def git_set_remote_url(self):
        success, stdout, stderr = run_git_command(['git', 'remote'])
        
        if not success:
            show_message(self.stdscr, f"Error:\n{stderr}", "error")
            return
        
        remotes = [r.strip() for r in stdout.split('\n') if r.strip()]
        
        if not remotes:
            show_message(self.stdscr, "No remotes configured!", "warning")
            return
        
        name_dialog = InputDialog(self.stdscr, f"Available: {', '.join(remotes)}\nEnter remote name:")
        remote_name = name_dialog.get_input()
        
        if not remote_name:
            show_message(self.stdscr, "Set URL cancelled.", "info")
            return
        
        url_dialog = InputDialog(self.stdscr, f"Enter new URL for '{remote_name}':")
        new_url = url_dialog.get_input()
        
        if not new_url:
            show_message(self.stdscr, "Set URL cancelled.", "info")
            return
        
        confirm = ConfirmDialog(self.stdscr, f"Change URL for remote '{remote_name}'?")
        if not confirm.confirm():
            show_message(self.stdscr, "Set URL cancelled.", "info")
            return
        
        success, stdout, stderr = run_git_command(['git', 'remote', 'set-url', remote_name, new_url])
        
        if success:
            show_message(self.stdscr, f"Remote '{remote_name}' URL updated!\nNew URL: {new_url}", "success")
        else:
            show_message(self.stdscr, f"Error:\n{stderr}", "error")
    
    def git_show_remote(self):
        success, stdout, stderr = run_git_command(['git', 'remote'])
        
        if not success:
            show_message(self.stdscr, f"Error:\n{stderr}", "error")
            return
        
        remotes = [r.strip() for r in stdout.split('\n') if r.strip()]
        
        if not remotes:
            show_message(self.stdscr, "No remotes configured!", "warning")
            return
        
        dialog = InputDialog(self.stdscr, f"Available: {', '.join(remotes)}\nEnter remote to show:")
        remote_name = dialog.get_input()
        
        if not remote_name:
            show_message(self.stdscr, "Show cancelled.", "info")
            return
        
        success, stdout, stderr = run_git_command(['git', 'remote', 'show', remote_name])
        
        if success:
            lines = stdout.split('\n')
            ScrollableWindow(self.stdscr, lines, f"Remote Info: {remote_name}").show()
        else:
            show_message(self.stdscr, f"Error:\n{stderr}", "error")
    
    def clone_repository(self):
        dialog = InputDialog(self.stdscr, "Enter repository URL to clone:")
        repo_url = dialog.get_input()
        
        if not repo_url:
            show_message(self.stdscr, "Clone cancelled.", "info")
            return
        
        target_dialog = InputDialog(self.stdscr, "Enter target directory (optional):", "")
        target_dir = target_dialog.get_input()
        
        show_message(self.stdscr, "Cloning repository...\nThis may take a while.", "info", wait=False)
        
        cmd = ['git', 'clone', repo_url]
        if target_dir:
            cmd.append(target_dir)
        
        success, stdout, stderr = run_git_command(cmd)
        
        if success:
            show_message(self.stdscr, f"Clone successful!\n{stdout}", "success")
        else:
            show_message(self.stdscr, f"Clone failed:\n{stderr}", "error")
    
    def init_repository(self):
        if check_git_repo():
            show_message(self.stdscr, "Already a git repository!", "warning")
            return
        
        confirm = ConfirmDialog(self.stdscr, "Initialize a new git repository in current directory?")
        if not confirm.confirm():
            show_message(self.stdscr, "Init cancelled.", "info")
            return
        
        success, stdout, stderr = run_git_command(['git', 'init'])
        
        if success:
            show_message(self.stdscr, f"Git repository initialized!\n{stdout}", "success")
        else:
            show_message(self.stdscr, f"Error:\n{stderr}", "error")
