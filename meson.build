project('orca',
  version: '46.beta',
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
dependency_atspi = dependency('atspi-2', version: '>= 2.50.0')
dependency_atkbridge = dependency('atk-bridge-2.0', version: '>= 2.50.0')
dependency_pygobject = dependency('pygobject-3.0', version: '>= 3.18')

# FIXME: Re-enable this check. It works just fine in (at least) Fedora,
# but fails in the SUSE CI bot.
# dependency_gtk = dependency('gtk+-3.0', version: '>= 3.24')

# Optional python modules with their descriptions
optional_modules = {
  'brlapi': 'braille output',
  'louis': 'contracted braille',
  'speechd': 'speech output',
  'psutil': 'system information commands',
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

subdir('docs')
subdir('help')
subdir('icons')
subdir('po')
subdir('src')

summary(summary)
