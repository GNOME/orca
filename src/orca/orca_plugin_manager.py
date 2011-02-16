import os
import gobject

import pluglib
from pluglib.manager import ModulePluginManager
from pluglib.confstore import GConfStore
from pluglib.interfaces import PluginManagerError

PLUGINS_DIR = ['baseplugins']
GCONF_DIR = '/apps/popoter/applet/plugins'

class SignalManager(gobject.GObject):

    __gsignals__ = {
        'plugin_enabled': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                (gobject.TYPE_PYOBJECT,)),
        'plugin_disabled': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                (gobject.TYPE_PYOBJECT,)),
    }

    def __init__(self):
        gobject.GObject.__init__(self)

    def emit_signal(self, signal_str, plugin_name):
        self.emit(signal_str, plugin_name)

class TestPluginManager(ModulePluginManager, GConfStore):

    defaults = {
        'active_plugins': [],
    }

    signal_manager = SignalManager()
 
    def __init__(self):
        ModulePluginManager.__init__(self, PLUGINS_DIR)
        GConfStore.__init__(self, GCONF_DIR)

        self.load()
 
    def restore(self):
        for plugin_name in self.options['active_plugins']:
            if plugin_name in self.plugins.keys():
                self.enable_plugin(plugin_name, emit=False)

    def cleanup(self):
        for plugin_object in [plugin['object'] for plugin in self.plugins.values() \
                if pluglib.verify_configurable(plugin['object'])]:
            plugin_object.save()

    def enable_plugin(self, plugin_name, emit=True):
        super(TestPluginManager, self).enable_plugin(plugin_name)

        if not plugin_name in self.options['active_plugins']:
            self.options['active_plugins'].append(plugin_name)
        self.save()

        if emit:
            self.signal_manager.emit_signal('plugin_enabled', plugin_name)

    def disable_plugin(self, plugin_name, emit=True):
        super(TestPluginManager, self).disable_plugin(plugin_name)

        if plugin_name in self.options['active_plugins']:
            self.options['active_plugins'].remove(plugin_name)
        self.save()

        if emit:
            self.signal_manager.emit_signal('plugin_disabled', plugin_name)

    def get_plugin_class(self, plugin_name):
        if self.plugins.has_key(plugin_name):
            return self.plugins[plugin_name]['class']
        else:
            raise PluginManagerError, 'No plugin named %s' % plugin_name

    def get_plugin_status(self, plugin_name):
        for plugin_id, plugin in plugmanager.get_plugins():
            if plugin.name != None and plugin_name == plugin.name:
                if plugmanager.is_plugin_enabled(plugin_id): return plugin_id
                else: return False

plugmanager = TestPluginManager()

