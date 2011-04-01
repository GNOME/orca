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

"""Classes that manages all events"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2011 Consorcio Fernando de los Rios."
__license__   = "LGPL"

import sys

class PluginEvent:
    def __init__(self, name):
        self.name = name
        self.listeners = {}

    def add(self, function, data=None):
        self.listeners[function] = data

    def delete(self, function):
        self.listeners.pop(function)

    def called(self, data=None):
        for function, d in self.listeners.items():
            if data is None:
                if d is None:
                    function()
                else:
                    if type(d) == type([]):
                        function(*d)
                    elif type(d) == type({}):
                        function(**d)
                    else:
                        function(d)
            else:
                if type(data) == type([]):
                    function(*data)
                elif type(data) == type({}):
                    function(**data)
                else:
                    function(data)

class PluginEventManager:
    def __init__(self):
        self.events = {}

    def list_events(self):
        return self.events

    def add_event(self, Event):
        self.events[Event.name] = Event

    def del_event(self, Event):
        self.events.pop(Event.name)

    def connect(self, event, function, data=None):
        print "and the function is: " + str(function)
        self.events[event].add(function, data)

    def disconnect(self, event, function):
        self.events[event].delete(function)

    def signal(self, event, data=None):
        try:
            if data is None:
                self.events[event].called()
            else:
                self.events[event].called(data)
        except Exception, e:
            print "ERROR: Event "+str(event)+" not in queue"
            return

plug_event_manager = PluginEventManager()
