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

/**
 * Manages the AT-SPI event queue for Orca.  Accessibility_Events are
 * added to this queue by the
 * eventlistener.c:event_listener_notify_event method, which is the
 * callback that was added to the ORB [[[TODO: WDW - by whom?]]]
 */
#include "eventqueue.h"
#include "eventlistener.h"

/**
 * An entry on the event queue.
 */
typedef struct {
	Accessibility_Event *event;
	EventListener *listener;
} EventQueueEntry;


/**
 * event_queue_entry_new:
 * @e: the Accessibility_Event from the AT-SPI Registry.
 * @el: the listener to call when this queue entry is handled
 *
 * Creates a new EventQueueEntry populated with the given the
 * Accessibility_Event and EventListener.
 *
 * Returns: a new EventQueueEntry populated with the given the
 * Accessibility_Event and EventListener.
 */
EventQueueEntry *event_queue_entry_new (const Accessibility_Event *e,
                                        EventListener *el) {
	Accessibility_Event *event;
	EventQueueEntry *new_entry = g_new (EventQueueEntry, 1);
	CORBA_Environment ev;

	/* Copy the event.
	 */
	event = Accessibility_Event__alloc ();
	event->type = CORBA_string_dup (e->type);	
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


/**
 * event_queue_entry_destroy:
 * @e: the entry to destroy
 *
 * Frees up any memory and references associated with the given
 * EventQueueEntry.
 */
void event_queue_entry_destroy (EventQueueEntry *e) {
	g_return_if_fail (e);
	CORBA_free (e->event);
	g_free (e);
}


/**
 * event_queue_new:
 *
 * Creates a new and empty EventQueue.
 */
EventQueue *event_queue_new (void) {
	EventQueue *queue = g_new (EventQueue, 1);
	queue->events = NULL;
	queue->cur = NULL;
	queue->idle_id = 0;
	return queue;
}


/**
 * event_queue_destroy:
 * @queue: the queue to destroy
 *
 * Frees up any memory and references associated with the given
 * EventQueue, including destroying any EventQueueEntry objects still
 * in the queue.
 */
void event_queue_destroy (EventQueue *queue) {
	GList *tmp;

	g_return_if_fail (queue);

	/* Empty the queue.
	 */
	for (tmp = queue->events; tmp; tmp = tmp->next) {
		EventQueueEntry *e = (EventQueueEntry *) tmp->data;
		event_queue_entry_destroy (e);
	}
	if (queue->events) {
		g_list_free (queue->events);
	}

	/* Remove the idle handler.  [[[TODO: WDW - this might need to
	 * be done before freeing up the queue.]]]
	 */
	if (queue->idle_id != 0) {
		g_source_remove (queue->idle_id);
	}

	g_free (queue);
}


/**
 * event_queue_idle_handler:
 * @data: the EventQueue
 *
 * Called by the GLib main loop in idle.
 *
 * Returns: TRUE if there are more events to handle; FALSE if not.
 */
static gboolean event_queue_idle_handler (void *data) {
	EventQueue *queue = (EventQueue *) data;
	EventQueueEntry *e;
	GList *tmp;

	/* Dispatch the currently pending event.
	 */
	e = (EventQueueEntry *) queue->cur->data;
	event_listener_dispatch (e->listener, e->event);
	event_queue_entry_destroy (e);
	
	/* Remove the event from the queue and find the next event to
	 * dispatch.
	 */
	tmp = queue->cur->prev;
	queue->events = g_list_remove_link (queue->events, queue->cur);
	queue->cur = tmp;
	
	/* If we're out of events, remove the idle handler.  Note that
	 * dispatching the current event may have caused the ORB to
	 * re-enter and more events to be added to the queue.
	 */
	if (!queue->cur) {
		queue->idle_id = 0; 
		return FALSE;
	} else {
		return TRUE;
	}
}


/**
 * event_queue_add:
 * @queue: the EventQueue to add the Accessibility_Event to
 * @e: the Accessibility_Event
 * @el: the EventListener to call when the EventQueueEntry for this
 * event is processed
 *
 * Creates a new EventQueueEntry for the given Accessibility_Event and
 * EventListener and then adds it to the given EventQueue.  Also adds
 * a new idle handler if the EventQueue was empty before this call.
 */
void event_queue_add (EventQueue *queue,
		      const Accessibility_Event *e,
		      void *el) {
	EventQueueEntry *entry;
	entry = event_queue_entry_new (e, el);
	queue->events = g_list_prepend (queue->events, entry);
	
	/* If no idle handler is active, register one to dispatch
	 * this event on idle
	 */
	if (queue->idle_id == 0) {
		queue->cur = queue->events;
		queue->idle_id = g_idle_add (event_queue_idle_handler, queue);
	}
}
