import os
import importlib

class PluginManager:
    def __init__(self):
        self.plugins = []

    def load_plugins(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        plugin_folder = os.path.join(base_dir, "plugins")

        for file in os.listdir(plugin_folder):
            if file.endswith(".py") and file != "__init__.py":
                module_name = f"plugins.{file[:-3]}"
                module = importlib.import_module(module_name)
                if hasattr(module, "Plugin"):
                    self.plugins.append(module.Plugin())