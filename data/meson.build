schema_generator = files('../tools/generate_gsettings_schemas.py')

# Source files with @gsettings_schema decorators. For meson dependency tracking only;
# the Python script discovers schemas by scanning src/orca/*.py at build time.
schema_sources = files(
  '../src/orca/speech_manager.py',
  '../src/orca/speech_presenter.py',
  '../src/orca/braille_presenter.py',
  '../src/orca/typing_echo_presenter.py',
  '../src/orca/caret_navigator.py',
  '../src/orca/structural_navigator.py',
  '../src/orca/table_navigator.py',
  '../src/orca/document_presenter.py',
  '../src/orca/say_all_presenter.py',
  '../src/orca/flat_review_presenter.py',
  '../src/orca/sound_presenter.py',
  '../src/orca/chat_presenter.py',
  '../src/orca/spellcheck_presenter.py',
  '../src/orca/mouse_review.py',
  '../src/orca/live_region_presenter.py',
  '../src/orca/system_information_presenter.py',
  '../src/orca/pronunciation_dictionary_manager.py',
  '../src/orca/command_manager.py',
  '../src/orca/text_attribute_manager.py',
)

generated_schema = custom_target(
  'org.gnome.Orca.gschema.xml',
  output: 'org.gnome.Orca.gschema.xml',
  command: [python3, schema_generator, meson.project_source_root() / 'src', '@OUTPUT@'],
  depend_files: [schema_generator, schema_sources],
  install: false,
  install_dir: get_option('datadir') / 'glib-2.0' / 'schemas'
)

glib_compile_schemas = find_program('glib-compile-schemas', required: false)
if glib_compile_schemas.found()
  validate_schemas_cmd = '; '.join([
    'import pathlib, subprocess, sys',
    'subprocess.check_call([sys.argv[1], "--strict", "--dry-run", sys.argv[2]])',
    'pathlib.Path(sys.argv[3]).write_text("ok")',
  ])
  test(
    'validate-schemas',
    glib_compile_schemas,
    args: ['--strict', '--dry-run', meson.current_build_dir()],
    depends: generated_schema,
  )
  custom_target(
    'validate-schemas-build',
    output: 'schemas.validated',
    command: [
      python3,
      '-c',
      validate_schemas_cmd,
      glib_compile_schemas,
      meson.current_build_dir(),
      '@OUTPUT@',
    ],
    depends: generated_schema,
    build_by_default: true,
  )
endif
