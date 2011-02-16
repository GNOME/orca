# -*- coding: utf-8 -*-

# Copyright (C) 2010, J. Félix Ontañón <felixonta@gmail.com>

# This file is part of Pluglib.

# Pluglib is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pluglib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pluglib.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import exceptions
import glob
import imp
import inspect
import abc

from interfaces import *

class ModulePluginManager(IPluginManager):
    """A plugin manager that handles with python modules"""

    def __init__(self, plugin_paths=[]):

        self.plugin_paths = plugin_paths
        if not type(self.plugin_paths) is list:
            self.plugin_paths = [self.plugin_paths]
        
        #{'plugin_name': {'class': plugin_class, 'object': plugin_object}
        self.plugins = {}

    def inspect_plugin_module(self, module_name, path):
        plugins = {}

        modfile, name, desc = imp.find_module(module_name, [path])
        try:
            module = imp.load_module(module_name, modfile, name, desc)
            plugins.update([(name, {'class': klass, 'object': None}) 
                for (name, klass) in inspect.getmembers(module, inspect.isclass)
                if issubclass(klass, IPlugin) and name != "IPlugin"])
        except Exception, e:
            raise PluginManagerError, 'Cannot load module %s: %s' % \
                (name, e)
        finally:
            if modfile:
                modfile.close()

        return plugins
        
    def scan_plugins(self):
        new_plugins = {}
        for path in self.plugin_paths:
            if not path in sys.path:
                sys.path.insert(0, path)
            for module in [os.path.basename(os.path.splitext(x)[0])
                    for x in glob.glob(os.path.join(path, '[!_]*.py'))]:
                new_plugins.update(self.inspect_plugin_module(module, path))
                
        new_plugins.update(self.plugins)
        self.plugins = new_plugins

    def enable_plugin(self, plugin_name):
        if not self.is_plugin_enabled(plugin_name):
            plugin_class = self.plugins[plugin_name]['class']

            if issubclass(plugin_class, IDependenciesChecker) \
                    and not plugin_class.check_dependencies():
                raise PluginManagerError, 'Cannot satisfy dependencies for %s: %s' % \
                    (plugin_name, plugin_class.check_err)

            plugin_object = plugin_class()
            if isinstance(plugin_object, IConfigurable):
	        plugin_object.load()
            
            self.plugins[plugin_name]['object'] = plugin_object

    def disable_plugin(self, plugin_name):
        if self.is_plugin_enabled(plugin_name):
            plugin_object = self.plugins[plugin_name]['object']
            if isinstance(plugin_object, IConfigurable):
	        plugin_object.save()
            self.plugins[plugin_name]['object'] = None

    def get_plugins(self):
        return [(plugin_name, plugin['class']) for (plugin_name, plugin) \
            in self.plugins.items()]

    def is_plugin_enabled(self, plugin_name):
        if self.plugins.has_key(plugin_name):
            return self.plugins[plugin_name]['object'] is not None
        else:
            raise PluginManagerError, 'No plugin named %s' % plugin_name

    _plugin_paths = None

    def plugin_paths_getter(self):
        return self._plugin_paths

    def plugin_paths_setter(self, new_plugin_paths):
        self._plugin_paths = new_plugin_paths

    plugin_paths = property(plugin_paths_getter, plugin_paths_setter)
   
    _plugins = None

    def plugins_getter(self):
        return self._plugins

    def plugins_setter(self, new_plugins):
        self._plugins = new_plugins

    plugins = property(plugins_getter, plugins_setter)

# Register implementation
IPluginManager.register(ModulePluginManager)

if __name__ == '__main__':
        print 'Subclass:', issubclass(ModulePluginManager, IPluginManager)
        print 'Instance:', isinstance(ModulePluginManager(), IPluginManager)


