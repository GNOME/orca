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

#ifndef __EVENT_QUEUE_H
#define __EVENT_QUEUE_H

#include <glib.h>
#include "Accessibility.h"

/**
 * The data structure used for the EventQueue.
 * @idle_id: the idle id as returned by g_idle_add
 * @events: the list of events, most recent first
 * @cur: the next event to process
 */
typedef struct {
	guint idle_id;
	GList *events;
	GList *cur;
} EventQueue;


/**
 * event_queue_new:
 *
 * Creates a new and empty EventQueue.
 */
EventQueue *event_queue_new (void);


/**
 * event_queue_destroy:
 * @queue: the queue to destroy
 *
 * Frees up any memory and references associated with the given
 * EventQueue, including destroying any EventQueueEntry objects still
 * in the queue.
 */
void event_queue_destroy (EventQueue *queue);


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
		      void *el);
#endif
