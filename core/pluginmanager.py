from core.interface import IFinalize, IPlugin, IInitialize
from twisted.python import log

from importlib import import_module
import sys

def filter_interface(plugins, interface):
    """Find all plugins in `plugins` that provide interface `interface`"""
    return [plugin for plugin in plugins if interface.providedBy(plugin)]

def filter_command(plugins, cmd):
    """Find all plugins in `plugins` that accept command `cmd`"""
    return [plugin for plugin in plugins if plugin.accepts_command(cmd)]

def _import(name):
    """Import plugin `name`, return True if  succeeded, false otherwise"""
    return _try_import('plugins.%s.%s' % (name, name))


def _import_or_reload(name):
    """Try to import or reload plugin `name`"""
    ## TEH HORROR
    pname = 'plugins.%s.%s' % (name, name)
    mod = sys.modules.get(pname, None)
    if  mod:
        reload(mod)
    else:
        _try_import(pname)

def _try_import(name):
    """Try to import plugin `name`"""
    try:
        import_module(name)
    except ImportError as e:
        log.msg('Failed to import [%s]: %s' % (name, e))
        return False
    else:
        return True

def _finalize(plugin):
    """Run finalize the plugin if the plugin provides that interface"""
    if IFinalize.providedBy(plugin):
        plugin.finalize()

class PluginManager(object):
    """PluginManger singleton class"""

    stopped = False

    def __init__(self):
        self.plugins = {}

### PRIVATE
    def _remove(self, name):
        """Remove a loaded plugin"""
        self.plugins.pop(name)

    def _add(self, plugin):
        """Add a newly loaded plugin"""
        self.plugins[plugin.name] = plugin

    def _is_loaded(self, name):
        """Return True if a plugin with name `name` is in the plugins list,
        False otherwise"""
        if self._findname(name):
            return True
        return False

    def _findname(self, name):
        """Find and return the plugin with name `name`"""
        return self.plugins.get(name, None)

### PUBLIC

    def load(self, name):
        """Load a plugin"""
        if self._is_loaded(name):
            log.msg('[load] Plugin already loaded [%s]' % name)
            return
        log.msg('[load] Loading plugin [%s]' % name)
        _import_or_reload(name)

    def unload(self, name):
        """Unload a plugin"""
        plugin = self._findname(name)
        if not plugin:
            log.msg('[unload] Plugin not loaded [%s]' % name)
            return
        log.msg('[unload] Unloading plugin [%s]' % name)
        _finalize(plugin)
        self._remove(name)

    def reload(self, name):
        """Reload a plugin"""
        plugin = self._findname(name)
        if not plugin:
            log.msg('[reload] Plugin not loaded [%s]' % name)
            return
        log.msg('[reload] Reloading plugin [%s]' % name)
        _finalize(plugin)
        self._remove(name)
        _import_or_reload(name)

    def reload_all(self):
        """Reload all loaded plugins"""
        #log.msg('Called reload')
        names = []
        log.msg('[reload_all] Reloading all plugins %s' % names)
        for name in self.plugins:
            plugin = self.plugins[name]
            names.append(name)
            _finalize(plugin)

        self.plugins = {}
        for name in names:
            _import_or_reload(name)

    def stop(self):
        """Stop the pluginmanager, finalize and remove all plugins"""
        if self.stopped:
            return
        self.stopped = True
        log.msg('Stopping the plugin manager')
        for plugin in self.plugins:
            _finalize(plugin)
            self.plugins = []

    def filter(self, interface=None, command=None):
        "Return a list of plugins matching the filter options"""
        plugins = [self.plugins[d] for d in self.plugins]
        if interface:
            plugins = filter_interface(plugins, interface)
        if command:
            plugins = filter_command(plugins, command)

        return plugins

    def register(self, plugin):
        """Register a new plugin, used by the plugin itself"""
        if IPlugin.providedBy(plugin):
            self._add(plugin)
            log.msg('Registered plugin [%s] version %s, by %s' %
                    (plugin.name, plugin.version, plugin.author))
        if IInitialize.providedBy(plugin):
            log.msg('Initializing plugin [%s]' % plugin.name)
            plugin.initialize()

## Singleton
plugin_manager = PluginManager()
