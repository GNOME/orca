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


/* Brlapi function pointers 
 */
static int (*brlapi_initializeConnection) (void *, void *);
static void (*brlapi_closeConnection) (void);
static char *(*brlapi_getDriverId) (void);
static char *(*brlapi_getDriverName) (void);
static int (*brlapi_getDisplaySize) (unsigned int *, unsigned int *);
static int (*brlapi_getTty) (int, int);
static int (*brlapi_leaveTty) (void);
static int (*brlapi_writeBrl) (unsigned int cursor, const char *text);
static int (*brlapi_readCommand) (unsigned int, unsigned int *);

/* From brldefs.h -- since hard linking/compilation of this module
 * isn't an option
 */
typedef enum {
  /* special commands which must be first and remain in order */
  CMD_NOOP = 0 /* do nothing */,

  /* vertical motion */
  CMD_LNUP /* go up one line */,
  CMD_LNDN /* go down one line */,
  CMD_WINUP /* go up several lines */,
  CMD_WINDN /* go down several lines */,
  CMD_PRDIFLN /* go up to line with different content */,
  CMD_NXDIFLN /* go down to line with different content */,
  CMD_ATTRUP /* go up to line with different attributes */,
  CMD_ATTRDN /* go down to line with different attributes */,
  CMD_TOP /* go to top line */,
  CMD_BOT /* go to bottom line */,
  CMD_TOP_LEFT /* go to top-left corner */,
  CMD_BOT_LEFT /* go to bottom-left corner */,
  CMD_PRPGRPH /* go to last line of previous paragraph */,
  CMD_NXPGRPH /* go to first line of next paragraph */,
  CMD_PRPROMPT /* go to previous command prompt */,
  CMD_NXPROMPT /* go to next command prompt */,
  CMD_PRSEARCH /* search backward for content of cut buffer */,
  CMD_NXSEARCH /* search forward for content of cut buffer */,
  
  /* horizontal motion */
  CMD_CHRLT /* go left one character */,
  CMD_CHRRT /* go right one character */,
  CMD_HWINLT /* go left half a window */,
  CMD_HWINRT /* go right half a window */,
  CMD_FWINLT /* go left one window */,
  CMD_FWINRT /* go right one window */,
  CMD_FWINLTSKIP /* go left to non-blank window */,
  CMD_FWINRTSKIP /* go right to non-blank window */,
  CMD_LNBEG /* go to beginning of line */,
  CMD_LNEND /* go to end of line */,
  
  /* implicit motion */
  CMD_HOME /* go to cursor */,
  CMD_BACK /* return to destination of most recent explicit motion */,
  
  /* feature activation and deactivation */
  CMD_FREEZE /* toggle screen frozen/unfrozen */,
  CMD_DISPMD /* toggle display attributes/text */,
  CMD_SIXDOTS /* toggle text style 6-dot/8-dot */,
  CMD_SLIDEWIN /* toggle sliding window on/off */,
  CMD_SKPIDLNS /* toggle skipping of identical lines on/off */,
  CMD_SKPBLNKWINS /* toggle skipping of blank windows on/off */,
  CMD_CSRVIS /* toggle cursor visibility on/off */,
  CMD_CSRHIDE /* toggle hide of cursor on/off */,
  CMD_CSRTRK /* toggle cursor tracking on/off */,
  CMD_CSRSIZE /* toggle cursor style block/underline */,
  CMD_CSRBLINK /* toggle cursor blinking on/off */,
  CMD_ATTRVIS /* toggle attribute underlining on/off */,
  CMD_ATTRBLINK /* toggle attribute blinking on/off */,
  CMD_CAPBLINK /* toggle capital letter blinking on/off */,
  CMD_TUNES /* toggle alert tunes on/off */,
 
  /* mode selection */
  CMD_HELP /* toggle help mode on/off */,
  CMD_INFO /* toggle info mode on/off */,
  CMD_LEARN /* enter command learn mode */,
  
  /* preference setting */
  CMD_PREFMENU /* present preferences menu */,
  CMD_PREFSAVE /* save current preferences */,
  CMD_PREFLOAD /* restore saved preferences */,
  
  /* menu navigation */
  CMD_MENU_FIRST_ITEM /* go to first item in menu */,
  CMD_MENU_LAST_ITEM /* go to last item in menu */,
  CMD_MENU_PREV_ITEM /* go to previous item in menu */,
  CMD_MENU_NEXT_ITEM /* go to next item in menu */,
  CMD_MENU_PREV_SETTING /* change value of current item in menu to previous choice */,
  CMD_MENU_NEXT_SETTING /* change value of current item in menu to next choice */,
 
  /* speech */
  CMD_SAY_LINE /* speak current line */,
  CMD_SAY_ABOVE /* speak from top through current line */,
  CMD_SAY_BELOW /* speak from current through bottom line */,
  CMD_MUTE /* stop speaking immediately */,
  CMD_SPKHOME /* go to current/last speech position */,
  
  /* virtual terminal switching */
  CMD_SWITCHVT_PREV /* switch to previous virtual terminal */,
  CMD_SWITCHVT_NEXT /* switch to next virtual terminal */,
  
  /* miscellaneous */
  CMD_CSRJMP_VERT /* vertically route cursor to top line of window */,
  CMD_PASTE /* insert cut buffer at cursor */,
  CMD_RESTARTBRL /* reinitialize braille driver */,
  CMD_RESTARTSPEECH /* reinitialize speech driver */,
  
  DriverCommandCount /* must be last */
} DriverCommand;

