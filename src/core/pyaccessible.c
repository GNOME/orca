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

#include <bonobo/bonobo-object.h>
#include <Python.h>
#include <pyorbit.h>
#include "pyaccessible.h"


/*
 *
 * We cache all the currently pyaccessible objects.  The keys to the
 * hash are Accessibility_Accessible CORBA objects.
 *
 */

static GHashTable *cache = NULL;

/*
 *
 * Uses CORBA_Object_hash to generate hash keys based on a
 * CORBA_Object reference
 *
 */

static guint
pyaccessible_hash (gconstpointer key)
{
	guint rv;
	CORBA_Object obj = (CORBA_Object) key;
	CORBA_Environment ev;

	CORBA_exception_init (&ev);
	rv = CORBA_Object_hash (obj, 0, &ev);
	CORBA_exception_free (&ev);
}


/*
 *
 * Uses CORBA_Object_is_equivalent to determine whether two
 * CORBA_Object references refer to the same object.  Used in the
 * pyaccessible hash functions.
 *
 */

static gboolean
corba_object_is_equal (gconstpointer a, gconstpointer b)
{
	gboolean rv;
	CORBA_Environment ev;
	CORBA_Object obj1 = (CORBA_Object) a;
	CORBA_Object obj2 = (CORBA_Object) b;
	CORBA_exception_init (&ev);
	rv = CORBA_Object_is_equivalent (obj1, obj2, &ev);
	CORBA_exception_free (&ev);
	return rv;
}


/*
 *
 * Unrefs a Python object.  Used in hash tables which are caching
 * PyObjects.
 *
 */

static void
pyobject_unref (gpointer data)
{
	PyObject *obj = (PyObject *) data;
	Py_DECREF (obj);
}


/*
 *
 * Returns the Python CORBA object contained in a pyaccessible.
 *
 */

static PyObject *
pyaccessible_get_objref (PyAccessible *self)
{
	return pycorba_object_new (self->acc);
}


/*
 *
 * Retrieve a string attribute from a pyaccessible.
 *
 */

static PyObject *
pyaccessible_get_string_attr (PyAccessible *self,
			      int attr)
{
	PyObject *rv;
	CORBA_Environment ev;
	CORBA_char *value;

	CORBA_exception_init (&ev);
	switch (attr)
	{
	case ATTR_NAME:
		value = Accessibility_Accessible__get_name (self->acc,
							    &ev);
		break;
	case ATTR_DESCRIPTION:
		value = Accessibility_Accessible__get_description (self->acc,
							    &ev);
		break;
	case ATTR_ROLE_NAME:
		value = Accessibility_Accessible_getRoleName (self->acc,
							    &ev);
		break;
	case ATTR_LOCALIZED_ROLE_NAME:
		value = Accessibility_Accessible_getLocalizedRoleName (self->acc,
								       &ev);
		break;
	}
	if (ev._major != CORBA_NO_EXCEPTION)
	{
		return NULL;
	}
	CORBA_exception_free (&ev);
	rv = PyString_FromString (value);
	CORBA_free (value);
	Py_INCREF (rv);
	g_hash_table_insert (self->attrs, (gpointer)attr, rv);
	return rv;
}


/*
 *
 * Get an integer attribute from a pyaccessible
 *
 */

static PyObject *
pyaccessible_get_int_attr (PyAccessible *self,
int attr)
{
	CORBA_long i;
	PyObject *rv;
	CORBA_Environment ev;

	CORBA_exception_init (&ev);
	switch (attr)
	{
	case ATTR_CHILD_COUNT:
		i = Accessibility_Accessible__get_childCount (self->acc,
							      &ev);
		break;
	case ATTR_INDEX_IN_PARENT:
		i = Accessibility_Accessible_getIndexInParent (self->acc,
								 &ev);
		break;
	}
	if (ev._major != CORBA_NO_EXCEPTION)
		return NULL;
	CORBA_exception_free (&ev);
	rv = PyInt_FromLong (i);
	Py_INCREF (rv);
	g_hash_table_insert (self->attrs, (gpointer)attr, rv);
	return rv;
}


/*
 *
 * Retrieve an attribute from a pyaccessible
 *
 */

