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

import gconf
import types

from interfaces import IConfigurable, PluginError

__all__ = ['GConfStore', 'PickleStore']

class GConfKeysDict(dict):
    VALID_KEY_TYPES = (bool, str, int, float, list, tuple)
    
    def __init__(self, *args, **kwargs):
        super(dict, self).__init__(*args, **kwargs)
    
    def __setitem__(self, key, val):
        if not type(val) in self.VALID_KEY_TYPES:
            raise PluginError, 'Invalid %s for gconf key' % type(val)
        else:
            dict.__setitem__(self, key, val)

# Partially based on http://crysol.org/node/758
class GConfStore(IConfigurable):
                
    defaults = {}

    def __init__(self, key):
        self.__app_key = key
        self.__client = gconf.client_get_default()
        
        self.options = GConfKeysDict()
        self.options.update(self.defaults)

    def load(self): 
        casts = {gconf.VALUE_BOOL:   gconf.Value.get_bool,
            gconf.VALUE_INT:    gconf.Value.get_int,
            gconf.VALUE_FLOAT:  gconf.Value.get_float,
            gconf.VALUE_STRING: gconf.Value.get_string,
            gconf.VALUE_LIST:   gconf.Value.get_list}
    
        for entry in self.__client.all_entries(self.__app_key):
            gval = self.__client.get(entry.key)
            if gval == None: continue
            
            if gval.type == gconf.VALUE_LIST:
                string_list = [item.get_string() for item in gval.get_list()]
                self.options[entry.key.split('/')[-1]] = string_list
            else:
                self.options[entry.key.split('/')[-1]] = casts[gval.type](gval)
 
    def save(self):
        casts = {types.BooleanType: gconf.Client.set_bool,
            types.IntType:     gconf.Client.set_int,
            types.FloatType:   gconf.Client.set_float,
            types.StringType:  gconf.Client.set_string,
            types.ListType:    gconf.Client.set_list,
            types.TupleType:   gconf.Client.set_list}

        #TODO: To clear the gconf dir before save, is it convenient?
        for name, value in self.options.items():
            if type(value) in (list, tuple):
                string_value = [str(item) for item in value]
                casts[type(value)](self.__client, self.__app_key + '/' + name,
                    gconf.VALUE_STRING, string_value)
            else:
                casts[type(value)](self.__client, self.__app_key + '/' + name, 
                    value)

import os
import cPickle

class PickleStore(IConfigurable):
                
    defaults = {}

    def __init__(self, path):
        self.__path = path
        self.options = {}
        self.options.update(self.defaults)
        
    def load(self):
        if os.path.exists(self.__path):
            filep = open(self.__path, 'r')
            self.options = cPickle.load(filep)
            filep.close()
    
    def save(self):
        if not os.path.exists(os.path.dirname(self.__path)):
            os.makedirs(os.path.dirname(self.__path))
            
        filep = open(self.__path, 'w')
        cPickle.dump(self.options, filep)
        filep.close()