/* Brlapi related variables 
 */
static void *brlapi_library;
static long brl_initialized = 0;
static int brlapi_fd = -1;
static int brlapi_display_size_x = 0;
static int brlapi_display_size_y = 0;
static GIOChannel *brlapi_channel = NULL;


/* Python callback for Braille command notifications.
 * Only ONE callback can be registered at a time.
 */
static PyObject *brl_callback = NULL;


/* Braille regions 
*/
typedef struct {
	char *text;
	int len;
	int virtual_display_position;
	int size;
	int display_start;
	int cursor_position;
} brl_region;


static GList *brl_regions = NULL;
static brl_region *scroll_region = NULL;
static int physical_display_position = 0;
static virtual_display_length = 0;


static brl_region *brl_region_new (const gchar *text,
				   int size,
				   int display_start) {
	brl_region *region = g_new (brl_region, 1);

	region->len = strlen (text);
	region->text = g_strdup (text);
	region->size = size;
	region->display_start = display_start;
	region->cursor_position = -1;
	return region;
}


static void brl_region_destroy (brl_region *region) {
	g_return_if_fail (region);
	g_free (region->text);
	g_free (region);
}


static gboolean brl_region_scroll (brl_region *region,
				   int scroll_amount) {
	g_return_if_fail (region);
	
	if (region->display_start+scroll_amount < 0 ||
	    region->display_start+scroll_amount >= region->len)
		return FALSE;
	region->display_start += scroll_amount;
	return TRUE;
}


static gboolean brl_scroll_virtual_display (int scroll_amount) {
	if (physical_display_position+scroll_amount < 0 ||
	    physical_display_position+scroll_amount >= virtual_display_length)
		return FALSE;
	physical_display_position += scroll_amount;
	return TRUE;
}


static void refresh (void) {
	gchar *display;
	GList *tmp;
	brl_region *region;
	int cursor_position = -1;
	

	display = g_new (char, virtual_display_length+1);
	memset (display, ' ', virtual_display_length);
	display[virtual_display_length] = 0;

	for (tmp = brl_regions; tmp; tmp = tmp->next) {
		int bytes_to_copy;

		region = (brl_region *) tmp->data;

		if (region->size > region->len)
			bytes_to_copy = region->len;
		else
			bytes_to_copy = region->size;

		if (region->cursor_position >= 0) {
			cursor_position = region->cursor_position-region->display_start;
			if (cursor_position >= region->size || cursor_position < 0)
				cursor_position = -1;
			else
				cursor_position += region->virtual_display_position;
		}
		strncpy (display+region->virtual_display_position,
			 region->text+region->display_start,
			 bytes_to_copy);
	}
	if (cursor_position >= 0)
		cursor_position -= (physical_display_position-1);
	else
		cursor_position = 0;
	brlapi_writeBrl (cursor_position, &(display[physical_display_position]));
	g_free (display);
}


static void clear (void) {
	brl_region *region;
	GList *tmp;
 
        /* Destroy all the Braille regions */

	for (tmp = brl_regions; tmp; tmp = tmp->next) {
		region = (brl_region *) tmp->data;
		brl_region_destroy (region);
	}
	g_list_free (brl_regions);
	brl_regions = NULL;
	scroll_region = NULL;
	physical_display_position = 0;
	virtual_display_length = 0;
}


static gint brl_region_add (brl_region *region) {
	brl_region *cur;
	GList *tmp;
	gint region_num = 0;

	/* Find the region number */

	if (brl_regions)
		region_num = g_list_length (brl_regions);
	
	/* Position the region on the virtual display */

	region->virtual_display_position = virtual_display_length;
	virtual_display_length += region->size;
	brl_regions = g_list_append (brl_regions, region);
	return region_num;
}


