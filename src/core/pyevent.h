/*
 * Orca
 *
 * Copyright 2004-2005 Sun Microsystems Inc.
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Library General Public
 * License as published by the Free Software Foundation; either
 * version 2 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Library General Public License for more details.
 *
 * You should have received a copy of the GNU Library General Public
 * License along with this library; if not, write to the
 * Free Software Foundation, Inc., 59 Temple Place - Suite 330,
 * Boston, MA 02111-1307, USA.
 *
 */

#include <glib.h>
#include "Accessibility.h"

/**
 * The data structure used to back the Python Event.  Keeps track of
 * the Accessibility_Event that was used to create this object.
 */
typedef struct {
	PyObject_HEAD
	Accessibility_Event *e;
} PyEvent;


/**
 * pyevent_init:
 * @mod: the module which to add this to
 *
 * Adds the "Event" class as an attribute of the given module.  For
 * example, if the core module calls this method, the Event class will
 * become available as "core.Event".
 *
 * Returns: void
 */
void pyevent_init (PyObject *mod);


/**
 * pyevent_new:
 * @e: the Accessibility_Event received from the at-spi
 *
 * Creates a new Event that delegates to the given Accessibility_Event
 * for information.
 *
 * Returns: a Python Event instance
 */
PyObject *pyevent_new (const Accessibility_Event *e);
