project('orca',
  version: '50.alpha',
  meson_version: '>= 1.0.0',
)

python = import('python')
gnome = import('gnome')
i18n = import('i18n')

python_minimum_version = '3.10'
python3 = python.find_installation('python3', required: true)
if not python3.language_version().version_compare(f'>= @python_minimum_version@')
  error(f'Python @python_minimum_version@ or newer is required.')
endif

# Hard dependencies (checked via pkg-config)
dependency('atspi-2', version: '>= 2.56.0')
dependency('atk-bridge-2.0', version: '>= 2.56.0')
dependency('pygobject-3.0', version: '>= 3.18')

# Hard Python module dependencies
dasbus_result = python.find_installation('python3', modules:['dasbus'], required: false)
if not dasbus_result.found()
  error('dasbus is required for D-Bus remote controller interface')
endif

# End users might not have the Gtk development libraries installed, making pkg-config fail.
# Therefore, check this dependency via python.
gtk_major_version = '3'
gtk_minor_version = '24'
gtk_command = ' '.join([
  'import gi; gi.require_version("Gtk", "3.0"); from gi.repository import Gtk;',
  'print(f"{Gtk.get_major_version()}.{Gtk.get_minor_version()}.{Gtk.get_micro_version()}");',
  f'failed = Gtk.get_major_version() != @gtk_major_version@ or Gtk.get_minor_version() < @gtk_minor_version@;',
  'exit(failed)'
])
gtk_test = run_command(python3, '-c', gtk_command, check: false)
description = f'GTK @gtk_major_version@.@gtk_minor_version@'
version = gtk_test.stdout().strip()
if gtk_test.returncode() != 0
  error(f'@description@ failed (found @version@)')
endif

# Optional python modules with their descriptions
optional_modules = {
  'brlapi': 'braille output',
  'louis': 'contracted braille',
  'psutil': 'system information commands',
  'gi.repository.Wnck': 'mouse review',
}

summary = {}
foreach module, description : optional_modules
  result = python.find_installation('python3', modules:[module], required: false)
  if result.found()
    summary += {description: f'yes (found @module@)'}
  else
    summary += {description: f'no (missing @module@)'}
  endif
endforeach

# Optional synthesizer services
speech_output = []
if python.find_installation('python3', modules:['speechd'], required: false).found()
  speech_output += ['speechd']
endif

# Experimental (checked via pkg-config)
if get_option('spiel')
  dependency('spiel-1.0',
            version: '>= 1.0.1',
           fallback: ['spiel', 'spiel_lib_dep'],
    default_options: [
      'docs=false',
      'tests=false',
      'werror=false',
    ],
  )
  speech_output += ['spiel']
endif

if speech_output.length() > 0
  summary += {'speech output': 'yes (found @0@)'.format(', '.join(speech_output))}
else
  summary += {'speech output': 'no (missing speechd, spiel)'}
endif

# Integration with session startup
systemd = dependency('systemd', required: false)
systemd_user_unit_dir = systemd.get_variable(
    'systemd_user_unit_dir',
    pkgconfig_define: ['prefix', get_option('prefix')],
    default_value: get_option('prefix') / 'lib' / 'systemd' / 'user'
)
install_data(
    'orca.service',
    install_dir: systemd_user_unit_dir
)
i18n.merge_file(
  input: 'orca-autostart.desktop.in',
  output: '@BASENAME@',
  type: 'desktop',
  po_dir: meson.project_source_root() / 'po',
  install: true,
  install_dir: get_option('sysconfdir') / 'xdg' / 'autostart',
)

gnome.post_install(
  gtk_update_icon_cache: true,
)

summary += {'Install dir': python.find_installation('python3').get_install_dir()}

subdir('docs')
subdir('help')
subdir('icons')
subdir('po')
subdir('src')
subdir('tests')

summary(summary)

# This may be removed once Spiel is widely available
if get_option('force_fallback_for').contains('spiel')
  warning('Spiel is being built as a subproject that may need to be updated.\n\n' +
          '    See the README.md in this directory or in the Orca repository at:\n' +
          '    https://gitlab.gnome.org/GNOME/orca/blob/main/README.md#experimental-features\n')
endif