static void brl_region_remove (gint region_num) {
	GList *l = g_list_nth (brl_regions, region_num);
	brl_region *region;

	g_return_if_fail (l);

	region = (brl_region *) l->data;
	
	brl_regions = g_list_remove (brl_regions, l);
	brl_region_destroy (region);
}


static void brl_region_update (int region_num,
			       const char *text,
			       int display_start) {
	GList *l = g_list_nth (brl_regions, region_num);
	brl_region *region;

	g_return_if_fail (l);

	region = (brl_region *) l->data;

	g_free (region->text);
	region->text = g_strdup (text);
	region->len = strlen (text);
	region->display_start = display_start;
}


static gboolean brlapi_io_cb (GIOChannel *ch,
			      GIOCondition condition,
			      void *data) {
	unsigned int  keypress;
	int region_num = -1;
	int region_position = -1;
	PyObject *result = NULL;
	PyObject *args;
	GList *l = brl_regions;
	brl_region *r;

	while (brlapi_readCommand (0, &keypress) == 1)
	{
		printf("brlapi_io_cb - keypress = %d\n", keypress);
		switch (keypress) {
		case CMD_FWINRT:
			if (scroll_region) {
				brl_region_scroll (scroll_region, scroll_region->size);
				refresh ();
			}
			else {
				brl_scroll_virtual_display (brlapi_display_size_x);
				refresh ();
			}
			break;
		case CMD_FWINLT:
			if (scroll_region) {
				brl_region_scroll (scroll_region, -(scroll_region->size));
				refresh ();
			}
			else {
				brl_scroll_virtual_display (-brlapi_display_size_x);
				refresh ();
			}
			break;
		default:
			if (!brl_callback)
				break;
			keypress -= 0X100;
			keypress += physical_display_position;
			region_num = 0;
			while (l) {
				r = (brl_region *) l->data;
				if (keypress >= r->virtual_display_position &&
				    keypress < r->virtual_display_position+r->size) {
					region_position = keypress-r->virtual_display_position+r->display_start;
					break;
				}
				region_num++;
				l = l->next;
			}
			if (!l)
				break;
			args = Py_BuildValue ("ii", region_num, region_position);
			result = PyObject_CallObject (brl_callback, args);
			if (result)
				Py_DECREF (result);
			Py_DECREF (args);
			
		}
			break;
	}
	return TRUE;
}


static PyObject *brl_module_init (PyObject *self) {
	int fd;
        int ttyNum;

	if (brl_initialized)
	{
		PyErr_SetString(PyExc_StandardError, "Already initialized");
		return NULL;
	}

	/* Open the brlapi library */

	brlapi_library = dlopen ("libbrlapi.so", RTLD_LAZY);
	if (!brlapi_library) {
  	        fprintf (stderr, 
			 "Failed to load libbrlapi.so\n");
		return PyInt_FromLong (0);
	}

	/* Load the functions */

	brlapi_initializeConnection = dlsym (brlapi_library, "brlapi_initializeConnection");
	if (!brlapi_initializeConnection) {
  	        fprintf (stderr, 
			 "Failed to find brlapi_initializeConnection in brltty.\n");
		return PyInt_FromLong (0);
	}

	brlapi_closeConnection = dlsym (brlapi_library, "brlapi_closeConnection");
	if (!brlapi_closeConnection) {
  	        fprintf (stderr,
			 "Failed to find brlapi_closeConnection in brltty.\n");
		return PyInt_FromLong (0);
	}

	brlapi_getDriverId = dlsym (brlapi_library, "brlapi_getDriverId");
	if (!brlapi_getDriverId) {
  	        fprintf (stderr, 
			 "Failed to find brlapi_getDriverId in brltty.\n");
		return PyInt_FromLong (0);
	}

	brlapi_getDriverName = dlsym (brlapi_library, "brlapi_getDriverName");
	if (!brlapi_getDriverName) {
		return PyInt_FromLong (0);
  	        fprintf (stderr,
			 "Failed to find brlapi_getDriverName in brltty.\n");
	}

	brlapi_getDisplaySize = dlsym (brlapi_library, "brlapi_getDisplaySize");
	if (!brlapi_getDisplaySize) {
  	        fprintf (stderr,
			 "Failed to find brlapi_getDisplaySize in brltty.\n");
		return PyInt_FromLong (0);
	}

	brlapi_getTty = dlsym (brlapi_library, "brlapi_getTty");
	if (!brlapi_getTty) {
  	        fprintf (stderr, 
			 "Failed to find brlapi_getTty in brltty.\n");
		return PyInt_FromLong (0);
	}

	brlapi_leaveTty = dlsym (brlapi_library, "brlapi_leaveTty");
	if (!brlapi_leaveTty) {
  	        fprintf (stderr,
			 "Failed to find brlapi_leaveTty in brltty.\n");
		return PyInt_FromLong (0);
	}

	brlapi_writeBrl = dlsym (brlapi_library, "brlapi_writeText");
	if (!brlapi_writeBrl) {
  	        fprintf (stderr,
			 "Failed to find brlapi_writeText in brltty.\n");
		return PyInt_FromLong (0);
	}

	brlapi_readCommand = dlsym (brlapi_library, "brlapi_readKey");
	if (!brlapi_readCommand) {
  	        fprintf (stderr,
			 "Failed to find brlapi_readKey in brltty.\n");
		return PyInt_FromLong (0);
	}

	/* Connect to brltty */

	brlapi_fd = brlapi_initializeConnection (NULL, NULL);
	if (brlapi_fd >= 0)
	{
		
		/* Take over the owning tty */

 	        ttyNum = brlapi_getTty (-1, /* Search for CONTROLVT      */
					0); /* HOW = give me BRLCOMMANDS */
		if (ttyNum == -1) {
 		        fprintf (stderr,
				 "Failed on call to brlapi_getTty in brltty.\n");
			return PyInt_FromLong (0);
		}

		/* Cache the Braille display size */

		brlapi_getDisplaySize (&brlapi_display_size_x,
				       &brlapi_display_size_y);

		/* Setup the GIOChannel to receive notifications of Braille key events */

		brlapi_channel = g_io_channel_unix_new (brlapi_fd);
		g_io_add_watch (brlapi_channel,
				G_IO_IN, 
				brlapi_io_cb,
				NULL);
		brl_initialized = 1;
	}
	else
	{
  	        fprintf (stderr,
			 "Failed on call to brlapi_initializeConnection in brltty.\n");
		brlapi_fd = -1;
	}
	return PyInt_FromLong (brl_initialized);
}


