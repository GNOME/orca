/* Liblouis Python bindings
 *
 * Copyright 2007-2008 Eitan Isaacson
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
#include <Python.h>
#include <liblouis.h>

static PyObject *module;

static PyObject *
louis_version(PyObject *self)
{
		const char *version_string;
		version_string = lou_version();
		return Py_BuildValue("s", version_string);
}


char *
pylist_to_string(PyObject *list)
{
		PyObject *list_joined, *sep;
		char *rv;

		sep = PyString_FromString(",");
		list_joined = PyUnicode_Join(sep, list);
		if (list_joined == NULL) 
        {
				/* Some list items were probably not strings */
				Py_DECREF(sep);
				return NULL;
        }
		rv = strdup(PyString_AsString(list_joined));

		Py_DECREF(list_joined);
		Py_DECREF(sep);

		return rv;
}

char *
pylist_to_typeform(PyObject *typeform_list, int len)
{
		char *typeform;
		int i;
		PyObject *l_item;
		typeform = calloc(len, sizeof(char));
		for (i=0; i < PySequence_Size(typeform_list); i++)
		{
				l_item = PySequence_Fast_GET_ITEM(typeform_list, i);
				typeform[i] = (char)PyInt_AsLong(l_item);
		}
		return typeform;
		
}

PyObject *
intbuf_to_pylist(int *intbuf, int len)
{
		PyObject *pylist;
		int i;

		pylist = PyList_New(len);

		for (i=0;i<len;i++)
				PyList_SetItem(pylist, i, PyInt_FromLong((long)intbuf[i]));

		return pylist;
}

static PyObject *
louis_translateString(PyObject *self, PyObject *args, PyObject *kw)
{
        static char *kw_args[]={"tran_tables", "inbuf", 
                                "typeform", "spacing", "mode", 0};
		char *typeform = NULL, *trantab_joined, *spacing = NULL;
		widechar *outbuf;
		int inlen, outlen, mode = 0;
		PyObject *trantab_list, *out, *typeform_list = NULL;
		Py_UNICODE *u_inbuf;
		int rv;

		if (!PyArg_ParseTupleAndKeywords(args, kw,
                                         "Ou#|OOi:translateString", kw_args,
                                         &trantab_list, &u_inbuf, &inlen,
                                         &typeform_list, &spacing, &mode))
		{
				return NULL;
        }
        
		trantab_joined = pylist_to_string(trantab_list);

        if (trantab_joined == NULL) 
        {
               PyErr_SetString(
                       PyExc_TypeError,
                       "translateString() argument 1 needs to be a list of strings"); 
               return NULL;
        }

		if (PySequence_Size(typeform_list) > 0) 
				typeform = pylist_to_typeform(typeform_list, inlen);

        outlen = inlen*2;
		outbuf = calloc(outlen, sizeof(widechar));

		rv = lou_translateString(trantab_joined, (widechar *)u_inbuf, 
                                 &inlen, outbuf, &outlen, typeform, 
                                 spacing, mode);

        out = PyUnicode_FromUnicode((Py_UNICODE *)outbuf, outlen);

		if (typeform != NULL)
				free(typeform);
		free(trantab_joined);
        free(outbuf);
        return out;

}

static PyObject *
louis_translate(PyObject *self, PyObject *args, PyObject *kw)
{
        static char *kw_args[]={"tran_tables", "inbuf", 
                                "typeform", "cursorPos","mode", 0};
		char *typeform = NULL, *trantab_joined, *spacing = NULL;
		widechar *outbuf;
		int inlen, outlen, mode = 0, cursorPos = 0;
		int rv, *outputPos, *inputPos;
		PyObject *trantab_list, *out, *typeform_list = NULL, *outputPos_list,
				*inputPos_list;
		Py_UNICODE *u_inbuf;

		if (!PyArg_ParseTupleAndKeywords(args, kw,
                                         "Ou#|Oii:translate", kw_args,
                                         &trantab_list, &u_inbuf, &inlen,
                                         &typeform_list, &cursorPos,
										 &mode))
		{
				return NULL;
        }
        
		trantab_joined = pylist_to_string(trantab_list);

        if (trantab_joined == NULL) 
        {
               PyErr_SetString(
                       PyExc_TypeError,
                       "translateString() argument 1 needs to be a list of strings"); 
               return NULL;
        }

		if (PySequence_Size(typeform_list) > 0) 
				typeform = pylist_to_typeform(typeform_list, inlen);

		inputPos = calloc(inlen, sizeof(int));

        outlen = inlen*2;
		outbuf = calloc(outlen, sizeof(widechar));
		outputPos = calloc(outlen, sizeof(int));

		rv = lou_translate(trantab_joined, (widechar *)u_inbuf, 
                           &inlen, outbuf, &outlen, typeform, spacing, 
                           outputPos, inputPos, &cursorPos, mode);

        out = PyUnicode_FromUnicode((Py_UNICODE *)outbuf, outlen);
		inputPos_list = intbuf_to_pylist(inputPos, inlen);
		outputPos_list = intbuf_to_pylist(outputPos, outlen);

		if (typeform != NULL) 
				free(typeform);
		free(trantab_joined);
        free(outbuf);
        free(outputPos);
        free(inputPos);

        Py_INCREF(outputPos_list);
        Py_INCREF(inputPos_list);
        Py_INCREF(out);

        PyErr_Clear();

        return Py_BuildValue("(NNNi)", out, inputPos_list, 
							 outputPos_list, cursorPos);

}

static PyMethodDef louis_methods[] = {
		{"version", 
         (PyCFunction) louis_version, METH_VARARGS},
		{"translateString", 
         (PyCFunction) louis_translateString, METH_KEYWORDS},
		{"translate", 
         (PyCFunction) louis_translate, METH_KEYWORDS},
		{NULL, NULL}
};

PyMODINIT_FUNC 
init_louis (void) {
        module = Py_InitModule ("_louis", louis_methods);
}
