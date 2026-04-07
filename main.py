from cli.command_handler import cli
from plugins.plugin_manager import PluginManager
from cli.alert_commands import alerts



def load_plugins():

    manager = PluginManager()
    manager.load_plugins()

cli.add_command(alerts)

if __name__ == "__main__":

    load_plugins()

    cli()