static PyObject *brl_module_shutdown (PyObject *self) {
        if (brl_initialized) {
  	        brlapi_leaveTty ();
		brlapi_closeConnection ();
	}
	brl_initialized = 0;
	return PyInt_FromLong (1);;
}


static PyObject *brl_module_getDriverId (PyObject *self) {
	if (!brl_initialized)
	{
		Py_INCREF (Py_None);
		return Py_None;
	}
	return PyString_FromString (brlapi_getDriverId());
}


static PyObject *brl_module_getDriverName (PyObject *self) {
	if (!brl_initialized)
	{
		Py_INCREF (Py_None);
		return Py_None;
	}
	return PyString_FromString (brlapi_getDriverName());
}


static PyObject *brl_module_getDisplaySize (PyObject *self) {
	int x, y;
	if (!brl_initialized)
	{
		return PyInt_FromLong (0);
	}

	brlapi_getDisplaySize (&x, &y);
	return PyInt_FromLong (x);
}


static PyObject *brl_module_writeMessage (PyObject *self,
					  PyObject *args) {
	char *str;
	brl_region *region;
	
	if (!PyArg_ParseTuple (args, "s:writeMessage", &str))
		return NULL;
	if (brl_initialized)
	{
		clear ();
		region = brl_region_new (str, brlapi_display_size_x, 0);
		brl_region_add (region);
		scroll_region = region;
		refresh ();
	}	
	Py_INCREF (Py_None);
	return Py_None;
}


static PyObject *brl_module_clear (PyObject *self) {
	if (brl_initialized)
		clear ();
	Py_INCREF (Py_None);
	return Py_None;
}


static PyObject *brl_module_refresh (PyObject *self) {
	if (brl_initialized)
		refresh ();
	Py_INCREF (Py_None);
	return Py_None;
}


static PyObject *brl_module_addRegion (PyObject *self,
				       PyObject *args) {
	char *text;
	int size;
	int display_start;
	brl_region *region;
	int region_num;
	
	if (!PyArg_ParseTuple (args, "sii:addRegion",
			       &text,
			       &size,
			       &display_start))
		return NULL;
	if (brl_initialized)
	{
		region = brl_region_new (text, size, display_start);
		region_num = brl_region_add (region);
		return PyInt_FromLong (region_num);
	}
	return PyInt_FromLong (0);
}


static PyObject *brl_module_removeRegion (PyObject *self,
					  PyObject *args) {
	int region_num;
	
	if (!PyArg_ParseTuple (args, "i:removeRegion", &region_num))
		return NULL;
	if (brl_initialized)
		brl_region_remove (region_num);
	Py_INCREF (Py_None);
	return Py_None;
}


