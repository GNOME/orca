module_LTLIBRARIES = coremodule.la

moduledir = $(pyexecdir)/orca

coremodule_la_LIBADD = \
	$(core_LIBS)

coremodule_la_CFLAGS = \
	$(core_CFLAGS) \
	$(PYTHON_INCLUDES)

coremodule_la_LDFLAGS = \
	-module \
	-avoid-version

IDL_OUT = \
	Accessibility.h \
	Accessibility-stubs.c \
	Accessibility-skels.c \
	Accessibility-common.c

BUILT_SOURCES = $(IDL_OUT)

CLEANFILES = $(IDL_OUT)

IDL = \
	$(AT_SPI_IDLDIR)/Accessibility.idl

IDLFLAGS = \
	-D__ACCESSIBILITY_COMPILATION__ \
	$(AT_SPI_IDLFLAGS)

$(IDL_OUT) : $(IDL) $(ORBIT_IDL)
	$(ORBIT_IDL) $(IDLFLAGS) $(IDL)

coremodule_la_SOURCES = \
	$(BUILT_SOURCES) \
	coremodule.c \
	eventlistener.c \
	eventlistener.h \
	eventqueue.c \
	eventqueue.h \
	pyevent.c \
	pyevent.h
