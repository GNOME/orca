# Orca
#
# Copyright 2011 Consorcio Fernando de los Rios.
# Author: J. Ignacio Alvarez <jialvarez@emergya.es>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Class to manage plugins and derivated"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2011 Consorcio Fernando de los Rios."
__license__   = "LGPL"

import os
import sys
import exceptions
import glob
import imp
import inspect
import abc

from orca.pluglib.interfaces import IPluginManager, IPlugin, ICommand, \
    IConfigurable, IDependenciesChecker, PluginManagerError, IPresenter

dirname, filename = os.path.split(os.path.abspath(__file__))
PLUGINS_DIR = [os.path.join(dirname, '..', 'baseplugins')]

class ModulePluginManager(IPluginManager):
    """A plugin manager that handles with python modules"""

    def __init__(self, plugin_paths=PLUGINS_DIR):

        self.plugin_paths = plugin_paths
        if not type(self.plugin_paths) is list:
            self.plugin_paths = [self.plugin_paths]
        
        #{'plugin_name': {'class': plugin_class, 'object': plugin_object,
        # 'type': plugin_type, 'registered':, if_registered}
        self.plugins = {}

# nacho's
#        self.store_conf = store_config.StoreConfig()
#        self.plugins_conf = self.store_conf.getPlugins()
        self.plugins_conf = {}

    def inspect_plugin_module(self, module_name, path):
        plugins = {}

        if self.plugins_conf:
            plugin_exists = module_name in self.plugins_conf['plugins']
        else:
            plugin_exists = False
            
        # plugin don't exists in conf or don't have any plugins
        if plugin_exists == False or not self.plugins_conf:
            try:
                modfile, name, desc = imp.find_module(module_name, [path])
                # the idea is not repeat this load unnecessarily
                module = imp.load_module(module_name, modfile, name, desc)
                try:
                    active = self.plugins_conf[module_name]['active'] \
                            if self.plugins_conf and module_name in self.plugins_conf \
                            else False

                    # REGISTERED NOT USED... IS ALL DONE WITH ACTIVE FIELD! (OR NOT?)
                    registered = self.plugins_conf[module_name]['registered'] \
                                if self.plugins_conf and \
                                module_name in self.plugins_conf \
                                else True
         
                    for (name, klass) in inspect.getmembers(module, \
                                    inspect.isclass):
                        if issubclass(klass, IPlugin) and name != "IPlugin":
                            plugDict = {'class':klass, \
			                   'object': None, \
                                           'name': name, 'active': active, \
                                           'type': None, \
                                           'registered': registered, \
                                           'path': path}

		            plugins.update({module_name : plugDict})
                            self.setPluginTypes(plugDict, module)

                    print "Loading '%s' plugin: done!" % str(module_name)
                    
                except LookupError, e:
                    raise PluginManagerError, \
                            'Update dictionary fails in %s: %s' % (name, e)
    
                # ADD PLUGIN!
                # pass name, module_name and registered or not
# nacho's
#                self.store_conf.addPlugin(name, registered, module_name, path)
    
            except Exception, e:
                raise PluginManagerError, 'Cannot load module %s: %s' % \
                    (name, e)
            finally:
                if modfile:
                    modfile.close()

        return plugins

    def scanPluginsDir(self):
        print "Scanning plugins..."
        # CHECK BASEPLUGINS FOR PLUGINS
        # In inspect_plugin_module we compare with the plugins list
        # in the appropiate backend form and if a plugin is active,
        # we will load it
        new_plugins = {}
        for path in self.plugin_paths:
            if not path in sys.path:
                sys.path.insert(0, path)
            for module in [os.path.basename(os.path.splitext(x)[0])
                    for x in glob.glob(os.path.join(path, '[!_]*.py'))]:
                new_plugins.update(self.inspect_plugin_module(module, path))
                
        new_plugins.update(self.plugins)
        self.plugins = new_plugins

    def load_class_in_plugin(self, dict_plugins, module_name, path):
        modfile, name, desc = imp.find_module(module_name, path)
        
        # the idea is not repeat this load unnecessarily
        module = imp.load_module(module_name, modfile, name, desc)
        
        for (the_name, klass) in inspect.getmembers(module, inspect.isclass):
            if issubclass(klass, IPlugin) and the_name != "IPlugin":
                klass_update = {'class': klass}
                object_update = {'object': None}
                type_update = {'type': 'Generic'}
                dict_plugins.update(type_update)               
                dict_plugins.update(klass_update)
                dict_plugins.update(object_update)
# nacho's
#            if issubclass(klass, ICommand) and the_name != "ICommand":
#                type_update = {'type': 'Command'}
#                dict_plugins.update(type_update) 

    def setPluginTypes(self, plugin, module):
        print module
        types = []
        for (the_name, klass) in inspect.getmembers(module, inspect.isclass):
            if issubclass(plugin['class'], ICommand) and the_name != "ICommand":
                if 'Command' not in types: types.append('Command') 
            if issubclass(plugin['class'], IPresenter) and the_name != "IPresenter":
                if 'Presenter' not in types: types.append('Presenter')
        plugin.update({'type' : types})

    def scan_plugins(self):
        # Compare
        self.scanPluginsDir()
        
        # LOAD FROM STORE_CONF
        if self.plugins_conf:
            # take the plugins list in the backend
            self.plugins = self.plugins_conf.copy()
            load_plugins = self.plugins['plugins']
    
            for module_name, data in load_plugins.iteritems():
                if load_plugins[module_name]['active'] == True:
                    try:
                        # if active, add the class into the plugin list
                        self.load_class_in_plugin(load_plugins[module_name], 
                                module_name, [load_plugins[module_name]['path']])

                        plugin_class = load_plugins[module_name]['class']

                        # we have the class now, we can get an object
                        plugin_object = plugin_class()
                        if isinstance(plugin_object, IConfigurable):
                	        plugin_object.load()
                        
                        load_plugins[module_name]['object'] = plugin_object
                        print "Starting existent module: " + str(module_name)
                    except Exception, e:
                        raise PluginManagerError, 'Cannot load module %s: %s' % \
                            (module_name, e)
                else:
                    # plugin not active, bring into plugin list 
                    # maintained in memory but not get the class
                    load_plugins[module_name].update({'class': None})
                    load_plugins[module_name].update({'object': None})
 
            self.plugins = load_plugins

    def enablePlugin(self, plugin_name):