static PyObject *brl_module_updateRegion (PyObject *self,
					  PyObject *args) {
	int region_num;
	char *text;
	int display_start;

	if (!PyArg_ParseTuple (args, "isi:updateRegion",
			       &region_num,
			       &text,
			       &display_start))
		return NULL;
	if (brl_initialized)
		brl_region_update (region_num, text, display_start);
	Py_INCREF (Py_None);
	return Py_None;
}


static PyObject *brl_module_setCursor (PyObject *self,
				       PyObject *args) {
	GList *l;
	int region_num;
	int cursor_position;
	brl_region *region;
	int scroll_amount;
	
	if (!PyArg_ParseTuple (args, "ii:setCursor",
			       &region_num,
			       &cursor_position))
		return NULL;
	if (brl_initialized)
	{
		l = g_list_nth (brl_regions, region_num);
		if (!l)
			return NULL;
		region = (brl_region *) l->data;
		if (!region)
			return NULL;

		/* Do we have to scroll the region to make the cursor visible */

		scroll_amount = cursor_position-region->display_start;
		if (scroll_amount < 0 && scroll_amount % region->size)
			scroll_amount = ((scroll_amount/region->size)+1)*region->size;
		else
			scroll_amount = (scroll_amount/region->size)*region->size;
		region->cursor_position = cursor_position;
		region->display_start += scroll_amount;

		/* Scroll the virtual display to make the cursor visible */

		scroll_amount = region->virtual_display_position-physical_display_position;
		if (scroll_amount < 0 && scroll_amount % brlapi_display_size_x)
			scroll_amount = ((scroll_amount/brlapi_display_size_x)+1)*brlapi_display_size_x;
		else
			scroll_amount = (scroll_amount/brlapi_display_size_x)*brlapi_display_size_x;
		physical_display_position += scroll_amount;
	}
	Py_INCREF (Py_None);
	return Py_None;
}


static PyObject *brl_module_setScrollRegion (PyObject *self,
					     PyObject *args) {
	brl_region *region;
	int region_num;
	GList *l;

	if (!PyArg_ParseTuple (args, "i:setScrollRegion", &region_num))
		return NULL;
	if (brl_initialized)
	{
		l = g_list_nth (brl_regions, region_num);
		if (!l)
			return NULL;
		region = (brl_region *) l->data;
		scroll_region = region;
	}
	return PyInt_FromLong (1l);
}


static PyObject *brl_module_registerCallback (PyObject *self,
					      PyObject *args) {
 	if (brl_callback)
		Py_DECREF (brl_callback);
	if (brl_initialized)
	{
		brl_callback = PyTuple_GetItem (args, 0);
		Py_INCREF (brl_callback);
	}
	Py_INCREF (Py_None);
	return Py_None;
}


static PyObject *brl_module_unregisterCallback (PyObject *self) {
 	if (brl_callback)
		Py_DECREF (brl_callback);
	brl_callback = NULL;
	Py_INCREF (Py_None);
	return Py_None;
}


static PyMethodDef brl_methods[] = {
	{"init", (PyCFunction) brl_module_init, METH_NOARGS},
	{"shutdown", (PyCFunction) brl_module_shutdown, METH_NOARGS},
	{"getDriverId", (PyCFunction) brl_module_getDriverId, METH_NOARGS},
	{"getDriverName", (PyCFunction) brl_module_getDriverName, METH_NOARGS},
	{"getDisplaySize", (PyCFunction) brl_module_getDisplaySize, METH_NOARGS},
	{"writeMessage", (PyCFunction) brl_module_writeMessage, METH_VARARGS},
	{"clear", (PyCFunction) brl_module_clear, METH_NOARGS},
	{"refresh", (PyCFunction) brl_module_refresh, METH_NOARGS},
	{"addRegion", (PyCFunction) brl_module_addRegion, METH_VARARGS},
	{"removeRegion", (PyCFunction) brl_module_removeRegion, METH_VARARGS},
	{"updateRegion", (PyCFunction) brl_module_updateRegion, METH_VARARGS},
	{"setCursor", (PyCFunction) brl_module_setCursor, METH_VARARGS},
	{"setScrollRegion", (PyCFunction) brl_module_setScrollRegion, METH_VARARGS},
	{"registerCallback", (PyCFunction) brl_module_registerCallback, METH_VARARGS},
	{"unregisterCallback", (PyCFunction) brl_module_unregisterCallback, METH_NOARGS},
	{NULL, NULL}
};

void initbrl (void) {
	(void) Py_InitModule ("brl", brl_methods);
}
