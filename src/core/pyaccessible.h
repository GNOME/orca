/*
 * Orca
 *
 * Copyright 2004 Sun Microsystems Inc.
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


typedef struct {
	PyObject_HEAD
	Accessibility_Accessible acc;
	GHashTable *attrs;
} PyAccessible;


enum {
	ATTR_NAME,
	ATTR_DESCRIPTION,
	ATTR_PARENT,
	ATTR_CHILD_COUNT,
	ATTR_INDEX_IN_PARENT,
	ATTR_ROLE,
	ATTR_ROLE_NAME,
	ATTR_LOCALIZED_ROLE_NAME,
	ATTR_STATE,
	ATTR_RELATION_SET
};


void
pyaccessible_init (PyObject *mod);
PyObject *
pyaccessible_new (Accessibility_Accessible acc);
PyAccessible *
pyaccessible_find (Accessibility_Accessible acc);
void
pyaccessible_invalidate_attribute (PyAccessible *acc,
				   int attr);
void
pyaccessible_remove (PyAccessible *pyacc);

