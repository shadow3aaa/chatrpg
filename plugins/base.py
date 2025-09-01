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

    @property
    def display_name(self) -> str:
        """A human-readable name for the plugin (e.g., 'Digestive System'). Defaults to a capitalized version of the internal name."""
        return self.name.capitalize()

    @abstractmethod
    def __init__(self, engine):
        self.engine = engine

    def register_properties(self):
        """Inspects the plugin for OrganProperty descriptors and registers them with the engine."""
        for attr_name in dir(self.__class__):
            attr_value = getattr(self.__class__, attr_name)
            if isinstance(attr_value, OrganProperty):
                self.engine.register_property(attr_name, self)

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

class OrganProperty:
    """A descriptor for a property of an organ that automatically handles min/max clamping."""
    def __init__(self, default, min_val=None, max_val=None, description=""):
        self.default = default
        self.min_val = min_val
        self.max_val = max_val
        self.description = description
        self._private_name = None

    def __set_name__(self, owner, name):
        self._private_name = f"_{name}"
        # Set the default value on the instance
        if not hasattr(owner, self._private_name):
             setattr(owner, self._private_name, self.default)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        # Get the value from the instance's __dict__
        return getattr(instance, self._private_name, self.default)

    def __set__(self, instance, value):
        if self.min_val is not None:
            value = max(self.min_val, value)
        if self.max_val is not None:
            value = min(self.max_val, value)
        setattr(instance, self._private_name, value)
