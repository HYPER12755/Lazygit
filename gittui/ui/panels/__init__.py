"""Panel components for the UI."""

from gittui.ui.panels.base import Panel
from gittui.ui.panels.status import StatusPanel
from gittui.ui.panels.files import FilesPanel
from gittui.ui.panels.commits import CommitsPanel
from gittui.ui.panels.command import CommandPanel

__all__ = ["Panel", "StatusPanel", "FilesPanel", "CommitsPanel", "CommandPanel"]
