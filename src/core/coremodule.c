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

#include <libbonobo.h>
#include "eventlistener.h"
#include "pyevent.h"

static gboolean core_initialized = FALSE;

/* A Python object reference to the core module itself */

static PyObject *core_module = NULL;

/* A CORBA object reference to the at-spi registry */

static Accessibility_Registry registry = CORBA_OBJECT_NIL;

/* Hash table of the current registered event listeners */

static GHashTable *listeners = NULL;

/*
 * One global event queue-- the design is such that we could have
 * multiple queues in the future if the need arises
 *
 */

static EventQueue *queue = NULL;


/*
 *
 * The core module's event listeners are GObjects which can reference
 * both a list of C callback functions, as well as a list of Python  objects
 * (which are callback functions written in Python).  Only one EventListener object should be registered for any
 * given at-spi event type at any given time.
 *
 * The C functions are always called first in the order in which they
 * were registered, so that the core can do any
 * internal processing that must happen before events are dispatchd to
 * the Python scripts.  then the Python callbacks are called in the
 * order in which they were registered.
 *
 */


/*
 *
 * Register a C function to receive at-spi event notifications.
 * Python callbacks are registered via the Python interface to the
 * core module defined later.
 *
 * This function searches for an EventListener object with the specified
 * event type.  If one is found, then the specified C function is
 * chained to the end of its list of C functions.  If one is not
 * found, a new EventListener is created, and the specified C function
 * is added as its only C callback.
 *
 */

static void
register_event_listener (const char *type,
			 event_listener_func f)
{
	GQuark type_quark;
	CORBA_Environment ev;
	EventListener *el;
	
	/* Generate the key for the hash table lookup */

	type_quark = g_quark_from_string (type);
	
	/* Do we already have a listener for this event type */

	el = g_hash_table_lookup (listeners, (gpointer) type_quark);
	if (!el)
	{
	
		/* Create a new event listener */

		GSList *funcs = g_slist_prepend (NULL, f);
		el = event_listener_new (queue, funcs, NULL);
		g_hash_table_insert (listeners, (gpointer) type_quark, el);


		/* Register the EventListener object with at-spi */

		CORBA_exception_init (&ev);
		Accessibility_Registry_registerGlobalEventListener (registry,
								    bonobo_object_corba_objref (BONOBO_OBJECT(el)),
								    type,
								    &ev);

		/* If an exception was thrown, return an error */

		if (ev._major != CORBA_NO_EXCEPTION)
		{
			g_hash_table_remove (listeners, (gpointer) type_quark);
			PyErr_SetString (PyExc_RuntimeError, "Couldn't register event listener with at-spi");
			return;
		}
		CORBA_exception_free (&ev);
	}
	else
	{
		
		/* Add this C callback to the existing listener */
		
		el->funcs = g_slist_append (el->funcs, f);
	}
}


static PyObject *
core_module_init (PyObject *self)
{
	CORBA_Environment ev;
	Accessibility_Desktop d;
	char *obj_id;

	/* Don't double-initialize */

	if (core_initialized)
	{
		PyErr_SetString (PyExc_RuntimeError, "Core already initialized");
		return NULL;
	}

	/* Initialize the pyevent code */
	
	pyevent_init (core_module);

	/* Make an empty event listeners hash table */

	listeners = g_hash_table_new (NULL, NULL);

	/* Create the global event queue */

	queue = event_queue_new ();

        /* The OAFIID of the registry */

	obj_id = "OAFIID:Accessibility_Registry:1.0";
	
	/* Attempt to activate the registry */

	CORBA_exception_init (&ev);
	registry = bonobo_activation_activate_from_id (obj_id, 0, NULL, &ev);
	if (ev._major != CORBA_NO_EXCEPTION)
	{
		PyErr_SetString (PyExc_RuntimeError, "Could not activate accessibility registry");
		return NULL;
	}
	
	/* Add a reference to the registry to the module */

	PyModule_AddObject (core_module, "registry",
			    pycorba_object_new (registry));

        /* Get the desktop */

	d = Accessibility_Registry_getDesktop (registry,
					       0,
					       &ev);

	if (ev._major != CORBA_NO_EXCEPTION)
	{
		PyErr_SetString (PyExc_RuntimeError, "Could not access the desktop");
		return NULL;
	}
	
	PyModule_AddObject (core_module, "desktop", 
			    pycorba_object_new(d));

	core_initialized = TRUE;
	return PyInt_FromLong (1);
}


