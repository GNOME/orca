# -*- coding: utf-8 -*-

# Copyright (C) 2010, J. Félix Ontañón <felixonta@gmail.com>
# Copyright (C) 2011, J. Ignacio Álvarez <neonigma@gmail.com>

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
import gobject

import pluglib
from pluglib.manager import ModulePluginManager
from pluglib.interfaces import PluginManagerError

import store_config

dirname, filename = os.path.split(os.path.abspath(__file__))
PLUGINS_DIR = [os.path.join(dirname, 'baseplugins')]
#PLUGINS_DIR = ['baseplugins']

class TestPluginManager(ModulePluginManager):

    def __init__(self):
        ModulePluginManager.__init__(self, PLUGINS_DIR)
 
    def enable_plugin(self, plugin_name):
        super(TestPluginManager, self).enable_plugin(plugin_name)

    def disable_plugin(self, plugin_name):
        super(TestPluginManager, self).disable_plugin(plugin_name)

    def get_plugin_class(self, plugin_name):
        if self.plugins.has_key(plugin_name):
            return self.plugins[plugin_name]['class']
        else:
            raise PluginManagerError, 'No plugin named %s' % plugin_name

plugmanager = TestPluginManager()