static PyObject *
pyaccessible_get_attr (PyAccessible *self,
		       int attr)
{
	PyObject *rv;

	/* Have we cached the value of this attribute */

	rv = g_hash_table_lookup (self->attrs, (gpointer)attr);
	if (!rv)
	{

		/* Retrieve the current value of the attribute from
		 * the CORBA Accessibility_Accessible object
		 *
		 */

		switch (attr)
		{
		case ATTR_NAME:
		case ATTR_DESCRIPTION:
		case ATTR_ROLE_NAME:
		case ATTR_LOCALIZED_ROLE_NAME:
			rv = pyaccessible_get_string_attr (self, attr);
			break;
		case ATTR_CHILD_COUNT:
		case ATTR_INDEX_IN_PARENT:
			rv = pyaccessible_get_int_attr (self, attr);
		}
	}
	else

		/* Simply increment the refcount of the cached value
		 * we already have
		 *
		 */

		Py_INCREF (rv);
	return rv;
}


/*
 *
 * Get a pyaccessible's name
 *
 * A pyaccessible's cached name is invalidated by
 * "object:property-change:accesible-name" events
 *
  */

static PyObject *
pyaccessible_get_name (PyAccessible *self)
{
	return pyaccessible_get_attr (self, ATTR_NAME);
}


/*
 *
 * Get a pyacessible's description
 *
 * A pyaccessible's cached description is invalidated by
 * "object:property-change:accesible-description" events
 *
 */

static PyObject *
pyaccessible_get_description (PyAccessible *self)
{
	return pyaccessible_get_attr (self, ATTR_DESCRIPTION);
}


/*
 *
 * Get the non-localized name of the role of this pyaccessible
 * The cached role name is never invalidated.
 *
 */

static PyObject *
pyaccessible_get_role_name (PyAccessible *self)
{
	return pyaccessible_get_attr (self, ATTR_ROLE_NAME);
}


/*
 *
 * Get the localized name of the role of this pyaccessible
 *
 * 
 * The cached localized role name is never invalidated
 *
 */

static PyObject *
pyaccessible_get_localized_role_name (PyAccessible *self)
{
	return pyaccessible_get_attr (self, ATTR_LOCALIZED_ROLE_NAME);
}


/*
 *
 * Get the parent object of this pyaccessible
 *
 * the cached parent is invalidated by
 * "object:property-change:accessible-parent" events
 *
 * We currently do not cache parent -> children traversal information,
 * but if we ever start, that support will need to be added as a part
 * of this function
 *
 */

static PyObject *
pyaccessible_get_parent (PyAccessible *self)
{
	Accessibility_Accessible parent;
	PyObject *rv;
	CORBA_Environment ev;

	/*
	 *
	 * Do we already have a cached reference to this
	 * pyaccessible's parent
	 *
	 */

	rv = g_hash_table_lookup (self->attrs, (gpointer) ATTR_PARENT);
	if (!rv)
	{
		/*
		 *
		 * Get the CORBA_Object Accessibility_Accessible object
		 * reference of the parent
		*
		*/

		CORBA_exception_init (&ev);
		parent = Accessibility_Accessible__get_parent (self->acc,
							       &ev);
		if (ev._major != CORBA_NO_EXCEPTION)
		{
			
			/*
			 *
			 * An exception occurred-- return NULL which
			 * will throw a Python exception
			 *
			 */

			return NULL;
		}
		CORBA_exception_free (&ev);

		/*
		 *
		 * Creat4 a pyaccessible from the CORBA_Object
		 * reference
		 *
		 */

		rv = pyaccessible_new (parent);
		
		/*
		 *
		 * The pyaccessible_new call refs the CORBA_Object, so
		 * Unref our object reference
		 *
		 */

		bonobo_object_release_unref (parent, NULL);
		
		/*
		 *
		 * Cache the pyaccessible parent object as the
		 * ATTR_PARENT attribute of this pyaccessible
		 *
		 */

		Py_INCREF (rv);
		g_hash_table_insert (self->attrs, (gpointer) ATTR_PARENT, rv);
	}
	else

		/* Just ref the cached reference to the parent */

		Py_INCREF (rv);
	return rv;
}


