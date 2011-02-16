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

import exceptions
import abc

class IPlugin(object):
    """Every plugin must implement this interface"""

    __metaclass__ = abc.ABCMeta

    ############### ATTRIBS ################

    def name_getter(self):
        """ You must implement this method in your class """

    def name_setter(self, new_name):
         """ You must implement this method in your class """

    # Name of the plugin
    name = abc.abstractproperty(name_getter, name_setter)


    def description_getter(self):
        """ You must implement this method in your class """

    def description_setter(self, new_description):
         """ You must implement this method in your class """

    # Description of the plugin's behaviour
    description = abc.abstractproperty(description_getter, description_setter)


    def version_getter(self):
        """ You must implement this method in your class """

    def version_setter(self, new_version):
         """ You must implement this method in your class """
                                                                                  
    # Version of the plugin
    version = abc.abstractproperty(version_getter, version_setter)    
    

    def authors_getter(self):
        """ You must implement this method in your class """

    def authors_setter(self, new_authors):
         """ You must implement this method in your class """
                                                                                  
    # Authors of the plugin, separated by comma
    authors = abc.abstractproperty(authors_getter, authors_setter)                    

    def website_getter(self):
        """ You must implement this method in your class """

    def website_setter(self, new_website):
         """ You must implement this method in your class """
                                                                                  
    # Website of the plugin
    website = abc.abstractproperty(website_getter, website_setter)                    

    def icon_getter(self):
        """ You must implement this method in your class """

    def icon_setter(self, new_icon):
         """ You must implement this method in your class """
                                                                                  
    # Icon for the plugin manager
    icon = abc.abstractproperty(icon_getter, icon_setter)


class IPluginManager(object):
    """Every plugin manager must implement this interface"""

    __metaclass__ = abc.ABCMeta

    ############### ATTRIBS ################

    def plugin_paths_getter(self):
        """ You must implement this method in your class """

    def plugin_paths_setter(self, new_plugin_paths):
         """ You must implement this method in your class """

    # List of path that may contain plugins
    plugin_paths = abc.abstractproperty(plugin_paths_getter, plugin_paths_setter)

    def plugins_getter(self):
        """ You must implement this method in your class """

    def plugins_setter(self, new_plugins):
         """ You must implement this method in your class """

    # Set of managed plugins
    plugins = abc.abstractproperty(plugin_paths_getter, plugin_paths_setter)

    ############## METHODS #################

    @abc.abstractmethod
    def scan_plugins():
        """Scan plugin paths looking for plugins"""

    @abc.abstractmethod
    def enable_plugin(plugin):
        """Perform the process of plugin activation"""

    @abc.abstractmethod
    def disable_plugin(plugin):
        """Perform the process of plugin deactivation"""

    @abc.abstractmethod    
    def get_plugins():
        """Return the list of managed plugins"""
    
    @abc.abstractmethod
    def is_plugin_enabled(plugin):
        """Return if plugin was enabled"""

class IConfigurable(object):
    """Allows user customize of settings"""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def load ():
        """Load last option values"""

    @abc.abstractmethod
    def save():
        """Save current option values"""

class IConfigureDialog(IConfigurable):
    """Allow user customize of settings thru configure dialog"""

    __metaclass__ = abc.ABCMeta

    def load ():
        """Load last option values"""

    def save():
        """Save current option values"""

    @abc.abstractmethod
    def configure_dialog(parent):
        """Display preferences dialog"""

class IDependenciesChecker(object):
    """Allows to check for dependencies before run"""

    __metaclass__ = abc.ABCMeta

    ############## ATTRIBS ##############

    def check_err_getter(self):
        """ You must implement this method in your class """

    def check_err_setter(self, new_plugins):
         """ You must implement this method in your class """

    # Message if dependencies was not satisfied
    check_err = abc.abstractproperty(check_err_getter, check_err_setter)

    ############## METHODS ##############

    @abc.abstractmethod
    def check_dependencies():
        """Check for dependencies"""

class IDependenciesResolver(IDependenciesChecker):
    """Resolves not satisfied dependencies"""

    __metaclass__ = abc.ABCMeta

    ############## ATTRIBS ##############

    def check_err_getter(self):
        """ You must implement this method in your class """

    def check_err_setter(self, new_plugins):
         """ You must implement this method in your class """

    # Message if dependencies was not satisfied
    check_err = abc.abstractproperty(check_err_getter, check_err_setter)

    def check_dependencies():
        """Check for dependencies"""

    @abc.abstractmethod
    def resolve_dependencies():
        """Performs the process of installing dependencies"""

class ISignaller(IPluginManager):

    __metaclass__ = abc.ABCMeta
    
    def signals_getter(self):
        """ You must implement this method in your class """

    def signals_setter(self, new_plugins):
         """ You must implement this method in your class """

    # List of signals
    signals = abc.abstractproperty(signals_getter, signals_setter)

    @abc.abstractmethod
    def emit(signal, data):
        """Emit a signal with data"""

    @abc.abstractmethod
    def connect(signal, method):
        """Add a signal handler"""

    @abc.abstractmethod
    def disconnect(signal, method):
        """Remove a signal handler"""

class PluginError(exceptions.Exception):
    pass
    
class PluginManagerError(exceptions.Exception):
    pass
