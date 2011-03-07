# -*- coding: utf-8 -*-

# Copyright (C) 2011, J. Ignacio Álvarez <neonigma@gmail.com>

# This file is part of Pluglib ABC.

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

import sys

class Event:
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

class EventManager:
    def __init__(self):
        self.events = {}

    def add_event(self, Event):
        self.events[Event.name] = Event

    def del_event(self, Event):
        self.events.pop(Event.name)

    def connect(self, event, function, data=None):
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

event_manager = EventManager()
