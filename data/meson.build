schema_generator = files('../tools/generate_gsettings_schemas.py')

generated_schema = custom_target(
  'org.gnome.Orca.gschema.xml',
  output: 'org.gnome.Orca.gschema.xml',
  command: [python3, schema_generator, meson.project_source_root() / 'src', '@OUTPUT@'],
  depend_files: [schema_generator, lib_source_files, files('../src/orca/meson.build')],
  install: true,
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
