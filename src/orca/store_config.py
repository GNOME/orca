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

"""Instance for managing the plugings."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2011 Consorcio Fernando de los Rios."
__license__   = "LGPL"

from settings_manager import SettingsManager

class StoreConfig:
    def __init__(self):
        # get settings_manager instance
        self.sm = SettingsManager()

    def addPlugin(self, name, registered, module_name, path):
        # receives a dict in the following way
        # 'chat': { 'name': 'Chat plugin',
        #           'active': True,
        #           'registered': False
        #           'type': 'Commander'
        #           'path': /bar/foo }

        plugin_data = {module_name: {'name': name, 'active': False, 
                       'type': None, 'registered': registered,
                       'path': path}}

        self.sm.addPlugin(plugin_data)

        print "Adding plugin: " + str(plugin_data)
    
    def getPluginByName(self, plugin_name):
        return self.sm.getPluginByName(plugin_name)

    def getPlugins(self):
        return self.sm.loadPlugins()

    def updatePlugin(self, plugin_to_update):
        self.plugins_conf = self.sm.updatePlugin(plugin_to_update)

    def saveConf(self, plugins_to_save):
        self.sm.saveConf(plugins_to_save)