/*
 *
 * Get the number of children in this pyaccessible
 *
 * The cached number of children is invalidated by
 * "object:children-changed" events
 *
 */

static PyObject *
pyaccessible_get_childCount (PyAccessible *self)
{
	return pyaccessible_get_attr (self, ATTR_CHILD_COUNT);
}


/*
 *
 * Get the index of this pyaccessible in it's parent
 *
 * XXX - This cached information is not invalidated as it should be
 *
 */

static PyObject *
pyaccessible_get_indexInParent (PyAccessible *self)
{
	return pyaccessible_get_attr (self, ATTR_INDEX_IN_PARENT);
}


/*
 *
 * Get the specified child of this pyaccessible
 *
 * No caching of this information is performed
 *
 */

static PyObject *
pyaccessible_getChildAtIndex (PyAccessible *self,
			      PyObject *args)
{
	CORBA_Environment ev;
	PyObject *rv;
	Accessibility_Accessible child;
	int index;

	if (!PyArg_ParseTuple (args, "i:getChildAtIndex", &index))

		/* The caller passed us the wrong thing.  Bail. */

		return NULL;
	
	/*
	*
	* Get the CORBA_Object Accessibility_Accessibility reference
	* to the specified child
	*
	 */

	CORBA_exception_init (&ev);
	child = Accessibility_Accessible_getChildAtIndex (self->acc,
							index,
							&ev);

	if (child != CORBA_OBJECT_NIL && ev._major == CORBA_NO_EXCEPTION)
	{
		PyAccessible *pyacc;

		/* 
		 *
		 * Create the pyaccessible from the CORBA object
		 * reference
		 *
		 */

		rv = pyaccessible_new (child);
		
		/* We're done with the CORBA object reference */
		
		bonobo_object_release_unref (child, &ev);
		pyacc = (PyAccessible *) rv; 

		/*
		 *
		 * Since we already have the infomation, cache the
		 * reference to this child's parent pyaccessible
		 *
		 */

		if (g_hash_table_lookup (pyacc->attrs, (gpointer) ATTR_PARENT) == NULL)
		{
			Py_INCREF (self);
			g_hash_table_insert (pyacc->attrs, (gpointer) ATTR_PARENT, self);
		}

		/*
		 *
		 * We also know this child's current index within its
		 * parent
		 *
		 */

		if (g_hash_table_lookup (pyacc->attrs, (gpointer) ATTR_INDEX_IN_PARENT) == NULL)
		{
			g_hash_table_insert (pyacc->attrs, (gpointer) ATTR_INDEX_IN_PARENT, PyInt_FromLong(index));
		}
	}
	else
	{

		/* This object has no parent, return nothing */

		rv = Py_None;
		Py_INCREF (Py_None);
	}
	CORBA_exception_free (&ev);
	return (PyObject *) rv;
}


/*
 *
 * Get the state set of this pyaccessible
 *
 * The cached state set is invalidated by "object:state-changed"
 * events
 *
 */

static PyObject *
pyaccessible_get_state (PyAccessible *self)
{
	Accessibility_StateSet set;
	PyObject *rv;
	CORBA_any any;
	CORBA_Environment ev;

	/* See if we already have ths state set in our cache */

	rv = g_hash_table_lookup (self->attrs, (gpointer) ATTR_STATE);
	if (!rv)
	{
		CORBA_exception_init (&ev);
		set = Accessibility_Accessible_getState (self->acc,
							   &ev);
		if (ev._major != CORBA_NO_EXCEPTION)

			/*
			 *
			 * Something went wrong-- return NULL so Pythn
			throws an exception
			*
			*/

			return NULL;
		CORBA_exception_free (&ev);

		/*
		 *
		 * Create a pycorba_object from our CORBA_Object
		 * reference, and cache it
		 *
		 */

		rv = pycorba_object_new (set);
		Py_INCREF (rv);
		g_hash_table_insert (self->attrs, (gpointer) ATTR_STATE, rv);
	}
	else

		/* Just ref our cached pycorba_object */

		Py_INCREF (rv);
	return rv;
}


/*
 *
 * Get the relation set of this pyaccessible
 *
 * Relation sets are not currently cached
 *
  */

