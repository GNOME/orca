orca_SCRIPTS = \
	orca

orcadir=$(bindir)
uidir=$(datadir)/orca/ui
gfxdir=$(datadir)/orca/gfx

orca_pathdir=$(pyexecdir)

orca_python_PYTHON = \
	__init__.py \
	acss.py \
	app_gui_prefs.py \
	app_prefs.py \
	bookmarks.py \
	braille.py \
	braille_generator.py \
	brlmon.py \
	chat.py \
	chnames.py \
	common_keyboardmap.py \
	dbusserver.py \
	debug.py \
	dectalk.py \
	desktop_keyboardmap.py \
	espeechfactory.py \
	event_manager.py \
	eventsynthesizer.py \
	find.py \
	flat_review.py \
	formatting.py \
	generator.py \
	gnomespeechfactory.py \
	gsmag.py \
	httpserver.py \
	input_event.py \
	keybindings.py \
	keynames.py \
	laptop_keyboardmap.py \
	liveregions.py \
	mag.py \
	mouse_review.py \
	notification_messages.py \
	orca.py \
	orca_console_prefs.py \
	orca_gtkbuilder.py \
	orca_gui_find.py \
	orca_gui_main.py \
	orca_gui_prefs.py \
	orca_gui_profile.py \
	orca_gui_splash.py \
	orca_i18n.py \
	orca_prefs.py \
	orca_quit.py \
	orca_state.py \
	outline.py \
	outloud.py \
	phonnames.py \
	orca_platform.py \
	plugin_manager.py \
	pronunciation_dict.py \
	punctuation_settings.py \
	rolenames.py \
	script.py \
	script_manager.py \
	script_utilities.py \
	settings.py \
	settings_manager.py \
	sound.py \
	speech.py \
	speechdispatcherfactory.py \
	speech_generator.py \
	speechserver.py \
	structural_navigation.py \
	text_attribute_names.py \
	tutorialgenerator.py \
	where_am_I.py

orca_pythondir=$(pyexecdir)/orca

SUBDIRS = \
        scripts \
        backends \
	pluglib \
	baseplugins

ui_DATA = \
	orca-advanced-magnification.ui \
	orca-find.ui \
	orca-mainwin.ui \
	orca-preferences-warning.ui \
	orca-quit.ui \
	orca-setup.ui \
	orca-profile.ui \
	orca-splash.ui

gfx_DATA = \
	orca-splash.png

EXTRA_DIST = \
	$(ui_DATA) \
	$(gfx_DATA)
