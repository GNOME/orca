# Orca Tools
#
# Copyright 2006-2008 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Generates an F12 key press/release."""

import time

import bonobo
import ORBit

ORBit.load_typelib("Accessibility")
ORBit.CORBA.ORB_init()

import Accessibility
import Accessibility__POA

listeners = []
keystrokeListeners = []

def main():
    registry = bonobo.get_object("OAFIID:Accessibility_Registry:1.0",
                                 "Accessibility/Registry")
    d = registry.getDeviceEventController()
    d.generateKeyboardEvent(96, "", Accessibility.KEY_PRESSED_EVENT)
    time.sleep(0.1)
    d.generateKeyboardEvent(96, "", Accessibility.KEY_RELEASED_EVENT)
    
if __name__ == "__main__":
    main()
