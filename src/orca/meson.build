subdir('backends')
subdir('scripts')

configure_file(
  input: 'orca_bin.py.in',
  output: 'orca',
  configuration: {
    'PYTHON': python3.full_path(),
    'prefix': get_option('prefix'),
    'libdir': python3.get_path('purelib').replace(python3.get_path('data'), get_option('prefix')),
  },
  install: true,
  install_dir: get_option('bindir'),
)

orca_i18n_py = configure_file(
  input: 'orca_i18n.py.in',
  output: '@BASENAME@',
  configuration: {
    'GETTEXT_PACKAGE': meson.project_name(),
    'localedir': get_option('localedir'),
    'prefix': get_option('prefix'),
  }
)

git = find_program('git', required: false)
if git.found()
  r = run_command('git', 'rev-parse', '--short', 'HEAD', check: false)
  revision = r.stdout().strip()
else
  revision = ''
endif

r = run_command('pkg-config', '--variable=tablesdir', 'liblouis', check: false)
louis_tables_dir = r.stdout().strip()

orca_platform_py = configure_file(
  input: 'orca_platform.py.in',
  output: '@BASENAME@',
  configuration: {
    'datadir': get_option('datadir'),
    'prefix': get_option('prefix'),
    'PACKAGE': meson.project_name(),
    'VERSION': meson.project_version(),
    'REVISION': revision,
    'LOUIS_TABLE_DIR': louis_tables_dir,
  }
)

lib_sources = [
  '__init__.py',
  'acss.py',
  'action_presenter.py',
  'ax_collection.py',
  'ax_component.py',
  'ax_document.py',
  'ax_event_synthesizer.py',
  'ax_hypertext.py',
  'ax_object.py',
  'ax_selection.py',
  'ax_table.py',
  'ax_text.py',
  'ax_utilities.py',
  'ax_utilities_application.py',
  'ax_utilities_collection.py',
  'ax_utilities_debugging.py',
  'ax_utilities_event.py',
  'ax_utilities_relation.py',
  'ax_utilities_role.py',
  'ax_utilities_state.py',
  'ax_value.py',
  'bookmarks.py',
  'braille.py',
  'braille_generator.py',
  'braille_presenter.py',
  'braille_rolenames.py',
  'brlmon.py',
  'brltablenames.py',
  'bypass_mode_manager.py',
  'caret_navigator.py',
  'chat.py',
  'clipboard.py',
  'cmdnames.py',
  'colornames.py',
  'dbus_service.py',
  'debug.py',
  'debugging_tools_manager.py',
  'event_manager.py',
  'flat_review.py',
  'flat_review_finder.py',
  'flat_review_presenter.py',
  'focus_manager.py',
  'generator.py',
  'guilabels.py',
  'highlighter.py',
  'input_event.py',
  'input_event_manager.py',
  'keybindings.py',
  'keynames.py',
  'label_inference.py',
  'learn_mode_presenter.py',
  'liveregions.py',
  'mathsymbols.py',
  'messages.py',
  'mouse_review.py',
  'notification_presenter.py',
  'object_navigator.py',
  'object_properties.py',
  'orca.py',
  'orca_gtkbuilder.py',
  'orca_gui_navlist.py',
  'orca_gui_prefs.py',
  'orca_gui_profile.py',
  'orca_modifier_manager.py',
  'phonnames.py',
  'pronunciation_dict.py',
  'say_all_presenter.py',
  'script.py',
  'script_manager.py',
  'script_utilities.py',
  'settings.py',
  'settings_manager.py',
  'sleep_mode_manager.py',
  'sound.py',
  'sound_generator.py',
  'speech_and_verbosity_manager.py',
  'speech.py',
  'spellcheck.py',
  'speechdispatcherfactory.py',
  'speech_generator.py',
  'speechserver.py',
  'spiel.py',
  'ssml.py',
  'structural_navigator.py',
  'systemd.py',
  'system_information_presenter.py',
  'table_navigator.py',
  'text_attribute_names.py',
  'typing_echo_presenter.py',
  'where_am_i_presenter.py',
]

ui_sources = [
  'orca-setup.ui',
]

python3.install_sources(
  [ lib_sources, orca_i18n_py, orca_platform_py ],
  subdir: meson.project_name())

install_data(
  ui_sources,
  install_dir: get_option('datadir') / meson.project_name() / 'ui'
)
