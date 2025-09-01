# ChatRPG Plugin Development Guide

This document will guide you on how to create new organ or physiological system plugins for this project.

## Basic Concept

The core of this project is a pluggable physiological engine. Each independent physiological function (e.g., digestion, circulation) is a separate "plugin." The engine automatically discovers and loads all plugins from the `plugins/` directory upon startup.

To create a new plugin, you simply need to create a new Python file and implement a class that inherits from the `OrganPlugin` base class.

## The Plugin Interface (`OrganPlugin`)

Your plugin class must inherit from the `OrganPlugin` base class, located in `plugins/base.py`, and implement all the abstract methods and properties it defines.

### `name` (property)

You must provide a string-type class attribute that serves as the unique identifier for the plugin. It should be in lowercase.

```python
class MyNewPlugin(OrganPlugin):
    name = "my_new_plugin"
```

### `__init__(self, engine)`

The constructor for the plugin. It receives an instance of the `BodyEngine` as an argument. You should save this `engine` instance for future use in accessing other plugins (dependency injection).

```python
def __init__(self, engine):
    super().__init__(engine)
    # Your initialization logic here
```

### `update(self, tick_duration: float)`

This method is called by the main engine on every time tick (approximately every second). You should implement all state logic that changes autonomously over time here.

### `get_sensations(self) -> list[str]`

This method should return a list of strings, with each string describing a "sensation" produced by this plugin. It should return an empty list when the state is normal.

### `get_state(self) -> dict[str, str]`

This method should return a dictionary used to display the plugin's current state on the TUI. The keys are the display labels, and the values are the string content to be displayed.

## Dependency Management

If your plugin depends on another plugin (e.g., the respiratory plugin needs heart rate data), you can access it through `self.engine` when needed.

```python
def update(self, tick_duration: float):
    circulatory_plugin = self.engine.get_plugin("circulatory")
    if circulatory_plugin:
        # Now you can access its properties
        current_heart_rate = circulatory_plugin.heart_rate
        # ...
```

## Complete Example: Creating a Temperature Plugin

Below is a complete example of a `temperature.py` plugin. You just need to place a file like this into the `plugins/` directory, and it will be automatically loaded and run.

```python
# file: plugins/temperature.py
from plugins.base import OrganPlugin

class TemperaturePlugin(OrganPlugin):
    name = "temperature"

    def __init__(self, engine):
        super().__init__(engine)
        self.current_temp = 37.0
        self.ambient_temp = 25.0 # Ambient temperature

    def update(self, tick_duration: float):
        # The body will slowly move towards the ambient temperature
        if self.current_temp > self.ambient_temp:
            self.current_temp -= 0.1 * tick_duration
        else:
            self.current_temp += 0.1 * tick_duration

    def get_sensations(self) -> list[str]:
        sensations = []
        if self.current_temp < 36.0:
            sensations.append("[Sensation: Feeling cold, skin is cool]")
        elif self.current_temp > 38.0:
            sensations.append("[Sensation: Feeling hot, slightly sweaty]")
        return sensations

    def get_state(self) -> dict[str, str]:
        return {
            "Body Temperature": f"{self.current_temp:.1f}°C",
            "Ambient Temperature": f"{self.ambient_temp:.1f}°C",
        }
```
