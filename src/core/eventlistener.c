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

#include "eventlistener.h"
#include "pyaccessible.h"
#include "pyevent.h"



static GObjectClass *parent_class;


/*
 *
 * This function is called by the ORB hen the registry sends an event
 * for which this listener is registered
 *
 */

static void 
event_listener_notify_event (PortableServer_Servant servant,
			const Accessibility_Event *e,
			     CORBA_Environment *ev)
{
	EventListener *el = EVENT_LISTENER(bonobo_object_from_servant(servant));


        /* Post the event to the event queue */

	event_queue_add (el->queue, e, el);
}


EventListener *
event_listener_new (EventQueue *queue,
		    GSList *f,
		     GSList *l)
{
	EventListener *el = g_object_new (EVENT_LISTENER_TYPE, NULL);
	if (l != NULL)
		el->pylisteners = l;
	el->funcs = f;
	el->queue = queue;
	return el;
}


void
event_listener_dispatch (EventListener *el,
			 Accessibility_Event *e)
{
	PyObject *event;
	GSList *tmp;
	
 	/* Call the C functions */

	for (tmp = el->funcs; tmp; tmp = tmp->next)
	{
		event_listener_func f = (event_listener_func) tmp->data;
		f (e);
	}

        /* Dispatch to the Python listener */

	for (tmp = el->pylisteners; tmp; tmp = tmp->next)
	{
		PyObject *l = (PyObject *) tmp->data;
		event = pyevent_new (e);
		Py_INCREF (event);
		PyObject_CallFunction (l, "O", event);
		if (PyErr_Occurred ())
		{
			PyErr_Print ();
			PyErr_Clear ();
		}
		Py_DECREF (event);
	}
}


static void
event_listener_init (EventListener *el)
{
	el->queue = NULL;
	el->funcs = NULL;
	el->pylisteners = NULL;
}


static void
event_listener_finalize (GObject *object)
{
	GSList *tmp;
	EventListener *el = EVENT_LISTENER (object);
	for (tmp = el->pylisteners; tmp; tmp = tmp->next)
	{
		Py_DECREF ((PyObject *)tmp->data);
	}
	if (el->pylisteners)
		g_slist_free (el->pylisteners);
	if (el->funcs)
		g_slist_free (el->funcs);
	parent_class->finalize (object);
}

static void
event_listener_class_init (EventListenerClass *klass)
{
	GObjectClass * object_class = G_OBJECT_CLASS(klass);
	POA_Accessibility_EventListener__epv *epv = &klass->epv;
	parent_class = g_type_class_peek_parent (klass);
	object_class->finalize = event_listener_finalize;

	/* Setup epv table */

	epv->notifyEvent = event_listener_notify_event;
}


BONOBO_TYPE_FUNC_FULL (EventListener,
		       Accessibility_EventListener,
		       bonobo_object_get_type (),
		       event_listener);
