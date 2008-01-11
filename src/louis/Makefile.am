louis_LTLIBRARIES = _louis.la

louisdir = $(pyexecdir)/orca/louis

_louis_la_CFLAGS = \
	$(louis_CFLAGS) \
	$(PYTHON_INCLUDES)

_louis_la_LDFLAGS = \
	-module \
	-avoid-version \
	-llouis

_louis_la_SOURCES = \
	_louis.c

louis_pythondir=$(louisdir)

louis_python_PYTHON = \
	__init__.py \
	constants.py