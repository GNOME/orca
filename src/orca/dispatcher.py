# Orca
#
# Copyright 2004 Sun Microsystems Inc.
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
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

# This hash table maps at-spi event names to Python function names
# which are to be used in scripts.  For example, it maps "focus:"
# events to call a script function called onFocus and
# "window:activate" to onWindowActivated


event = {}

event["onWindowActivated"] = "window:activate"
event["onWindowDestroyed"] = "window:destroy"
event["onFocus"] = "focus:"
event["onStateChanged"] = "object:state-changed:"
event["onSelectionChanged"] = "object:selection-changed:"
event["onCaretMoved"] = "object:text-caret-moved"
event["onTextInserted"] = "object:text-changed:insert"
event["onTextDeleted"] = "object:text-changed:delete"
event["onLinkSelected"] = "object:link-selected"
event["onNameChanged"] = "object:property-change:accessible-name"
