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
#include <string.h>
#include <errno.h>
#include <dlfcn.h>
#include <glib.h>
#include <Python.h>


/* BrlAPI function pointers - these map directly to BrlAPI 3.6.2 methods.
 */
static int (*brlapi_initializeConnection)(const void *clientSettings, 
					  const void *usedSettings);
static void (*brlapi_closeConnection)(void);

static int (*brlapi_getDriverId)(unsigned char *id, unsigned int n);
static int (*brlapi_getDriverName)(unsigned char *name, unsigned int n);
static int (*brlapi_getDisplaySize)(unsigned int *x, unsigned int *y);

static int (*brlapi_getTty) (int tty, int how);
static int (*brlapi_leaveTty) (void);

static int (*brlapi_writeText) (int cursor, const unsigned char *str);
static int (*brlapi_writeDots) (const unsigned char *dots);

static int (*brlapi_readKey) (int block, unsigned int *code);

/* A non-zero value indicates this module has been initialized and is
 * ready for communication with BrlTTY.
 */
static long brl_initialized = 0;

/* Python callback for Braille command notifications.  Only ONE callback can
 * be registered at a time.
 */
static PyObject *brl_callback = NULL;

/* The g_io_add_watch (see glib docs) that keeps track of input events
 * coming from BrlTTY.
 */
static gboolean brlapi_io_cb(GIOChannel *ch,
			     GIOCondition condition,
			     void *data) {

	unsigned int keypress;
	PyObject *result;
	PyObject *args;

	while (brlapi_readKey(0, &keypress) == 1) {
	        if (!brl_callback) {
		        break;
	        }
	        args = Py_BuildValue("(i)", keypress);
	        result = PyObject_CallObject(brl_callback, args);
		if (result != NULL) {
		        Py_DECREF(result);
		} else {
		        PyErr_Print();
                }
	        Py_DECREF(args);		
	}
	return TRUE;
}


/* Initializes the brl module, connecting to BrlTTY.  Returns 0 on failure or
 * 1 on success.  The first argument is optional and indicated the tty to
 * open.  The default value for this argument is -1, which means to let BrlTTY
 * use its default logic.  A typical value might be 7 which is usually what
 * the CONTROLVT should be set to for a console running the X11 server.  The
 * second argument is also optional and is to be passed to brlapi_getTty and
 * is used to tell BrlTTY whether to return raw keycodes (BRLKEYCODES=1) or
 * BrlTTY commands (BRLCOMMANDS=0).  The default value is to give us
 * BRLCOMMANDS.
 */
