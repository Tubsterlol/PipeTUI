from cli.command_handler import cli
from plugins.plugin_manager import PluginManager


def load_plugins():
    manager = PluginManager()
    manager.load_plugins()


def main():
    load_plugins()
    cli()


if __name__ == "__main__":
    main()