python_module = import('python')
python = python_module.find_installation('python3', required: false, modules: ['pytest', 'pytest_mock'])

if not python.found()
  subdir_done()
endif

test_env = environment()
test_env.prepend('PYTHONPATH', meson.project_source_root() / 'src')
test_env.prepend('PYTHONPATH', meson.project_source_root())
test_env.set('GSETTINGS_BACKEND', 'memory')

unit_tests = [
  'unit_tests/test_action_presenter.py',
  'unit_tests/test_ax_action.py',
  'unit_tests/test_ax_cache_manager.py',
  'unit_tests/test_ax_collection.py',
  'unit_tests/test_ax_component.py',
  'unit_tests/test_ax_document.py',
  'unit_tests/test_ax_device_manager.py',
  'unit_tests/test_ax_event_synthesizer.py',
  'unit_tests/test_ax_hypertext.py',
  'unit_tests/test_ax_utilities_hypertext.py',
  'unit_tests/test_ax_object.py',
  'unit_tests/test_ax_selection.py',
  'unit_tests/test_ax_table.py',
  'unit_tests/test_ax_text.py',
  'unit_tests/test_ax_utilities.py',
  'unit_tests/test_ax_utilities_action.py',
  'unit_tests/test_ax_utilities_component.py',
  'unit_tests/test_ax_utilities_application.py',
  'unit_tests/test_ax_utilities_debugging.py',
  'unit_tests/test_ax_utilities_document.py',
  'unit_tests/test_ax_utilities_event.py',
  'unit_tests/test_ax_utilities_object.py',
  'unit_tests/test_ax_utilities_relation.py',
  'unit_tests/test_ax_utilities_role.py',
  'unit_tests/test_ax_utilities_state.py',
  'unit_tests/test_ax_value.py',
  'unit_tests/test_braille.py',
  'unit_tests/test_braille_presenter.py',
  'unit_tests/test_bypass_mode_manager.py',
  'unit_tests/test_caret_navigator.py',
  'unit_tests/test_chat_presenter.py',
  'unit_tests/test_command_manager.py',
  'unit_tests/test_command_registry.py',
  'unit_tests/test_dbus_service.py',
  'unit_tests/test_debugging_tools_manager.py',
  'unit_tests/test_document_presenter.py',
  'unit_tests/test_event_manager.py',
  'unit_tests/test_extension.py',
  'unit_tests/test_extension_loader.py',
  'unit_tests/test_flat_review_presenter.py',
  'unit_tests/test_focus_manager.py',
  'unit_tests/test_gsettings_registry.py',
  'unit_tests/test_input_event.py',
  'unit_tests/test_input_event_manager.py',
  'unit_tests/test_keybindings.py',
  'unit_tests/test_language_utilities.py',
  'unit_tests/test_learn_mode_presenter.py',
  'unit_tests/test_live_region_presenter.py',
  'unit_tests/test_notification_presenter.py',
  'unit_tests/test_object_navigator.py',
  'unit_tests/test_orca_modifier_manager.py',
  'unit_tests/test_output_reader.py',
  'unit_tests/test_output_recorder.py',
  'unit_tests/test_preferences_documentation_metadata.py',
  'unit_tests/test_preferences_grid_base.py',
  'unit_tests/test_presentation_manager.py',
  'unit_tests/test_pronunciation_dictionary_manager.py',
  'unit_tests/test_profile_manager.py',
  'unit_tests/test_say_all_presenter.py',
  'unit_tests/test_script_manager.py',
  'unit_tests/test_sleep_mode_manager.py',
  'unit_tests/test_sound_presenter.py',
  'unit_tests/test_speech_generator.py',
  'unit_tests/test_speech_manager.py',
  'unit_tests/test_speech_presenter.py',
  'unit_tests/test_spellcheck_presenter.py',
  'unit_tests/test_structural_navigator.py',
  'unit_tests/test_system_information_presenter.py',
  'unit_tests/test_typing_echo_presenter.py',
  'unit_tests/test_table_navigator.py',
  'unit_tests/test_text_attribute_manager.py',
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

orca_integration_tests = [
  'integration_tests/test_dbus_with_orca.py',
  'integration_tests/test_learn_mode.py',
  'integration_tests/test_caret_navigation.py',
  'integration_tests/test_web_mixed_line_heights.py',
  'integration_tests/test_web_navigation.py',
  'integration_tests/test_web_language_switching.py',
  'integration_tests/test_web_table_navigation.py',
  'integration_tests/test_web_table_missing_cells.py',
  'integration_tests/test_web_sortable_table.py',
  'integration_tests/test_web_form_fields.py',
  'integration_tests/test_web_form_fields_navigation.py',
  'integration_tests/test_web_custom_wrappers.py',
  'integration_tests/test_web_landmarks.py',
  'integration_tests/test_web_region_headings.py',
  'integration_tests/test_web_inline_landmarks.py',
  'integration_tests/test_web_inline_list.py',
  'integration_tests/test_web_nested_headings.py',
  'integration_tests/test_web_headings.py',
  'integration_tests/test_web_structural_navigation.py',
  'integration_tests/test_web_field_states.py',
  'integration_tests/test_web_flat_review.py',
  'integration_tests/test_web_flat_review_shrink.py',
  'integration_tests/test_web_label_inference.py',
  'integration_tests/test_web_mode_switching.py',
  'integration_tests/test_web_caret_text_navigation.py',
  'integration_tests/test_web_weird_headings.py',
  'integration_tests/test_web_wrapping_text.py',
  'integration_tests/test_web_wrapped_link.py',
  'integration_tests/test_web_lists.py',
  'integration_tests/test_web_math.py',
  'integration_tests/test_web_sister_projects.py',
  'integration_tests/test_web_sliders.py',
  'integration_tests/test_web_text_attributes.py',
  'integration_tests/test_web_form_state_changes.py',
  'integration_tests/test_web_tree.py',
  'integration_tests/test_web_live_regions.py',
  'integration_tests/test_web_dialogs.py',
  'integration_tests/test_web_aria_spinbutton.py',
  'integration_tests/test_web_autocomplete.py',
  'integration_tests/test_web_dynamic_content.py',
  'integration_tests/test_web_focus_mutations.py',
  'integration_tests/test_web_removed_child_recovery.py',
  'integration_tests/test_web_block_context.py',
  'integration_tests/test_web_caret_context.py',
  'integration_tests/test_web_pain_slider.py',
  'integration_tests/test_web_pain_slider_no_valuenow.py',
  'integration_tests/test_web_cssed_brokenness.py',
  'integration_tests/test_web_line_breaks.py',
  'integration_tests/test_web_page_up_down.py',
  'integration_tests/test_web_same_page_links.py',
  'integration_tests/test_web_image_link.py',
  'integration_tests/test_web_useless_images.py',
  'integration_tests/test_web_redundant_content.py',
  'integration_tests/test_web_offscreen_labels.py',
  'integration_tests/test_web_plain_text.py',
  'integration_tests/test_web_option_removal.py',
  'integration_tests/test_web_editing.py',
  'integration_tests/test_web_editable_embedded.py',
  'integration_tests/test_web_alert.py',
  'integration_tests/test_web_braille_panning.py',
  'integration_tests/test_web_braille_contractions.py',
  'integration_tests/test_web_braille_attribute_mask.py',
  'integration_tests/test_web_braille_selection.py',
  'integration_tests/test_gui_braille_selection.py',
  'integration_tests/test_flat_review_textview.py',
  'integration_tests/test_flat_review_focus_tracking.py',
  'integration_tests/test_flat_review_window_change.py',
  'integration_tests/test_flat_review_move_commands.py',
  'integration_tests/test_flat_review_treeview.py',
  'integration_tests/test_flat_review_commands.py',
  'integration_tests/test_gui_tree_view.py',
  'integration_tests/test_gui_widget_notebook.py',
  'integration_tests/test_gui_spinbutton.py',
  'integration_tests/test_gui_toolbar.py',
  'integration_tests/test_gui_braille_panning.py',
  'integration_tests/test_sleep_mode.py',
  'integration_tests/test_speech_presenter_commands.py',
  'integration_tests/test_braille_presenter_commands.py',
  'integration_tests/test_typing_echo.py',
  'integration_tests/test_terminal.py',
  'integration_tests/test_gtk_text_view_emoji.py',
]

integration_wrapper = configure_file(
  input: 'integration_test_wrapper.py.in',
  output: 'integration_test_wrapper.py',
  configuration: {
    'PYTHON': python.full_path(),
    'prefix': get_option('prefix'),
  },
)

foreach test_file : orca_integration_tests
  test_name = test_file.split('/')[-1].split('.')[0]
  test(
    test_name,
    integration_wrapper,
    args: [files(test_file)],
    env: test_env,
    suite: 'integration',
    timeout: 120,
    is_parallel: false,
  )
endforeach

gsettings_integration_tests = [
  'integration_tests/test_gsettings.py',
]

foreach test_file : gsettings_integration_tests
  test_name = test_file.split('/')[-1].split('.')[0]
  test(
    test_name,
    python,
    args: ['-m', 'pytest', files(test_file), '-v'],
    env: test_env,
    suite: 'integration',
    timeout: 30,
  )
endforeach

# The integration tests are a work in progress; run them with `meson test --suite integration`.
add_test_setup(
  'default',
  is_default: true,
  exclude_suites: ['integration'],
)
