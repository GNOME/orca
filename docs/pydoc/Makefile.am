
PYTHONPATH=@pyexecdir@

DOC_FILES = \
	orca \
	orca.acss \
	orca.atspi \
	orca.braillegenerator \
	orca.braille \
	orca.brl \
	orca.brlmon \
	orca.chnames \
	orca.debug \
	orca.dectalk \
	orca.default \
	orca.espeechfactory \
	orca.eventsynthesizer \
	orca.flat_review \
	orca.focus_tracking_presenter \
	orca.Gecko \
	orca.gnomespeechfactory \
	orca.hierarchical_presenter \
	orca.httpserver \
	orca.input_event \
	orca.J2SE-access-bridge \
	orca.keybindings \
	orca.keynames \
	orca.mag \
	orca.orca_console_prefs \
	orca.orca_gui_prefs \
	orca.orca_i18n \
	orca.orca_prefs \
	orca.orca \
	orca.orca_state \
	orca.outloud \
	orca.platform \
	orca.presentation_manager \
	orca.rolenames \
	orca.script \
	orca.settings \
	orca.speechgenerator \
	orca.speechserver \
	orca.speech \
	orca.util \
	orca.scripts \
	orca.scripts.Evolution \
	orca.scripts.gaim \
	orca.scripts.gcalctool \
	orca.scripts.gdmlogin \
	orca.scripts.gedit \
	orca.scripts.gnome-terminal \
	orca.scripts.gnome-window-properties \
	orca.scripts.metacity \
	orca.scripts.Mozilla \
	orca.scripts.planner \
	orca.scripts.self_voicing \
	orca.scripts.StarOffice

if ENABLE_PYDOC
all:
	for i in $(DOC_FILES); \
	    do pydoc -w $$i; done
endif

