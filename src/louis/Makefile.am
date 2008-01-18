louis_LTLIBRARIES = _louis.la

louisdir = $(pyexecdir)/orca/louis

_louis_la_CFLAGS = 		\
	$(LOUIS_CFLAGS) 	\
	$(PYTHON_INCLUDES)

_louis_la_LDFLAGS = 	\
	$(LOUIS_LIBS)	\
	-module 			\
	-avoid-version 		\
	-llouis

_louis_la_SOURCES = \
	_louis.c

louis_pythondir=$(louisdir)

louis_python_PYTHON = \
	__init__.py 

nodist_louis_python_PYTHON = \
	constants.py