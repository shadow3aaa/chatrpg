import time
import os
import importlib
from plugins.base import OrganPlugin

class BodyEngine:
    def __init__(self):
        self.plugins: dict[str, OrganPlugin] = {}
        self.property_map: dict[str, OrganPlugin] = {}
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
                            plugin_instance.register_properties()
                            print(f"[Engine] Loaded plugin: {plugin_instance.name}")
                except Exception as e:
                    print(f"[Engine ERROR] Failed to load plugin {module_name}: {e}")

    def register_property(self, prop_name: str, plugin: OrganPlugin):
        """Registers a property with the engine, mapping it to a plugin."""
        if prop_name in self.property_map:
            print(f"[Engine WARNING] Property '{prop_name}' is already registered. Overwriting.")
        self.property_map[prop_name] = plugin
        print(f"[Engine] Registered property '{prop_name}' to plugin '{plugin.name}'")

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
            # Use the registered properties for a more accurate schema
            for prop_name, owner_plugin in self.property_map.items():
                if owner_plugin == plugin:
                    prop_instance = getattr(plugin, prop_name)
                    prop_type = type(prop_instance).__name__
                    schema += f"- {prop_name}: {prop_type}\n"
            schema += "\n"
            
        return schema

    def apply_impact(self, impact: dict):
        """Applies a dictionary of impacts to the relevant organ properties with strict error handling."""
        # The impact format is expected to be: {"plugin_name": {"prop_name": "+=value"}}
        for plugin_name, properties in impact.items():
            if not isinstance(properties, dict):
                print(f"[Engine ERROR] Invalid impact format for '{plugin_name}'. Expected a dictionary of properties.")
                continue

            for prop_name, value_str in properties.items():
                try:
                    # Clean the value string to extract the number. Handles formats like '+=5.0', '-=2', '5'.
                    cleaned_value_str = "".join(filter(lambda c: c in '-.0123456789', value_str))
                    if not cleaned_value_str:
                        raise ValueError("No numeric value found in string")
                    
                    change = float(cleaned_value_str)
                    lower_prop_name = prop_name.lower()

                    if lower_prop_name not in self.property_map:
                        raise ValueError(f"No plugin registered for property: '{lower_prop_name}'")

                    plugin = self.property_map[lower_prop_name]
                    
                    # Strict check: does the plugin in the impact match the registered owner?
                    if plugin.name.lower() != plugin_name.lower():
                        raise ValueError(f"Mismatched plugin for property '{lower_prop_name}'. Impact specified '{plugin_name}' but property is owned by '{plugin.name}'.")

                    current_value = getattr(plugin, lower_prop_name)
                    setattr(plugin, lower_prop_name, current_value + change)
                    print(f"[Engine] Applied impact: {plugin.name}.{lower_prop_name} changed by {change}")

                except (ValueError, TypeError) as e:
                    # Re-raise the exception to halt execution and provide a full traceback.
                    # This is a deliberate choice for strict, fail-fast debugging.
                    print(f"[Engine CRITICAL] Halting due to error while applying impact for '{plugin_name}.{prop_name}' with value '{value_str}'. Reason: {e}")
                    raise
