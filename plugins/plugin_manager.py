import importlib
import os


class PluginManager:

    def __init__(self):
        self.plugins = []

    def load_plugins(self):

        plugin_folder = "plugins"

        for file in os.listdir(plugin_folder):

            if file.endswith("_plugin.py") and file != "base_plugin.py":

                module_name = file[:-3]

                module = importlib.import_module(f"plugins.{module_name}")

                if hasattr(module, "PluginImpl"):

                    plugin_class = getattr(module, "PluginImpl")

                    plugin = plugin_class()

                    plugin.initialize()

                    self.plugins.append(plugin)

                    print(f"Loaded plugin: {plugin.name}")