from abc import ABC, abstractmethod
from typing import Type
from textual.widget import Widget

class OrganPlugin(ABC):
    """The interface that all organ plugins must implement."""

    @property
    @abstractmethod
    def name(self) -> str:
        """A unique, lowercase name for the plugin (e.g., 'digestive')."""
        pass

    @abstractmethod
    def __init__(self, engine):
        self.engine = engine

    @abstractmethod
    def update(self, tick_duration: float) -> None:
        """Called by the engine on every tick to update the plugin's state."""
        pass

    @abstractmethod
    def get_sensations(self) -> list[str]:
        """Return a list of strings describing current sensations."""
        pass

    @abstractmethod
    def get_state(self) -> dict[str, str]:
        """Return a dictionary of states for TUI display."""
        pass

    def get_widget_class(self) -> Type[Widget] | None:
        """Optionally return a custom Textual Widget class for this plugin."""
        return None
