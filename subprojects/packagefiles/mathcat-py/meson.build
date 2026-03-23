project('mathcat-py', 'c',
  version: '0.7.6',
  meson_version: '>= 1.0.0',
)

python = import('python')
cargo = find_program('cargo', required: true)
cp = find_program('cp')

source_dir = meson.current_source_dir()
cargo_target_dir = meson.current_build_dir() / 'cargo-target'

mathcat_so = 'libmathcat_py.so'
cargo_output = cargo_target_dir / 'release' / 'lib' + mathcat_so

# If the rustc version has changed since the last build, clean the cargo
# cache to avoid "compiled by an incompatible version" errors.
rustc_version_check = 'RUSTC_VER=$(' + cargo.full_path() + ' rustc -- --version 2>/dev/null || echo unknown);' + \
  ' STORED_VER=$(cat ' + cargo_target_dir / '.rustc_version' + ' 2>/dev/null || echo none);' + \
  ' if [ "$RUSTC_VER" != "$STORED_VER" ]; then rm -rf ' + cargo_target_dir + '; fi'

store_rustc_version = 'mkdir -p ' + cargo_target_dir + \
  ' && ' + cargo.full_path() + ' rustc -- --version > ' + cargo_target_dir / '.rustc_version' + ' 2>/dev/null || true'

mathcat_lib = custom_target('libmathcat_py',
  output: mathcat_so,
  command: [
    'sh', '-c',
    'echo "Building MathCAT Python bindings (this may take a while)..." &&' +
    rustc_version_check +
    ' && ' +
    cargo.full_path() + ' build --release' +
    ' --manifest-path ' + source_dir / 'Cargo.toml' +
    ' --target-dir ' + cargo_target_dir +
    ' && ' +
    store_rustc_version +
    ' && ' +
    cp.full_path() + ' ' + cargo_output + ' @OUTPUT@',
  ],
  build_by_default: true,
  install: true,
  install_dir: python.find_installation('python3').get_install_dir() / 'orca',
)

# Rules are extracted by build.rs to addon/globalPlugins/MathCAT/Rules.
# Install them and delete the nested .zip files that MathCAT can't handle
# in read-only system directories.
rules_source = source_dir / 'addon' / 'globalPlugins' / 'MathCAT' / 'Rules'
mathcat_rules_install_dir = get_option('datadir') / 'mathcat' / 'Rules'

install_emptydir(mathcat_rules_install_dir)

meson.add_install_script(
  'sh', '-c',
  'cp -r ' + rules_source / '*' + ' "$DESTDIR$MESON_INSTALL_PREFIX/' + mathcat_rules_install_dir + '/"',
)

mathcat_py_dep = declare_dependency()
