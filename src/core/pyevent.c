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

#include <Python.h>
#include <pyorbit.h>
#include "pyevent.h"


static void
pyevent_dealloc (PyEvent *e)
{
	bonobo_object_release_unref (e->e->source);
	CORBA_free (&(e->e->any_data));
	CORBA_free (e->e);
}


PyObject *
pyevent_get_type (PyEvent *self)
{
	return PyString_FromString (self->e->type);
}


static PyObject *
pyevent_get_source (PyEvent *self)
{
	return pycorba_object_new (self->e->source);
}


static PyObject *
pyevent_get_detail1 (PyEvent *self)
{
	return PyInt_FromLong (self->e->detail1);
}


static PyObject *
pyevent_get_detail2 (PyEvent *self)
{
	return PyInt_FromLong (self->e->detail2);
}


static PyObject *
pyevent_get_any_data (PyEvent *self)
{
	return pyorbit_demarshal_any (&(self->e->any_data));
}


static PyGetSetDef pyevent_getsets[] = {
	{ "type", (getter) pyevent_get_type, (setter) 0 },
	{ "source", (getter) pyevent_get_source, (setter) 0 },
	{ "detail1", (getter) pyevent_get_detail1, (setter) 0 },
	{ "detail2", (getter) pyevent_get_detail2, (setter) 0 },
	{ "any_data", (getter) pyevent_get_any_data, (setter) 0 },
	{NULL, (getter)0, (setter)0 }
};


PyTypeObject PyEvent_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                  /* ob_size */
    "core.Event",                     /* tp_name */
    sizeof(PyEvent),             /* tp_basicsize */
    0,                                  /* tp_itemsize */
    /* methods */
    (destructor)pyevent_dealloc, /* tp_dealloc */
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
    0,             /* tp_methods */
    0,                                  /* tp_members */
    pyevent_getsets,                                  /* tp_getset */
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


void
pyevent_init (PyObject *mod)
{
	if (PyType_Ready(&PyEvent_Type) < 0)
		return;
	PyModule_AddObject (mod, "Event",
			    (PyObject *)&PyEvent_Type);
}


PyObject *
pyevent_new (const Accessibility_Event *e)
{
	CORBA_Environment ev;
	PyEvent *event;
	PyObject *args;

        /* Create the event object */

	args = PyTuple_New (0);
	event = (PyEvent *) PyEvent_Type.tp_new (&PyEvent_Type, args, NULL);
	Py_DECREF (args);

	event->e = Accessibility_Event__alloc ();
	event->e->type = CORBA_string_dup (e->type);
	event->e->detail1 = e->detail1;
	event->e->detail2 = e->detail2;
	event->e->source = e->source;
	bonobo_object_dup_ref (e->source, NULL);
	CORBA_any__copy (&(event->e->any_data), &e->any_data);
	return (PyObject *) event;
}