/*
 *
 * Throw a Python exception if the core module is not initialized
 *
 */

static gboolean
core_check_init ()
{
	if (!core_initialized)
	{
		PyErr_SetString (PyExc_RuntimeError, "Core not initialized");
		return FALSE;
	}
	return TRUE;
}


/*
 *
 * Free all the resources allocated by the core module
 *
 */

static PyObject *
core_module_shutdown (PyObject *self)
{
	if (!core_check_init ())
		return NULL;

	if (registry != CORBA_OBJECT_NIL)
	{
		bonobo_object_release_unref (registry, NULL);
		registry = CORBA_OBJECT_NIL;
	}
	g_hash_table_destroy (listeners);
	bonobo_main_quit ();
	core_initialized = FALSE;
	return PyInt_FromLong (1);
}


/*
 *
 * Return a pycorba_object reference to the at-spi registry
 *
 */

static PyObject *
core_module_getRegistry (PyObject *self)
{
	PyObject *obj;

	if (!core_check_init ())
		return NULL;
	obj = pycorba_object_new (registry);
	return obj;
}


/*
 *
 * Register a Python event listener callback function to respond to
 * at-spi events.  This function checks to see if an event listener
 * exists for the given event type.  If one exists, the Python
 * function is added to its list of Python callbacks.  If not, a new
 * listener is created with an empty list of C callbacks, and the
 * specified Python callback as the only callback in its list of
 * Python callbacks
 *
 */

static PyObject *
core_module_registerEventListener (PyObject *self,
				   PyObject *args)
{
 	GQuark type_quark;
	CORBA_Environment ev;
	PyObject *listener;
	char *event_name;
	EventListener *el;
	GSList *listener_list;

	if (!core_check_init ())
		return NULL;

	/* Get the arguments */

	if (!PyArg_ParseTuple (args, "Os:registerEventListener", &listener, &event_name))
		return NULL;
	Py_INCREF (listener);

	/* Do we already have a listener registered for this event type? */

        type_quark = g_quark_from_string (event_name);
	el = g_hash_table_lookup (listeners, (gpointer) type_quark);
	
	if (!el)
	{

		/* Create the bonobo event listener */

		listener_list = g_slist_prepend (NULL, listener);
		el = event_listener_new (queue, NULL, listener_list);

		/* Add it to our hash table */

		g_hash_table_insert (listeners, (gpointer) type_quark, el);

		/* Register it with at-spi */

		CORBA_exception_init (&ev);
		Accessibility_Registry_registerGlobalEventListener (registry,
								    bonobo_object_corba_objref (BONOBO_OBJECT(el)),
								    event_name,
								    &ev);

		/* If an exception was thrown, return an error */

		if (ev._major != CORBA_NO_EXCEPTION)
		{
			g_hash_table_remove (listeners, (gpointer) type_quark);
			PyErr_SetString (PyExc_RuntimeError, "Couldn't register event listener with at-spi");
			return NULL;
		}
		CORBA_exception_free (&ev);
	}
	else
	{
		el->pylisteners = g_slist_append (el->pylisteners, listener);
	}
	return PyInt_FromLong (1);
}


/*
 *
 * Unregister a Python event listener callback
 *
 */

static PyObject *
core_module_unregisterEventListener (PyObject *self,
				     PyObject *args)
{
	GQuark type_quark;
	CORBA_Environment ev;
	char *event_name;
	PyObject *listener;
	EventListener *el;

	/* Parse arguments */

	if (!PyArg_ParseTuple (args, "Os:unregisterEventListener", &listener, &event_name))
		return NULL;

	/* See if we have it in our list */

	type_quark = g_quark_from_string (event_name);
	el = g_hash_table_lookup (listeners, (gpointer) type_quark);
	if (!el)
		return PyInt_FromLong (1);

	el->pylisteners = g_slist_remove (el->pylisteners, listener);

        /* If the event listener has no callbacks, get rid of it */

	if (el->pylisteners == NULL && el->funcs == NULL)
	{

                /* Unregister it from at-spi */

		CORBA_exception_init (&ev);
		Accessibility_Registry_deregisterGlobalEventListener (registry,
								      bonobo_object_corba_objref (BONOBO_OBJECT(el)),
								      event_name,
								      &ev);

		/* If unregistration failed, throw an exception */

		if (ev._major != CORBA_NO_EXCEPTION)
		{
			PyErr_SetString (PyExc_RuntimeError, "Could not unregister event listener from at-spi");
			return NULL;
		}
	
		CORBA_exception_free (&ev);

		/* Destroy the listener and remove it from our list */

		g_hash_table_remove (listeners, (gpointer) type_quark);
	
		Py_DECREF (listener);
	}
	return PyInt_FromLong (1);
}


