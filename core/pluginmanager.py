from core.interface import *
from twisted.python import log

from importlib import import_module

def filter_interface(plugins, interface):
    return filter(lambda p: interface.providedBy(p), plugins)

def filter_command(plugins, cmd):
    return filter(lambda p: p.accepts_command(cmd), plugins)

def _import(name):
    if _try_import('plugins.%s.%s' % (name, name)):
        return True
    return False

def _reload(name):
    ## TEH HORROR
    import sys
    mod = sys.modules['plugins.%s.%s' % (name, name)]
    reload(mod)

def _try_import(name):
    try:
        import_module(name)
    except ImportError:
        return False
    else:
        return True

class PluginManager(object):
    def __init__(self):
        self.plugins = []

    def load(self, name):
        if self.is_loaded(name):
            log.msg('Plugin [%s] already loaded!' % name)
            return
        _import(name)

    def reload(self, name):
        p = self.findname(name)
        if not p:
            return
        self.plugins.remove(p)
        _reload(name)

    def findname(self, name):
        for p in self.plugins:
            if p.name == name:
                return p
        return None

    def is_loaded(self, name):
        if self.findname(name):
            return True
        return False

    def reload_all(self):
        names = []
        for p in self.plugins:
            names.append(p.name)
            if IFinalize.providedBy(p):
                p.finalize()

            self.plugins.remove(p)

        self.plugins = []
        for n in names:
            _reload(n)

    def filter(self, interface=None, command=None):
        plugins = self.plugins
        if interface:
            plugins = filter_interface(plugins, interface)
        if command:
            plugins = filter_command(plugins, command)

        return plugins

    def register(self, plugin):
        if IPlugin.providedBy(plugin):
            self.plugins.append(plugin)
        log.msg("Registered plugin [%s] version %s, by %s" %
                (plugin.name, plugin.version, plugin.author))

plugin_manager = PluginManager()
