python_module = import('python')
python = python_module.find_installation('python3', required: false, modules: ['pytest'])

if not python.found()
  subdir_done()
endif

test_env = environment()
test_env.prepend('PYTHONPATH', meson.project_source_root() / 'src')

unit_tests = [
  'unit_tests/test_action_presenter.py',
  'unit_tests/test_ax_collection.py',
  'unit_tests/test_ax_component.py',
  'unit_tests/test_ax_document.py',
  'unit_tests/test_ax_event_synthesizer.py',
  'unit_tests/test_ax_hypertext.py',
  'unit_tests/test_ax_object.py',
  'unit_tests/test_ax_selection.py',
  'unit_tests/test_ax_table.py',
  'unit_tests/test_ax_text.py',
  'unit_tests/test_ax_utilities.py',
  'unit_tests/test_ax_utilities_application.py',
  'unit_tests/test_ax_utilities_debugging.py',
  'unit_tests/test_ax_utilities_event.py',
  'unit_tests/test_ax_utilities_relation.py',
  'unit_tests/test_ax_utilities_role.py',
  'unit_tests/test_ax_utilities_state.py',
  'unit_tests/test_ax_value.py',
  'unit_tests/test_braille_presenter.py',
  'unit_tests/test_bypass_mode_manager.py',
  'unit_tests/test_caret_navigator.py',
  'unit_tests/test_dbus_service.py',
  'unit_tests/test_debugging_tools_manager.py',
  'unit_tests/test_event_manager.py',
  'unit_tests/test_flat_review_presenter.py',
  'unit_tests/test_focus_manager.py',
  'unit_tests/test_input_event_manager.py',
  'unit_tests/test_learn_mode_presenter.py',
  'unit_tests/test_notification_presenter.py',
  'unit_tests/test_object_navigator.py',
  'unit_tests/test_orca_modifier_manager.py',
  'unit_tests/test_say_all_presenter.py',
  'unit_tests/test_script_manager.py',
  'unit_tests/test_sleep_mode_manager.py',
  'unit_tests/test_speech_and_verbosity_manager.py',
  'unit_tests/test_structural_navigator.py',
  'unit_tests/test_system_information_presenter.py',
  'unit_tests/test_typing_echo_presenter.py',
  'unit_tests/test_table_navigator.py',
  'unit_tests/test_where_am_i_presenter.py',
]

foreach test_file : unit_tests
  test_name = test_file.split('/')[-1].split('.')[0]
  test(
    test_name,
    python,
    args: ['-m', 'pytest', files(test_file), '-v'],
    env: test_env,
    suite: 'unit',
    timeout: 30,
  )
endforeach

integration_tests = [
  'integration_tests/test_dbus_with_orca.py',
]

integration_wrapper = configure_file(
  input: 'integration_test_wrapper.py.in',
  output: 'integration_test_wrapper.py',
  configuration: {
    'PYTHON': python.full_path(),
  },
)

foreach test_file : integration_tests
  test_name = test_file.split('/')[-1].split('.')[0]
  test(
    test_name,
    integration_wrapper,
    args: [files(test_file)],
    env: test_env,
    suite: 'integration',
    timeout: 120,
  )
endforeach
