from core.interface import *
from twisted.python import log

def filter_interface(plugins, interface):
    return filter(lambda p: interface.providedBy(p), plugins)

def filter_command(plugins, cmd):
    return filter(lambda p: p.accepts_command(cmd), plugins)

class PluginManager(object):
    def __init__(self):
        self.plugins = []

    def load(self, plugins):
        # log.msg("Plugins: %s" % plugins)
        for plugin in plugins:
            __import__(plugin['name'])

    def register(self, plugin, command=''):
        if IPlugin.providedBy(plugin):
            self.plugins.append(plugin)
        log.msg("Registered plugin: %s, version %s, by %s" %
                (plugin.name, plugin.version, plugin.author))

    def filter(self, interface=None, command=None):
        plugins = self.plugins
        if interface:
            plugins = filter_interface(plugins, interface)
        if command:
            plugins = filter_command(plugins, command)

        return plugins

plugin_manager = PluginManager()