static PyObject *
pyaccessible_get_relation_set (PyAccessible *self)
{
	Accessibility_RelationSet *set;
	PyObject *o, *list;
	CORBA_Environment ev;
	int i;
	
	list = PyList_New (0);
	CORBA_exception_init (&ev);
	set = Accessibility_Accessible_getRelationSet (self->acc,
						       &ev);

	if (ev._major != CORBA_NO_EXCEPTION)

		/*
		 *
		 * We got a CORBA exception, Return NULL so Python
		 * throws an exception
		 *
		 */
		 
		return NULL;
	CORBA_exception_free (&ev);

	/* Create the list of relations */

	for (i = 0; i < set->_length; i++)
	{
		
		/*
		 *
		 * Create a pycorba_object for each relation in the
		 * sequence we received
		 *
		 */

		o = pycorba_object_new (set->_buffer[i]);
		PyList_Append (list, o);
	}
	CORBA_free (set);
	return list;
}


/*
 *
 * The destructor for pyaccessible objects
 *
 */

static void
pyaccessible_dealloc (PyAccessible *acc)
{
	
	/* Unref the bonobo object */

	bonobo_object_release_unref (acc->acc, NULL);

	/* Destroy the attribute hash table */

	g_hash_table_destroy (acc->attrs);
}


/*
 *
 * This table defines the methods of a pyaccessible object
 *
 */

static PyMethodDef pyaccessible_methods[] = {
    { "getChildAtIndex", (PyCFunction)pyaccessible_getChildAtIndex, METH_VARARGS,
      "" },
    { "getState", (PyCFunction)pyaccessible_get_state, METH_NOARGS,
      "" },
    { "getRelationSet", (PyCFunction)pyaccessible_get_relation_set, METH_NOARGS,
      "" },
    { "getRoleName", (PyCFunction)pyaccessible_get_role_name, METH_NOARGS,
      "" },
    { "getLocalizedRoleName", (PyCFunction)pyaccessible_get_localized_role_name, METH_NOARGS,
      "" },
    { "getIndexInParent", (PyCFunction)pyaccessible_get_indexInParent, METH_NOARGS,
      "" },
    { NULL, NULL, 0 }
};

/*
 *
 * This table defines the attributes exposed by pyaccessible objects
 *
 */

static PyGetSetDef pyaccessible_getsets[] = {
	{"objref", (getter)pyaccessible_get_objref, (setter)0 },
	{"name", (getter)pyaccessible_get_name, (setter)0 },
	{"description", (getter)pyaccessible_get_description, (setter)0 },
	{"parent", (getter)pyaccessible_get_parent, (setter)0 },
	{"childCount", (getter)pyaccessible_get_childCount, (setter)0 },
	{NULL, (getter)0, (setter)0 }
};

/*
 *
 * This is the standard Python glue defining the inner-workings of the
 * pyaccessible object
 *
 */

PyTypeObject PyAccessible_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                  /* ob_size */
    "core.Accessible",                     /* tp_name */
    sizeof(PyAccessible),             /* tp_basicsize */
    0,                                  /* tp_itemsize */
    /* methods */
    (destructor)pyaccessible_dealloc, /* tp_dealloc */
    (printfunc)0,                       /* tp_print */
    (getattrfunc)0,                     /* tp_getattr */
    (setattrfunc)0,                     /* tp_setattr */
    (cmpfunc)0,        /* tp_compare */
    (reprfunc)0,      /* tp_repr */
    0,                                  /* tp_as_number */
    0,                                  /* tp_as_sequence */
    0,                                  /* tp_as_mapping */
    (hashfunc)0,   /* tp_hash */
    (ternaryfunc)0,                     /* tp_call */
    (reprfunc)0,                        /* tp_str */
    (getattrofunc)0,                    /* tp_getattro */
    (setattrofunc)0,                    /* tp_setattro */
    0,                                  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,   /* tp_flags */
    NULL, /* Documentation string */
    (traverseproc)0,                    /* tp_traverse */
    (inquiry)0,                         /* tp_clear */
    (richcmpfunc)0,                     /* tp_richcompare */
    0,                                  /* tp_weaklistoffset */
    (getiterfunc)0,                     /* tp_iter */
    (iternextfunc)0,                    /* tp_iternext */
    pyaccessible_methods,             /* tp_methods */
    0,                                  /* tp_members */
    pyaccessible_getsets,                                  /* tp_getset */
    (PyTypeObject *)0,                  /* tp_base */
    (PyObject *)0,                      /* tp_dict */
    0,                                  /* tp_descr_get */
    0,                                  /* tp_descr_set */
    0,                                  /* tp_dictoffset */
    (initproc)0,      /* tp_init */
    PyType_GenericAlloc,                                  /* tp_alloc */
    PyType_GenericNew,                                  /* tp_new */
    0,                                  /* tp_free */
    (inquiry)0,                         /* tp_is_gc */
    (PyObject *)0,                      /* tp_bases */
};


