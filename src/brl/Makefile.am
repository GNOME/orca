module_LTLIBRARIES = brlmodule.la

moduledir = $(pyexecdir)/orca

brlmodule_la_LIBADD = \
	$(brl_LIBS)

brlmodule_la_CFLAGS = \
	$(brl_CFLAGS) \
	$(PYTHON_INCLUDES)

brlmodule_la_LDFLAGS = \
	-module \
	-avoid-version

brlmodule_la_SOURCES = \
	brlmodule.c