static PyObject *brl_module_init(PyObject *self,
				 PyObject *args) {
        int tty = -1;
        int how = 0;  /* BRLCOMMANDS */
        int ttyNum;

	void *brlapi_library;
	int brlapi_fd;
	GIOChannel *brlapi_channel;

	if (brl_initialized) {
		PyErr_SetString(PyExc_StandardError, "Already initialized");
		return NULL;
	}

	if (!PyArg_ParseTuple (args, "|ii:init", &tty, &how))
		return NULL;

	/* Open the brlapi library 
         */
	brlapi_library = dlopen("libbrlapi.so", RTLD_LAZY);
	if (!brlapi_library) {
  	        fprintf(stderr, "Failed to load libbrlapi.so\n");
		return PyInt_FromLong(0);
	}

	/* Load the functions */

	brlapi_initializeConnection = 
                (int (*)(const void *, const void *)) dlsym(brlapi_library, 
					    "brlapi_initializeConnection");
	if (!brlapi_initializeConnection) {
  	        fprintf(stderr, 
			"Failed to find brlapi_initializeConnection in BrlTTY.\n");
		return PyInt_FromLong(0);
	}

	brlapi_closeConnection = 
                (void (*)(void)) dlsym(brlapi_library, 
                                       "brlapi_closeConnection");
	if (!brlapi_closeConnection) {
  	        fprintf(stderr,
			"Failed to find brlapi_closeConnection in BrlTTY.\n");
		return PyInt_FromLong(0);
	}

	brlapi_getDriverId = 
                (int (*)(unsigned char *, unsigned int)) dlsym(brlapi_library, 
				                        "brlapi_getDriverId");
	if (!brlapi_getDriverId) {
  	        fprintf(stderr, 
			"Failed to find brlapi_getDriverId in BrlTTY.\n");
		return PyInt_FromLong(0);
	}

	brlapi_getDriverName = 
                (int (*)(unsigned char *, unsigned int)) dlsym(brlapi_library, 
				                       "brlapi_getDriverName");
	if (!brlapi_getDriverName) {
  	        fprintf(stderr,
			"Failed to find brlapi_getDriverName in BrlTTY.\n");
		return PyInt_FromLong(0);
	}

	brlapi_getDisplaySize = 
                (int (*)(unsigned int *, unsigned int *)) dlsym(brlapi_library, 
				                      "brlapi_getDisplaySize");
	if (!brlapi_getDisplaySize) {
  	        fprintf(stderr,
			"Failed to find brlapi_getDisplaySize in BrlTTY.\n");
		return PyInt_FromLong(0);
	}

	brlapi_getTty = 
                (int (*) (int tty, int how)) dlsym(brlapi_library, 
			                           "brlapi_getTty");
	if (!brlapi_getTty) {
  	        fprintf(stderr, 
			"Failed to find brlapi_getTty in BrlTTY.\n");
		return PyInt_FromLong(0);
	}
	
	brlapi_leaveTty = 
                (int (*) (void)) dlsym(brlapi_library, 
				       "brlapi_leaveTty");
	if (!brlapi_leaveTty) {
  	        fprintf(stderr,
			"Failed to find brlapi_leaveTty in BrlTTY.\n");
		return PyInt_FromLong(0);
	}

	brlapi_writeText = 
                (int (*) (int, const unsigned char *)) dlsym(brlapi_library, 
                                                         "brlapi_writeText");
	if (!brlapi_writeText) {
  	        fprintf(stderr,
			"Failed to find brlapi_writeText in BrlTTY.\n");
		return PyInt_FromLong(0);
	}

	brlapi_writeDots = 
                (int (*) (const unsigned char *)) dlsym(brlapi_library, 
                                                        "brlapi_writeDots");
	if (!brlapi_writeDots) {
  	        fprintf(stderr,
			"Failed to find brlapi_writeDots in BrlTTY.\n");
		return PyInt_FromLong(0);
	}

	brlapi_readKey = 
                (int (*) (int, unsigned int *)) dlsym(brlapi_library, 
                                                      "brlapi_readKey");
	if (!brlapi_readKey) {
	        fprintf(stderr,
			"Failed to find brlapi_readKey in BrlTTY.\n");
		return PyInt_FromLong(0);
	}

	/* Connect to BrlTTY 
	 */
	brlapi_fd = brlapi_initializeConnection(NULL, NULL);
	if (brlapi_fd >= 0) {		
		/* Take over the owning tty. 
		 */
 	        ttyNum = brlapi_getTty(tty,
				       0); /* HOW = give me BRLCOMMANDS */
		if (ttyNum == -1) {
 		        fprintf(stderr,
				"Failed on call to brlapi_getTty in BrlTTY.\n");
			return PyInt_FromLong(0);
		}

		/* Setup the GIOChannel to receive notifications of Braille 
		 * key events 
		 */
		brlapi_channel = g_io_channel_unix_new(brlapi_fd);
		g_io_add_watch(brlapi_channel,
			       G_IO_IN, 
			       brlapi_io_cb,
			       NULL);
		brl_initialized = 1;
	} else {
  	        fprintf(stderr,
			"Failed on call to brlapi_initializeConnection in BrlTTY.\n");
	}
	return PyInt_FromLong(brl_initialized);
}


static PyObject *brl_module_shutdown(PyObject *self) {
        if (brl_initialized) {
	        /* [[[TODO: WDW - clean up the g_io_channel here?]]] 
		 */ 
  	        brlapi_leaveTty();
		brlapi_closeConnection();
	}
	brl_initialized = 0;
	return PyInt_FromLong(1);
}


