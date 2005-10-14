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

#include <libbonobo.h>
#include "eventlistener.h"
#include "pyevent.h"

#include <X11/Xlib.h>
#include <gdk/gdkx.h>


/**
 * If TRUE, then this module has been intialized (see initcore).
 */
static gboolean core_initialized = FALSE;


/**
 * Python object reference to the core module itself.
 */
static PyObject *core_module;


/**
 * CORBA object reference to the at-spi registry 
 */
static Accessibility_Registry registry = CORBA_OBJECT_NIL;


/**
 * Hash table of the current registered event listeners.  The keys
 * represent the name of the events (a quark'd string), and the values
 * represent pointers to EventListeners (see eventlistener.h).  The
 * hash table is used to allow a maximum of one listener to be added
 * directly to the Accessiblity Registry for any given event type.
 *
 * The core_module_registerEventListener and
 * core_module_unregisterEventListener methods are exposed to Python
 * as registerEventListener and unregisterEventListener.  These methods
 * manage the EventListeners in this hash table, and keep any Python
 * listeners sorted in the order they were registered.
 */
static GHashTable *listeners = NULL;


/**
 * Global event queue -- entries are added to this queue via 
 * eventlistener.c:event_listener_notify_event, and are dispatched
 * via the event_queue.c:event_queue_idle_handler, which ultimately calls
 * event_listener.c:event_listener_dispatch.
 *
 * The design is such that we could have multiple queues in the future
 * if the need arises
 */
static EventQueue *queue = NULL;


/**
 * core_module_init:
 * @self: the core module as seen by Python
 * 
 * The Python init() method for the core Python module.  Initializes
 * contact with the at-spi Accessibility_Registry and also adds the
 * "registry" and "desktop" attributes to the core module so that they
 * can be accessed from Python.
 *
 * Returns: 1 on success, NULL (plus a raised exception) on failure
 */
static PyObject *core_module_init (PyObject *self) {
	CORBA_Environment ev;
	Accessibility_Desktop d;
	char *obj_id;

	/* Don't double-initialize 
	 */
	if (core_initialized) {
		PyErr_SetString (PyExc_RuntimeError, 
				 "Core already initialized");
		return NULL;
	}

	/* Initialize the pyevent code, adding the Python "Event" class.
	 */
	pyevent_init (core_module);

	/* Make an empty event listeners hash table 
	 */
	listeners = g_hash_table_new (NULL, NULL);

	/* Create the global event queue 
	 */
	queue = event_queue_new ();

	/* Attempt to activate the registry and add it as the "registry"
	 * attribute to the core module.
	 */
	CORBA_exception_init (&ev);
	obj_id = "OAFIID:Accessibility_Registry:1.0";
	registry = bonobo_activation_activate_from_id (obj_id, 0, NULL, &ev);

	if (ev._major != CORBA_NO_EXCEPTION) {
		CORBA_exception_free (&ev);
		PyErr_SetString (PyExc_RuntimeError, 
				 "Could not activate accessibility registry");
		return NULL;
	}
	
	PyModule_AddObject (core_module, 
			    "registry",
			    pycorba_object_new (registry));

        /* Get the desktop and add it as the "desktop attribute to the core 
	 * module.  [[[TODO:  WDW - I think there may be the notion of more
	 * than one desktop.]]]
	 */
	d = Accessibility_Registry_getDesktop (registry,
					       0,
					       &ev);

	if (ev._major != CORBA_NO_EXCEPTION) {
		CORBA_exception_free (&ev);
		PyErr_SetString (PyExc_RuntimeError, 
				 "Could not access the desktop");
		return NULL;
	}
	
	PyModule_AddObject (core_module, 
			    "desktop", 
			    pycorba_object_new(d));

	CORBA_exception_free (&ev);
	core_initialized = TRUE;
	return PyInt_FromLong (1);
}


/**
 * core_check_init:
 *
 * Throw a Python exception if the core module is not initialized
 *
 * Returns: TRUE if the module is initialized or FALSE (plus a raised
 * exception) if not.
 */
static gboolean core_check_init () {
	if (!core_initialized) {
		PyErr_SetString (PyExc_RuntimeError, "Core not initialized");
		return FALSE;
	}
	return TRUE;
}


