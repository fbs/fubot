from core.interface import IFinalize, IPlugin
from twisted.python import log

from importlib import import_module

def filter_interface(plugins, interface):
    """Find all plugins in `plugins` that provide interface `interface`"""
    return [plugin for plugin in plugins if interface.providedBy(plugin)]

def filter_command(plugins, cmd):
    """Find all plugins in `plugins` that accept command `cmd`"""
    return [plugin for plugin in plugins if plugin.accepts_command(cmd)]

def _import(name):
    """Import plugin `name`, return True if  succeeded, false otherwise"""
    return _try_import('plugins.%s.%s' % (name, name))


def _reload(name):
    """Try to reload plugin `name`"""
    ## TEH HORROR
    import sys
    mod = sys.modules['plugins.%s.%s' % (name, name)]
    reload(mod)

def _try_import(name):
    """Try to import plugin `name`"""
    try:
        import_module(name)
    except ImportError:
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
        self.plugins = []

### PRIVATE

    def _remove(self, plugin):
        """Remove a loaded plugin"""
        self.plugins.remove(plugin)

    def _is_loaded(self, name):
        """Return True if a plugin with name `name` is loaded,
        False otherwise"""
        if self._findname(name):
            return True
        return False

    def _findname(self, name):
        """Find and return the plugin with name `name`"""
        for plugin in self.plugins:
            if plugin.name == name:
                return plugin
            return None

### PUBLIC

    def load(self, name):
        """Load a plugin"""
        if self._is_loaded(name):
            return
        log.msg('Loading plugin [%s]' % name)
        _import(name)

    def unload(self, name):
        """Unload a plugin"""
        plugin = self._findname(name)
        if not plugin:
            return
        log.msg('Unloading plugin [%s]' % name)
        _finalize(plugin)
        self._remove(plugin)

    def reload(self, name):
        """Reload a plugin"""
        plugin = self._findname(name)
        if not plugin:
            return
        log.msg('Reloading plugin [%s]' % name)
        _finalize(plugin)
        self._remove(plugin)
        _reload(name)

    def reload_all(self):
        """Reload all loaded plugins"""
        names = []
        log.msg('Reloading all plugins')
        for plugin in self.plugins:
            names.append(plugin.name)
            _finalize(plugin)
            self._remove(plugin)

        self.plugins = []
        for name in names:
            _reload(name)

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
        plugins = self.plugins
        if interface:
            plugins = filter_interface(plugins, interface)
            if command:
                plugins = filter_command(plugins, command)

        return plugins

    def register(self, plugin):
        """Register a new plugin, used by the plugin itself"""
        if IPlugin.providedBy(plugin):
            self.plugins.append(plugin)
            log.msg('Registered plugin [%s] version %s, by %s' %
                    (plugin.name, plugin.version, plugin.author))

## Singleton
plugin_manager = PluginManager()