# nacho's
#        # first, make the plugin active in appropiated backend
#        enabling_plugins = self.store_conf.getPluginByName(plugin_name)
#        enabling_plugins['active'] = True
#        self.store_conf.updatePlugin({plugin_name: enabling_plugins})

        if self.plugins:
            #print self.plugins
            # load the class in the plugin list maintained in memory
            self.load_class_in_plugin(self.plugins[plugin_name], plugin_name, PLUGINS_DIR)

            plugin_class = self.plugins[plugin_name]['class']

            # this code is not checked actually 
            if issubclass(plugin_class, IDependenciesChecker) \
                    and not plugin_class.check_dependencies():
                raise PluginManagerError, 'Cannot satisfy dependencies for %s: %s' % \
                    (plugin_name, plugin_class.check_err)

            # instantiate an object, we have the class now
            plugin_object = plugin_class()
            plugin_object.enable()

            # nacho's
            # this code is not checked actually, but I know
            # what to do with it
            #if isinstance(plugin_object, IConfigurable):
    	    #    plugin_object.load()
            
            self.plugins[plugin_name]['object'] = plugin_object

    def disablePlugin(self, plugin_name):
# nacho's
#        if self.is_plugin_enabled(plugin_name):
        plugin_object = self.plugins[plugin_name]['object']

# nacho's
#        if isinstance(plugin_object, IConfigurable):
#            plugin_object.save()
#
#        if isinstance(plugin_object, ICommand):
#            plugin_object.removePluginKeybinding()

        plugin_object.disable()
        self.plugins[plugin_name]['object'] = None

# nacho's
#            # make the plugin inactive in the appropiated backend
#            disabling_plugins = self.store_conf.getPluginByName(plugin_name)
#            disabling_plugins['active'] = False
#            self.store_conf.updatePlugin({plugin_name: disabling_plugins})
    
        
        print "Unloaded module " + str(plugin_name)
            
        # this *only* delete the name from sys.modules,
        # not the module itself. See http://bit.ly/gbjPnB 
        del (plugin_name)


    def get_plugins(self):
        return [(plugin_name, plugin['class'], 
                 plugin['type'], plugin['registered'], plugin['name']) 
            for (plugin_name, plugin) in self.plugins.items()]

    def is_plugin_enabled(self, plugin_name):
        check_plugin = self.store_conf.getPluginByName(plugin_name)
        return check_plugin['active']

    def get_plugin_class(self, plugin_name):
        if self.plugins.has_key(plugin_name):
            return self.plugins[plugin_name]['class']
        else:
            raise PluginManagerError, 'No plugin named %s' % plugin_name

    def is_plugin_loaded(self, plugin_name):
        if self.plugins.has_key(plugin_name):
            return self.plugins[plugin_name]['object'] is not None
        else:
            raise PluginManagerError, 'No plugin named %s' % plugin_name

    # ATTRIBS REQUIRES TO ACCOMPLISH THE ABSTRACTION CONCEPT

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


    # Configuration purposes

#    def addPluginConf(self, name, registered, module_name, path):
#        # receives a dict in the following way
#        # 'chat': { 'name': 'Chat plugin',
#        #           'active': True,
#        #           'registered': False
#        #           'type': 'Commander'
#        #           'path': /bar/foo }
#
#        plugin_data = {module_name: {'name': name, 'active': False, 
#                       'type': None, 'registered': registered,
#                       'path': path}}
#
#        self.sm.addPlugin(plugin_data)
#
#        print "Adding plugin: " + str(plugin_data)
#    

    def isEnabled(self, plugin_name):
        if self.getPluginObject(plugin_name) == None:
            return False
        else:
            return True

    def getPluginObject(self, plugin_name):
        if not 'object' in self.plugins[plugin_name]:
            return None
        else:
            return self.plugins[plugin_name]['object']

    def getPlugins(self):
        self.scanPluginsDir()
        plugins = self.plugins
        for plug in self.plugins:
            if 'class' in plugins[plug]: plugins[plug].pop('class')
            if 'object' in plugins[plug]: plugins[plug].pop('object')
            if 'path' in plugins[plug]: plugins[plug].pop('path')
            if 'registered' in plugins[plug]: plugins[plug].pop('registered')

        return plugins
#
#    def updatePlugin(self, plugin_to_update):
#        self.plugins_conf = self.sm.updatePlugin(plugin_to_update)
#
#    def saveConf(self, plugins_to_save):
#        self.sm.saveConf(plugins_to_save)

# Register implementation
IPluginManager.register(ModulePluginManager)

plugmanager = ModulePluginManager(PLUGINS_DIR)