/**
 * core_module_shutdown:
 * @self: the core module as seen by Python
 *
 * Free all the resources allocated by the core module, quits from
 * the Bonobo main loop, and resets the initialized state to FALSE.
 *
 * Returns: 1 on success or NULL (plus a raised exception) on failure,
 * which occurs if the core module has not been initialized.
 */
static PyObject *core_module_shutdown (PyObject *self)
{
	if (!core_check_init ()) {
		return NULL;
	}

	if (registry != CORBA_OBJECT_NIL) {
		bonobo_object_release_unref (registry, NULL);
		registry = CORBA_OBJECT_NIL;
	}
	g_hash_table_destroy (listeners);
	core_initialized = FALSE;
	return PyInt_FromLong (1);
}


/**
 * core_module_registerEventListener:
 * @self: the core module as seen by Python
 * @args: the arguments, which should be a Python function pointer and
 * a string that specifies an at-spi event name
 *
 * Register a Python event listener callback function to respond to
 * at-spi events.  This function checks to see if an event listener
 * exists for the given event type.  If one exists, the Python
 * function is added to its list of Python callbacks.  If not, a new
 * listener is created with an empty list of C callbacks, and the
 * specified Python callback as the only callback in its list of
 * Python callbacks
 *
 * Returns: 1 on success and NULL (and a raised exception) on failure
 */
static PyObject *core_module_registerEventListener (PyObject *self,
						    PyObject *args) {
 	GQuark type_quark;
	CORBA_Environment ev;
	PyObject *listener;
	char *event_name;
	EventListener *el;
	GSList *listener_list;

	if (!core_check_init ()) {
		return NULL;
	}

	/* Get the arguments.
	 */
	if (!PyArg_ParseTuple (args, 
			       "Os:registerEventListener", 
			       &listener, 
			       &event_name)) {
		return NULL;
	}
	Py_INCREF (listener); /* [[[TODO: WDW - check to make sure we
				 DECREF in the right places.]]] */

	/* Do we already have a listener registered for this event type? 
	 */
        type_quark = g_quark_from_string (event_name);
	el = g_hash_table_lookup (listeners, (gpointer) type_quark);
	if (!el) {
		/* Create the bonobo event listener and register it with
		 * at-spi.
		 */
		listener_list = g_slist_prepend (NULL, listener);
		el = event_listener_new (queue, NULL, listener_list);
		CORBA_exception_init (&ev);
		Accessibility_Registry_registerGlobalEventListener (
			registry,
			bonobo_object_corba_objref (BONOBO_OBJECT(el)),
			event_name,
			&ev);

		/* If an exception was thrown, return an error 
		 */
		if (ev._major != CORBA_NO_EXCEPTION) {
			/* [[[TODO: WDW - finalize/free el (which also
			 * frees up listener_list and DECREF
			 * listener?)
			 */
			CORBA_exception_free (&ev);
			PyErr_SetString (
				PyExc_RuntimeError, 
				"Couldn't register event listener with at-spi");
			return NULL;
		} else {
			CORBA_exception_free (&ev);
			g_hash_table_insert (listeners, 
					     (gpointer) type_quark, 
					     el);
		}
	} else {
		el->pylisteners = g_slist_append (el->pylisteners, listener);
	}
	return PyInt_FromLong (1);
}


/**
 * core_module_isEventListenerRegistered:
 * @self: the core module as seen by Python
 * @args: the argument, which should be a string that specifies an at-spi 
 * event name
 *
 * Checks to see if a given listener for the given event has already
 * been registered.
 *
 * Returns: True if the event listener has been registered, False if it
 * has not and NULL (and a raised exception) on failure
 */
static PyObject *core_module_isEventListenerRegistered (PyObject *self,
							PyObject *args) {
 	GQuark type_quark;
	char *event_name;
	EventListener *el;

	if (!core_check_init ()) {
		return NULL;
	}

	/* Get the arguments.
	 */
	if (!PyArg_ParseTuple (args, 
			       "s:isEventListenerRegistered", 
			       &event_name)) {
		return NULL;
	}

	/* Do we already have a listener registered for this event type? 
	 */
        type_quark = g_quark_from_string (event_name);
	el = g_hash_table_lookup (listeners, (gpointer) type_quark);
	if (!el) {
		return PyBool_FromLong (0);
	} else {
		return PyBool_FromLong (1);
	}
}


