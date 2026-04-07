from cli.command_handler import cli
from plugins.plugin_manager import PluginManager


def load_plugins():

    manager = PluginManager()
    manager.load_plugins()


if __name__ == "__main__":

    load_plugins()

    cli()