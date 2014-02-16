from twisted.python import log

from importlib import import_module
import sys

from core.interface import IFinalize

def filter_interface(plugins, interface):
    """Find all plugins in `plugins` that provide interface `interface`"""
    return [plugin for plugin in plugins if interface.providedBy(plugin)]

def filter_command(plugins, cmd):
    """Find all plugins in `plugins` that accept command `cmd`"""
    return [plugin for plugin in plugins if plugin.accepts_command(cmd)]

def _import_or_reload(name):
    """Import or reload the plugin, return the loaded module"""
    pname = 'plugins.%s.%s' % (name, name)
    mod = sys.modules.get(pname, None)
    if mod:
        return reload(mod)
    else:
        return _try_import(pname)

def _try_import(name):
    """Try to import plugin `name`"""
    try:
        mod = import_module(name)
    except ImportError as e:
        log.msg('Failed to import [%s]: %s' % (name, e))
        mod = None

    return mod

class PluginLoader(object):
    """Does the loading stuff"""
    def __init__(self):
        self.plugins = dict()

    def filter(self, names_set, interface=None, command=None):
        """Return all enabled plugins that are in names_set"""
        plugins = [self.plugins[d] for d in self.plugins if d in names_set]

        if interface:
            plugins = filter_interface(plugins, interface)

        if command:
            plugins = filter_command(plugins, command)

        return plugins

    def load(self, name):
        """Load a plugin"""
        if name in self.plugins:
            return True # already loaded

        module = _import_or_reload(name)
        if not module:
            log.msg('Unable to load module [%s]' % name)
            return False # unable to load module

        if not hasattr(module, 'register'):
            log.msg('Module has no attribute register [%s]' % name)
            return False # no register function, unable to use

        plugin = module.register()
        self.plugins[plugin.name] = plugin
        log.msg('[PluginManager] registered plugin [%s]' % plugin.name)
        return True

    def unload(self, name):
        """Unload a plugin"""
        if name not in self.plugins:
            return # not loaded

        plugin = self.plugins.pop(name)

        if IFinalize.providedBy(plugin):
            plugin.finalize()

    def unload_all(self):
        """Unload all plugins"""
        names = [name for name in self.plugins]
        for name in names:
            self.unload(name)

    def reload(self, name):
        """Reload a plugin"""
        self.unload(name)
        self.load(name)

    def reload_all(self):
        """Reload all plugins"""
        names = [name for name in self.plugins]
        for name in names:
            self.reload(name)

class PluginManager(object):
    """Does the stuff"""
    def __init__(self):
        self.map = dict()
        self.globals = set()
        self.loader = PluginLoader()


    def add_network(self, network):
        """Add a network to the PluginManager"""
        if network not in self.map:
            self.map[network] = dict()
            log.msg('[PluginManager] added network [%s]' % network)

    def add_channel(self, network, channel):
        """Add a channel to the PluginManager"""
        self.add_network(network)
        if channel not in self.map[network]:
            self.map[network][channel] = set()
            log.msg('[PluginManager] added channel [%s:%s]' %
                    (network, channel))

    def stop(self):
        """Stop the plugin manager, unload all plugins"""
        self.map.clear()
        self.loader.unload_all()

    def enable(self, network, channel, plugin_name):
        """Enable a plugin"""
        if self.loader.load(plugin_name):
            self.map[network][channel].add(plugin_name)
            log.msg('[PluginManager] Enable plugin [%s] for [%s %s]' %
                    (name, network, channel))

    def enable_global(self, plugin_name):
        """Enable a global plugin"""
        if self.loader.load(plugin_name):
            self.globals.add(plugin_name)
            log.msg('[pluginmanager] Enable global plugin [%s]' % plugin_name)

    def disable(self, network, channel, plugin_name):
        """Disable a plugin"""
        if plugin_name in self.map[network][channel]:
            self.map[network][channel].remove(plugin_name)
            log.msg('[pluginmanager] Disable plugin [%s] for [%s %s]' %
                    (name, network, channel))

    def disable_global(self, plugin_name):
        """Disable a global plugin"""
        if plugin_name in self.globals:
            self.globals.remove(plugin_name)
            log.msg('[pluginmanager] Disable global plugin [%s]' % plugin_name)

    def filter(self, network, channel, interface=None, command=None):
        """Return a list of plugins matching the filter parameters"""
        if channel:
            plugin_names = self.map[network][channel].union(self.globals)
        else:
            plugin_names = self.globals

        return self.loader.filter(plugin_names, interface, command)

    def reload_plugin(self, name):
        """Reload a plugin"""
        log.msg('[pluginmanager] Reloading plugin [%s]' % name)
        self.loader.reload(name)

    def reload_all_plugins(self):
        """Reload all plugins"""
        log.msg('[pluginmanager] Reloading all plugins')
        self.loader.reload_all()