/**
 * core_module_unregisterEventListener:
 * @self: the core module as seen by Python
 * @args: the arguments, which should be a Python function pointer and
 * a string that specifies an at-spi event name
 *
 * Unregisters a Python event listener callback
 *
 * Returns: 1 on sucess and NULL (and a raised exception) on failure
 */
static PyObject *core_module_unregisterEventListener (PyObject *self,
						      PyObject *args) {
	GQuark type_quark;
	CORBA_Environment ev;
	char *event_name;
	PyObject *listener;
	EventListener *el;

	/* Parse arguments 
	 */
	if (!PyArg_ParseTuple (args, 
			       "Os:unregisterEventListener", 
			       &listener, 
			       &event_name)) {
		return NULL;
	}

	/* See if we have it in our list and remove it.  If we don't
	 * have it (e.g., lookup on the event name returns nothing or
	 * the listener was never registered), this is considered a
	 * no-op.
	 */
	type_quark = g_quark_from_string (event_name);
	el = g_hash_table_lookup (listeners, (gpointer) type_quark);
	if (!el) {
		return PyInt_FromLong (1);
	}

	el->pylisteners = g_slist_remove (el->pylisteners, listener);
	
        /* If the event listener has no more callbacks, unregister
	 * from the at-spi.
	 */
	if (el->pylisteners == NULL) {
		CORBA_exception_init (&ev);
		Accessibility_Registry_deregisterGlobalEventListener (
			registry,
			bonobo_object_corba_objref (BONOBO_OBJECT(el)),
			event_name,
			&ev);

		/* If unregistration failed, throw an exception 
		 */
		if (ev._major != CORBA_NO_EXCEPTION) {
			CORBA_exception_free (&ev);
			PyErr_SetString (PyExc_RuntimeError, 
					 "Could not unregister event listener from at-spi");
			return NULL;
		}
	
		CORBA_exception_free (&ev);

		/* Destroy the listener and remove it from our list 
		 */
		g_hash_table_remove (listeners, (gpointer) type_quark);
		Py_DECREF (listener);
	}

	return PyInt_FromLong (1);
}


/**
 * core_module_xKeysymToKeycode
 * @self: the core module as seen by Python
 * @args: the arguments, which should be a string version of an XKeysym.
 *
 * Returns: an integer representing the keycode for the keysym.
 */
static PyObject *core_module_xKeysymStringToKeycode (PyObject *self,
					       PyObject *args) {
        Display *display = GDK_DISPLAY();
	char *keysym;
	unsigned int keycode;

	/* Parse arguments 
	 */
	if (!PyArg_ParseTuple (args, 
			       "s:keysym", 
			       &keysym)) {
	        return NULL;
	}

	keycode = XKeysymToKeycode(display, XStringToKeysym(keysym));

	/* [[[TODO: WDW - I'm not quite sure if long is the right thing
	 * here.]]]
	 */
	return PyInt_FromLong (keycode);
}


/**
 * Methods exported by the core module to Python - maps Python method
 * names to the method names in this file.
 */
static PyMethodDef core_methods[] = {
	{"init", 
	 (PyCFunction) core_module_init, 
	 METH_NOARGS},
	{"shutdown", 
	 (PyCFunction) core_module_shutdown, 
	 METH_NOARGS},
	{"registerEventListener", 
	 (PyCFunction) core_module_registerEventListener, 
	 METH_VARARGS},
	{"isEventListenerRegistered", 
	 (PyCFunction) core_module_isEventListenerRegistered, 
	 METH_VARARGS},
	{"unregisterEventListener", 
	 (PyCFunction) core_module_unregisterEventListener, 
	 METH_VARARGS},
	{"XKeysymStringToKeycode", 
	 (PyCFunction) core_module_xKeysymStringToKeycode, 
	 METH_VARARGS},
	{NULL, NULL}
};

