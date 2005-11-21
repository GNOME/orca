
PYTHONPATH=$(top_srcdir)/src

DOC_FILES = \
	orca \
	orca.atspi \
	orca.braille \
	orca.braillegenerator \
	orca.brl \
	orca.chnames \
	orca.debug \
	orca.default \
	orca.eventsynthesizer \
	orca.flat_review \
	orca.focus_tracking_presenter \
	orca.hierarchical_presenter \
	orca.input_event \
	orca.kbd \
	orca.keybindings \
	orca.mag \
	orca.orca \
	orca.orca_i18n \
	orca.presentation_manager \
	orca.rolenames \
	orca.script \
	orca.settings \
	orca.speech \
	orca.speechgenerator \
	orca.scripts \
	orca.scripts.Gecko \
	orca.scripts.StarOffice \
	orca.scripts.gaim \
	orca.scripts.gcalctool \
	orca.scripts.gedit \
	orca.scripts.gnome-terminal \
	orca.scripts.metacity

if ENABLE_PYDOC
all:
	for i in $(DOC_FILES); \
	    do pydoc -w $$i; done
endif

