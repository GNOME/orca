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

#include "eventqueue.h"
#include "eventlistener.h"

typedef struct {
	Accessibility_Event *event;
	EventListener *listener;
} EventQueueEntry;


EventQueueEntry *
event_queue_entry_new  (const Accessibility_Event *e,
		 EventListener *el)
{
	Accessibility_Event *event;
	EventQueueEntry *new_entry = g_new (EventQueueEntry, 1);
	CORBA_Environment ev;

	/* Copy the event */

	event = Accessibility_Event__alloc ();
	event->type = CORBA_string_dup (e->type);
	
	/* Keep a reference to the object */

	CORBA_exception_init (&ev);
	event->source = bonobo_object_dup_ref (e->source, &ev);
	event->detail1 = e->detail1;
	event->detail2 = e->detail2;
	CORBA_any__copy (&event->any_data, &e->any_data);
	new_entry->event = event;
	new_entry->listener = el;
	CORBA_exception_free (&ev);
	return new_entry;
}


void
event_queue_entry_destroy (EventQueueEntry *e)
{
	g_return_if_fail (e);
	CORBA_free (e->event);
	g_free (e);
}


EventQueue *
event_queue_new (void)
{
	EventQueue *queue = g_new (EventQueue, 1);
	queue->events = NULL;
	queue->cur = NULL;
	queue->idle_id = 0;
	return queue;
}


void
event_queue_destroy (EventQueue *queue)
{
	GList *tmp;
	g_return_if_fail (queue);

	for (tmp = queue->events; tmp; tmp = tmp->next)
	{
		EventQueueEntry *e = (EventQueueEntry *) tmp->data;
		event_queue_entry_destroy (e);
	}
	if (queue->events)
		g_list_free (queue->events);
	
	/* Remove the idle handler */

	if (queue->idle_id == 0)
		g_source_remove (queue->idle_id);
	
	g_free (queue);
}


/*
 *
 * This function gets called by the GLib main loop on idle
 *
 *
 */

static gboolean
event_queue_idle_handler (void *data)
{
	EventQueue *queue = (EventQueue *) data;
	EventQueueEntry *e;
	GList *tmp;

	/* Dispatch the currently pending event */

	e = (EventQueueEntry *) queue->cur->data;
	event_listener_dispatch (e->listener, e->event);
	event_queue_entry_destroy (e);
	
	/*
	 *
	 * Find the next event to dispatch.  Dispatching the current event may have caused the ORB to re-enter and more events to be added to the queue
	 *
	 */

	tmp = queue->cur->prev;
	queue->events = g_list_remove_link (queue->events, queue->cur);
	queue->cur = tmp;
	
	/* If we're out of events, remove the idle handler */
	
	if (!queue->cur)
	{
		queue->idle_id = 0;
		return FALSE;
	}
	else
		return TRUE;
}


void
event_queue_add (EventQueue *queue,
		 const Accessibility_Event *e,
		 void *el)
{
	EventQueueEntry *entry;

	entry = event_queue_entry_new (e, el);
	queue->events = g_list_prepend (queue->events, entry);
	
	/*
	 *
	 * If no idle handler is active, register one to dispatch
	 * this event on idle
	 *
	 */
	
	if (queue->idle_id == 0)
	{
		queue->cur = queue->events;
		queue->idle_id = g_idle_add (event_queue_idle_handler, queue);
	}
}