/**
 * initcore:
 * 
 * Called by python when the core module is imported.  Sets up the
 * core_methods that can be called from Python.  Imports the ORBit
 * module and exposes it as "core.ORBit." Imports the Bonobo module
 * and exposes it as "core.bonobo."  Initializes AT-SPI accessibility
 * support and exposes it as "core.Accessibility" and
 * "core.Accessibility__POA".
 *
 * Returns: void, but also raises an exception on failure
 */
void initcore (void) {
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

        Display *display = GDK_DISPLAY();
	int major_opcode_return;
	int first_event_return;
	int first_error_return;

	core_module = Py_InitModule ("core", core_methods);

	/* Import the pyorbit module, initialize it, and allow access
	 * to it as "core.ORBit."  [[[TODO: WDW - the call to
	 * init_pyorbit also does a PyImport_ImportModul ("ORBit").
	 * Not sure what the impact of this is.]]]
	 */
	pyorbit_module = PyImport_ImportModule ("ORBit");
	init_pyorbit ();
        if (!pyorbit_module) {
		PyErr_SetString (PyExc_ImportError, 
				 "Can not load ORBit2 support");
		return;
	}
	PyModule_AddObject (core_module, "ORBit", pyorbit_module);
	

        /* Import bonobo support and allow access to it as "core.bonobo"
	 */
	bonobo_module = PyImport_ImportModule ("bonobo");
        if (!bonobo_module) {
		PyErr_SetString (PyExc_ImportError, 
				 "Can not load Bonobo support");
		return;
	}
	PyModule_AddObject (core_module, "bonobo", bonobo_module);


	/* We need to initialize a bunch of ORBit stuff so we can get
	 * to the Accessibility and Accessibility__POA module
	 */
	dict = PyModule_GetDict (pyorbit_module);
	if (!dict) {
		PyErr_SetString (PyExc_AttributeError, 
				 "Can not load ORBit2's module dictionary");
		return;
	}
	
	load_typelib = PyDict_GetItemString (dict, "load_typelib");
	if (!load_typelib) {
		PyErr_SetString (PyExc_KeyError, 
				 "Can not find the load_typelib function for ORBit2");
		return;
	}
	
	PyObject_CallFunction (load_typelib, "s", a11y_module_name);
	
	corba_module = PyDict_GetItemString (dict, "CORBA");
	if (!corba_module) {
		PyErr_SetString (PyExc_KeyError, 
				 "Can not find the CORBA submodule of  ORBit2");
		return;
	}
	
	dict = PyModule_GetDict (corba_module);
	orb_init = PyDict_GetItemString (dict, "ORB_init");
	if (!orb_init) {
		PyErr_SetString (PyExc_KeyError, 
				 "Can not find the CORBA.ORB_init functioninthe  ORBit2 module");
		return;
	}

	PyObject_CallFunction (orb_init, "");
	
	/* Allow access to the Accessibility and Accessibility__POA
	 * modules through the core module as "core.Accessibility"
	 * and "core.Accessibility__POA."
	 */
	a11y_module = PyImport_ImportModule (a11y_module_name);
        if (!a11y_module) {
		PyErr_SetString (PyExc_ImportError, 
				 "Can not load accessibility support");
		return;
	}

	a11y_poa_module = PyImport_ImportModule (a11y_poa_module_name);
        if (!a11y_poa_module)
	{
		PyErr_SetString (PyExc_ImportError, 
				 "Can not load accessibility support");
		return;
	}

	PyModule_AddObject (core_module, 
			    a11y_module_name, 
			    a11y_module);

	PyModule_AddObject (core_module, 
			    a11y_poa_module_name, 
			    a11y_poa_module);

	/* XEvIE is a nice extension that helps us get around a lot
	 * of keyboard issues.  Let's see if it's present and let
	 * Python modules know this via "core.xeviePresent" being a
	 * non-zero value if it is present.
	 */
	PyModule_AddIntConstant (core_module, 
				 "xeviePresent", 
				 XQueryExtension (display,
						  "XEVIE",
						  &major_opcode_return,
						  &first_event_return,
						  &first_error_return));
}
