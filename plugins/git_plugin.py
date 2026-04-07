from plugins.base_plugin import Plugin


class PluginImpl(Plugin):

    name = "Git Integration"

    def initialize(self):

        print("Git plugin initialized")

    def pull_repository(self, repo):

        print(f"Pulling repository {repo}")