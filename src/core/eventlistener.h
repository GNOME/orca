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

#ifndef _EVENT_LISTENER_H
#define _EVENT_LISTENER_H


#include <bonobo/bonobo-object.h>
#include "Accessibility.h"
#include <pyorbit.h>
#include "eventqueue.h"


struct EventQueue;


#define EVENT_LISTENER_TYPE        (event_listener_get_type ())
#define EVENT_LISTENER(o)          (G_TYPE_CHECK_INSTANCE_CAST ((o), EVENT_LISTENER_TYPE, EventListener))
#define EVENT_LISTENER_CLASS(k)    (G_TYPE_CHECK_CLASS_CAST((k), EVENT_LISTENER_TYPE, EventListenerClass))
#define IS_EVENT_LISTENER(o)       (G_TYPE_CHECK_INSTANCE_TYPE ((o), EVENT_LISTENER_TYPE))
#define IS_EVENT_LISTENER_CLASS(k) (G_TYPE_CHECK_CLASS_TYPE ((k), EVENT_LISTENER_TYPE))

typedef void (*event_listener_func)(Accessibility_Event *e);


typedef struct {
	BonoboObject parent;

	/* The event queue associated with this listener */
	
	EventQueue *queue;

        /* A C function */

	GSList *funcs;
	
	/* A Python function */

	GSList *pylisteners;
} EventListener;


typedef struct {
	BonoboObjectClass parent_class;
	POA_Accessibility_EventListener__epv epv;
} EventListenerClass;



GType
event_listener_get_type (void);
EventListener *
event_listener_new (EventQueue *queue,
		    GSList  *f,
		    GSList *l);
void
event_listener_dispatch (EventListener *el,
			 Accessibility_Event *e);


#endif /* _EVENT_LISTENER_H */
