"""
GitTUI - A fast, colorful terminal UI for Git operations.

Like lazygit but fully customizable with YAML configuration.
"""

__version__ = "1.0.0"
__author__ = "GitTUI Team"

from gittui.core.application import Application

__all__ = ["Application", "__version__"]