/*
 *
 * This table lists the methods exported by the core module
 *
 */

static PyMethodDef core_methods[] = {
	{"init", (PyCFunction) core_module_init, METH_NOARGS},
	{"shutdown", (PyCFunction) core_module_shutdown, METH_NOARGS},
	{"registerEventListener", (PyCFunction) core_module_registerEventListener, METH_VARARGS},
	{"unregisterEventListener", (PyCFunction) core_module_unregisterEventListener, METH_VARARGS},
	{NULL, NULL}
};

/*
 *
 * This function is called by python when the core module is imported
 *
 */

void
initcore (void)
{
	PyObject *dict;
	PyObject *load_typelib;
	PyObject *pyorbit_module;
	PyObject *corba_module;
	PyObject *orb_init;
	PyObject *bonobo_module;
	PyObject *a11y_module;
	PyObject *a11y_poa_module;
	char *a11y_module_name = "Accessibility";
	char *a11y_poa_module_name = "Accessibility__POA";

	core_module = Py_InitModule ("core", core_methods);

	/* Import the pyorbit module */

	pyorbit_module = PyImport_ImportModule ("ORBit");

	/* Initialize pyorbit */

	init_pyorbit ();

        if (!pyorbit_module)
	{
		PyErr_SetString (PyExc_RuntimeError, "Can not load ORBit2 support");
		return;
	}

	/* Allow access to the ORBit module through the core module */

	PyModule_AddObject (core_module, "ORBit", pyorbit_module);
	
        /* Import bonobo support */

	bonobo_module = PyImport_ImportModule ("bonobo");

        if (!bonobo_module)
	{
		PyErr_SetString (PyExc_RuntimeError, "Can not load Bonobo support");
		return;
	}

	/* Allow access to the bonobo module through the core module */

	PyModule_AddObject (core_module, "bonobo", bonobo_module);

        /* Get pyorbit's dictionary */

	dict = PyModule_GetDict (pyorbit_module);

	if (!dict)
	{
		PyErr_SetString (PyExc_RuntimeError, "Can not load ORBit2's module dictionary");
		return;
	}
	
	/* Find the load_typelib function */
	
	load_typelib = PyDict_GetItemString (dict, "load_typelib");

	if (!load_typelib)
	{
		PyErr_SetString (PyExc_RuntimeError, "Can not find the load_typelib function for ORBit2");
		return;
	}
	
	PyObject_CallFunction (load_typelib, "s", a11y_module_name);
	
	/* Find the CORBA submodule */
	
	corba_module = PyDict_GetItemString (dict, "CORBA");

	if (!corba_module)
	{
		PyErr_SetString (PyExc_RuntimeError, "Can not find the CORBA submodule of  ORBit2");
		return;
	}
	
	/* Find and call the ORB_init function of the CORBA submodule */

	dict = PyModule_GetDict (corba_module);

	orb_init = PyDict_GetItemString (dict, "ORB_init");
	if (!orb_init)
	{
		PyErr_SetString (PyExc_RuntimeError, "Can not find the CORBA.ORB_init functioninthe  ORBit2 module");
		return;
	}

	PyObject_CallFunction (orb_init, "");
	
	/* Import the at-spi bindings */

	a11y_module = PyImport_ImportModule (a11y_module_name);
        if (!a11y_module)
	{
		PyErr_SetString (PyExc_RuntimeError, "Can not load accessibility support");
		return;
	}
	a11y_poa_module = PyImport_ImportModule (a11y_poa_module_name);
        if (!a11y_poa_module)
	{
		PyErr_SetString (PyExc_RuntimeError, "Can not load accessibility support");
		return;
	}

	/*
	* 
	* Allow access to the Accessibility and Accessibility__POA
	* modules through the core module
	*
	*/
	
	PyModule_AddObject (core_module, a11y_module_name, a11y_module);
	PyModule_AddObject (core_module, a11y_poa_module_name, a11y_poa_module);
}