static PyObject *brl_module_getDriverId (PyObject *self) {
        unsigned char id[3];

        if (!brl_initialized) {
		Py_INCREF (Py_None);
		return Py_None;
	}

	if (brlapi_getDriverId(id, sizeof(id)) >= 0) {
	        PyString_FromString((const char *) id);
	} else {
		Py_INCREF (Py_None);
		return Py_None;
	}
}


static PyObject *brl_module_getDriverName(PyObject *self) {
        unsigned char name[80];

	if (!brl_initialized) {
		Py_INCREF(Py_None);
		return Py_None;
	}
	
	if (brlapi_getDriverName(name, sizeof(name)) >= 0) {
	        PyString_FromString((const char *) name);
	} else {
		Py_INCREF (Py_None);
		return Py_None;
	}
}


static PyObject *brl_module_getDisplayWidth(PyObject *self) {
	unsigned int x, y;

	if (!brl_initialized) {
		return PyInt_FromLong(0);
	}

	brlapi_getDisplaySize(&x, &y);
	return PyInt_FromLong(x);
}


static PyObject *brl_module_getDisplayHeight(PyObject *self) {
	unsigned int x, y;

	if (!brl_initialized) {
		return PyInt_FromLong(0);
	}

	brlapi_getDisplaySize(&x, &y);
	return PyInt_FromLong(y);
}


static PyObject *brl_module_writeText(PyObject *self,
				      PyObject *args) {
        int cursor;
	char *str;
	
	if (!PyArg_ParseTuple(args, "is:writeText", &cursor, &str)) {
		return NULL;
	}

	if (brl_initialized) {
	    brlapi_writeText(cursor, (const unsigned char *) str);
	}	

	Py_INCREF(Py_None);
	return Py_None;
}


static PyObject *brl_module_writeDots(PyObject *self,
				      PyObject *args) {
	char *str;
	
	if (!PyArg_ParseTuple(args, "s:writeText", &str)) {
		return NULL;
	}

	if (brl_initialized) {
	    brlapi_writeDots((const unsigned char *) str);
	}	
	Py_INCREF(Py_None);
	return Py_None;
}


static PyObject *brl_module_registerCallback(PyObject *self,
					     PyObject *args) {
        if (brl_callback) {
		Py_DECREF (brl_callback);
        }
	if (brl_initialized) {
		brl_callback = PyTuple_GetItem(args, 0);
		Py_INCREF(brl_callback);
	}
	Py_INCREF(Py_None);
	return Py_None;
}


static PyObject *brl_module_unregisterCallback(PyObject *self) {
 	if (brl_callback)
		Py_DECREF(brl_callback);
	brl_callback = NULL;
	Py_INCREF(Py_None);
	return Py_None;
}


static PyMethodDef brl_methods[] = {
	{"init", (PyCFunction) brl_module_init, METH_VARARGS},
	{"shutdown", (PyCFunction) brl_module_shutdown, METH_NOARGS},
	{"getDriverId", (PyCFunction) brl_module_getDriverId, METH_NOARGS},
	{"getDriverName", (PyCFunction) brl_module_getDriverName, METH_NOARGS},
	{"getDisplayWidth", (PyCFunction) brl_module_getDisplayWidth, METH_NOARGS},
	{"getDisplayHeight", (PyCFunction) brl_module_getDisplayWidth, METH_NOARGS},
	{"writeText", (PyCFunction) brl_module_writeText, METH_VARARGS},
	{"writeDots", (PyCFunction) brl_module_writeDots, METH_VARARGS},
	{"registerCallback", (PyCFunction) brl_module_registerCallback, METH_VARARGS},
	{"unregisterCallback", (PyCFunction) brl_module_unregisterCallback, METH_NOARGS},
	{NULL, NULL}
};

void initbrl (void) {
	(void) Py_InitModule ("brl", brl_methods);
}