/*
 *
 * These functions are defined in pyaccessible.h as well so they can
 * be used by other files in the core module, namely coremodule.c
 *
 */


/*
 *
 * Initialize stuff having to do with pyaccessible objects
 *
 * This is called by coremodule.c as a part of the core module
 * initialization
 *
 */

void
pyaccessible_init (PyObject *mod)
{
	/* Register the pyaccesible object type with Python */

	if (PyType_Ready(&PyAccessible_Type) < 0)
		return;
	
	/* Add the pyaccessible object type to the core module */

	PyModule_AddObject (mod, "Accessible",
			    (PyObject *)&PyAccessible_Type);

	/* Create the pyaccessible object cache */

	cache = g_hash_table_new_full (pyaccessible_hash,
				       corba_object_is_equal,
				       NULL,
				       pyobject_unref);
}


/*
 *
 * Create a pyaccessible object from a CORBA object reference
 *
 * If a pyaccessible object already exists for the given CORBA object,
 * a reference to that object is returned
 *
 */

PyObject *
pyaccessible_new (Accessibility_Accessible acc)
{
	PyAccessible *pyacc;
	PyObject *args;

	/* Do we already have a reference to it */

	pyacc = g_hash_table_lookup (cache, acc);
	if (!pyacc)
	{
		
		/* Create a new pyaccessible */

		args = PyTuple_New (0);
		pyacc = (PyAccessible *) PyAccessible_Type.tp_new (&PyAccessible_Type, args, NULL);
		Py_DECREF (args);
		if (!pyacc)
			return NULL;
		pyacc->acc = bonobo_object_dup_ref (acc, NULL);
		pyacc->attrs = g_hash_table_new_full (NULL,
						      NULL,
						      NULL,
						      pyobject_unref);
		Py_INCREF (pyacc);
		g_hash_table_insert (cache, acc, pyacc);
	}
	else

		/* Just ref the one we have */

		Py_INCREF (pyacc);
	return (PyObject *) pyacc;
}


/*
 *
 * Returns the pyaccessible object for a given CORBA object
 * reference.  If one does not exist, it returns NULL.
 *
 */

PyAccessible *
pyaccessible_find (Accessibility_Accessible acc)
{
	PyAccessible *rv;
	rv = g_hash_table_lookup (cache, acc);
	if (rv)
		Py_INCREF (rv);
	return rv;
}


/*
 *
 * Invalidatethe specified pyaccessible attribute.  This is called
 * from coremodule.c in the core module's internal event listeners
 *
 */

void
pyaccessible_invalidate_attribute (PyAccessible *acc,
				   int attr)
{
	if (g_hash_table_lookup (acc->attrs, (gpointer) attr))
		g_hash_table_remove (acc->attrs, (gpointer) attr);
}


/*
 *
 * Remove a pyaccessible from the cache.  This does not necessarily
 * mean it is destroyed, only that future lookups won't find it (other
 * Python or C code may still be hanging on to a reference to it).
 *
 * Note that this does not clean up references to this object that may
 * be in other objects' attribute caches such as references to an
 * object's parent.  We're relying on the completeness of the at-spi
 * event model to send an event which causes any other references to
 * the object to be removed when the corresponding attributes are
 * invalidated ("object:property-change:accessible-parent" for example
 *
 */

void
pyaccessible_remove (PyAccessible *pyacc)
{
	g_hash_table_remove (cache, pyacc->acc);
}
