from core.interface import *
from twisted.python import log

class PluginManager(object):
    # __instance = None
    # def __new__(cls):
    #     if not PluginManager.__instance:
    #         PluginManager._instance = object.__new__(cls)
    #     return PluginManager.__instance

    def __init__(self):
        self.plugins = []

    def load(self, plugins):
        # log.msg("Plugins: %s" % plugins)
        for plugin in plugins:
            __import__(plugin['name'])

    def register(self, plugin):
        log.msg("Registering plugin: %s, version %s" %
                (plugin.name, plugin.version))
        if IPlugin.providedBy(plugin):
            self.plugins.append(plugin)

    def filter(self): #, interface=None):
        plugins = self.plugins
#        if interface:
#            pass #filter on interface
        return plugins

plugin_manager = PluginManager()
