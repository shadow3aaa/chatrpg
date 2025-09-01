import time
import os
import importlib
from plugins.base import OrganPlugin

class BodyEngine:
    def __init__(self):
        self.plugins: dict[str, OrganPlugin] = {}
        self.load_plugins()
        self.last_update_time = time.time()

    def load_plugins(self):
        """Dynamically loads all plugins from the 'plugins' directory."""
        plugin_dir = "plugins"
        for filename in os.listdir(plugin_dir):
            if filename.endswith(".py") and filename != "base.py":
                module_name = f"{plugin_dir}.{filename[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    for item_name in dir(module):
                        item = getattr(module, item_name)
                        if isinstance(item, type) and issubclass(item, OrganPlugin) and item is not OrganPlugin:
                            plugin_instance = item(self)
                            self.plugins[plugin_instance.name] = plugin_instance
                            print(f"[Engine] Loaded plugin: {plugin_instance.name}")
                except Exception as e:
                    print(f"[Engine ERROR] Failed to load plugin {module_name}: {e}")

    def get_plugin(self, name: str) -> OrganPlugin | None:
        """Gets a loaded plugin by its name."""
        return self.plugins.get(name)

    def update(self):
        current_time = time.time()
        tick_duration = current_time - self.last_update_time
        self.last_update_time = current_time

        if tick_duration > 0:
            for plugin in self.plugins.values():
                plugin.update(tick_duration)

    def get_all_sensations(self) -> list[str]:
        all_sensations = []
        for plugin in self.plugins.values():
            all_sensations.extend(plugin.get_sensations())
        return all_sensations

    def get_full_state(self) -> dict[str, dict]:
        full_state = {}
        for name, plugin in self.plugins.items():
            full_state[name.capitalize()] = plugin.get_state()
        return full_state

    def get_organs_schema(self) -> str:
        """Generates a schema of all organs and their attributes for the LLM."""
        schema = "# Organ Schema\n"
        schema += "You must use the following schema to format your JSON response. Do not add attributes not listed here.\n\n"
        
        for name, plugin in self.plugins.items():
            schema += f"## Plugin: {name}\n"
            # Inspect attributes
            attrs = {k: v for k, v in plugin.__dict__.items() if not k.startswith('_') and not callable(v)}
            for attr, value in attrs.items():
                attr_type = type(value).__name__
                schema += f"- {attr}: {attr_type}\n"
            schema += "\n"
            
        return schema

    def apply_impact(self, impact: dict):
        for key, value in impact.items():
            try:
                change = float(value)
                lower_key = key.lower()
                
                # This logic could be improved by having plugins register the keys they respond to.
                # For now, we keep the simple mapping.
                if 'heart_rate' in lower_key:
                    self.get_plugin("circulatory").heart_rate += change
                elif 'adrenaline' in lower_key:
                    self.get_plugin("endocrine").adrenaline += change
                elif 'cortisol' in lower_key:
                    self.get_plugin("endocrine").cortisol += change
                elif 'endorphins' in lower_key:
                    self.get_plugin("endocrine").endorphins += change
                elif 'fullness' in lower_key:
                    self.get_plugin("digestive").fullness += change
                # ... and so on

            except (ValueError, TypeError, AttributeError) as e:
                print(f"[Engine WARNING] Could not apply impact: {key}:{value}. Error: {e}")
