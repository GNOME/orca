
PYTHONPATH=@pyexecdir@

DOC_FILES = \
	orca \
	orca.acss \
	orca.app_gui_prefs \
	orca.atspi \
	orca.bookmarks \
	orca.braille \
	orca.braillegenerator \
	orca.brl \
	orca.brlmon \
	orca.chnames \
	orca.debug \
	orca.dectalk \
	orca.default \
	orca.espeechfactory \
	orca.eventsynthesizer \
	orca.find \
	orca.flat_review \
	orca.focus_tracking_presenter \
	orca.Gecko \
	orca.gnomespeechfactory \
	orca.httpserver \
	orca.input_event \
	orca.J2SE-access-bridge \
	orca.keybindings \
	orca.keynames \
	orca.mag \
	orca.orca \
	orca.orca_console_prefs \
	orca.orca_glade \
	orca.orca_gui_find \
	orca.orca_gui_main \
	orca.orca_gui_prefs \
	orca.orca_i18n \
	orca.orca_prefs \
	orca.orca_quit \
	orca.orca_state \
	orca.outloud \
	orca.phonnames \
	orca.platform \
	orca.presentation_manager \
	orca.pronunciation_dict \
	orca.punctuation_settings \
	orca.rolenames \
	orca.script \
	orca.settings \
	orca.speech \
	orca.speechdispatcherfactory \
	orca.speechgenerator \
	orca.speechserver \
	orca.where_am_I \
	orca.scripts \
	orca.scripts.acroread \
	orca.scripts.Evolution \
	orca.scripts.gaim \
	orca.scripts.gcalctool \
	orca.scripts.gdmlogin \
	orca.scripts.gedit \
	orca.scripts.gnome_segv2 \
	orca.scripts.gnome-keyring-ask \
	orca.scripts.gnome-mud \
	orca.scripts.gnome-panel \
	orca.scripts.gnome-search-tool \
	orca.scripts.gnome-system-monitor \
	orca.scripts.gnome-terminal \
	orca.scripts.gnome-window-properties \
	orca.scripts.liferea \
	orca.scripts.metacity \
	orca.scripts.Mozilla \
	orca.scripts.nautilus \
	orca.scripts.notification-daemon \
	orca.scripts.planner \
	orca.scripts.self_voicing \
	orca.scripts.StarOffice \
	orca.scripts.Thunderbird

if ENABLE_PYDOC
all:
	for i in $(DOC_FILES); \
	    do pydoc -w $$i; done
endif

