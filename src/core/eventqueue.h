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

#ifndef __EVENT_QUEUE_H
#define __EVENT_QUEUE_H


#include <glib.h>
#include "Accessibility.h"



typedef struct {
	guint idle_id;
	GList *events;
	GList *cur;
} EventQueue;


EventQueue *
event_queue_new (void);
void
event_queue_destroy (EventQueue *queue);
void
event_queue_add (EventQueue *queue,
		 const Accessibility_Event *e,
		 void *el);


#endif
