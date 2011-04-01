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

import interfaces

def verify_conf_dialog(plugin_class):
    return issubclass(plugin_class, interfaces.IConfigureDialog)
    
def verify_configurable(plugin_obj):
    return isinstance(plugin_obj, interfaces.IConfigureDialog)
