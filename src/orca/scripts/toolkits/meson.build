subdir('Chromium')
subdir('clutter')
subdir('Gecko')
subdir('gtk')
subdir('J2SE-access-bridge')
subdir('Qt')
subdir('WebKitGtk')

lib_sources = [
  '__init__.py',
  'VCL.py',
]

python3.install_sources(
  lib_sources,
  subdir: meson.project_name() / 'scripts' / 'toolkits'
)
