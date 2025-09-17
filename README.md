# Orca v50.alpha

[TOC]

## Attention Application Developers

If you are an application developer trying to make your application work with Orca, please see the
[README for application developers](README-APPLICATION-DEVELOPERS.md).

## Introduction

Orca is a free, open source, flexible, and extensible screen reader
that provides access to the graphical desktop via user-customizable
combinations of speech and/or braille.

Orca works with applications and toolkits that support the assistive
technology service provider interface (AT-SPI), which is the primary
assistive technology infrastructure for the Solaris and Linux
operating environments.  Applications and toolkits supporting the
AT-SPI include the GNOME GTK+ toolkit, the Java platform's Swing
toolkit, OpenOffice/LibreOffice, Gecko, and WebKitGtk.  AT-SPI support
for the KDE Qt toolkit is currently being pursued.

See also <https://orca.gnome.org> for detailed information on Orca,
including how to run Orca, how to communicate with the Orca user
community, and where to log bugs and feature requests.

## Dependencies

Orca v50.x is supported on GNOME 50.x only.  We highly suggest you
use the latest releases of GNOME because they contain accessibility
infrastructure and application bug fixes that help Orca work better.

Orca also has the following dependencies:

* meson            - The build system used by Orca
* Python 3         - Python platform
* pygobject-3.0    - Python bindings for the GObject library
* gtk+-3.0         - GTK+ toolkit
* python3-dasbus   - Dasbus (<https://dasbus.readthedocs.io/>) support for remote control of Orca
* python-speechd   - Python bindings for Speech Dispatcher (optional)
* BrlTTY           - BrlTTY (<https://mielke.cc/brltty/>) support for braille (optional)
* BrlAPI           - BrlAPI support for braille (optional)
* liblouis         - Liblouis (<https://liblouis.io/>) support for contracted braille (optional)
* py-setproctitle  - Python library to set the process title (optional)
* gstreamer-1.0    - GStreamer - Streaming media framework (optional)
* python3-psutil   - Process and system utilities (optional)
* libwnck3         - Used for mouse review (optional)

You are strongly encouraged to also have the latest stable versions
of AT-SPI2 and ATK for the GNOME 50.x release.

## Note for Braille Users

Orca depends upon the Python bindings for BrlAPI available in BrlTTY v4.5
or better.  You can determine if the Python bindings for BrlAPI are
installed by running the following command:

```sh
python -c "import brlapi"
```

If you get an error, the Python bindings for BrlAPI are not installed.

## Building and Installing Orca

If you want to build Orca in a directory called `_build` and install Orca using
your distro's default location (e.g `/usr/local`):

```sh
meson setup _build
meson compile -C _build
meson install -C _build
```

The installer will prompt you for `sudo` permission if needed.

To specify an alternative install location, use `-D prefix=` during setup
(e.g. `meson setup -D prefix=$HOME/orca-test _build`).

To rebuild, either remove the build directory you created before (e.g. `_build`)
or add the `--reconfigure` flag to the end of your existing `meson setup` command.

To uninstall, `cd` into the build directory you created and use `ninja uninstall`,
or `sudo ninja uninstall` if you had installed Orca with `sudo` permission.
Note that this will not remove the bytecode files in `__pycache__`. See this
[meson issue](https://github.com/mesonbuild/meson/issues/12798).

## Running Orca

If you wish to modify your Orca preferences, you can press "Insert+space"
while Orca is running.

To get help while running Orca, press "Insert+H".  This will enable
"learn mode", which provides a spoken and brailled description of what
various keyboard and braille input device actions will do.  To exit
learn mode, press "Escape."  Finally, the preferences dialog contains
a "Key Bindings" tab that lists the keyboard binding for Orca.

For more information, see the Orca documentation which is available
within Orca as well as at <https://gnome.pages.gitlab.gnome.org/orca/help>.

## Orca's Scripts and Features

Orca's scripts provide access to applications and toolkits by responding to
accessible events. For instance, when focus changes in an application, that
application will emit an accessible event, `object:state-changed:focused`,
which is then handled by the script associated with the application or toolkit.

If you have an application or toolkit that is accessible, but poorly supported
by Orca, writing a custom script for that application might be the correct
solution. (The correct solution might instead be to fix a bug in Orca and/or the
application.) To see examples of scripts, look in `src/orca/scripts` of the
source tree.

Scripts can also import features, but the features themselves should not live
inside the script. Some examples of features imported by scripts include:

* `src/orca/system_information_presenter.py`
* `src/orca/flat_review_presenter.py`
* `src/orca/notification_presenter.py`
* `src/orca/object_navigator.py`

Please note: Historically features were implemented directly inside the scripts.
Moving features outside of scripts is still a work in progress. Thus if you're
wondering why some features are inside `src/orca/scripts/default.py` and others
are not, the answer is that we haven't yet gotten around to migrating the features
outside of `default.py`.

## Experimental Features

### Remote Controller (D-Bus Interface)

**New in Orca v49.0:** Orca now provides a D-Bus interface that allows external applications
to remotely control Orca's functionality and present messages to users. This feature is
currently experimental. For detailed usage instructions, examples, and API documentation, see
[README-REMOTE-CONTROLLER.md](README-REMOTE-CONTROLLER.md).

### Spiel Text-to-Speech Support

By default, Orca uses speech-dispatcher for its TTS support. In addition, there is
basic support for [Spiel](https://github.com/project-spiel) which allows choosing
voices from multiple synthesizers, currently including eSpeak and Piper.

To test Spiel, configure Orca to build from the latest source. Once compiled,
`meson devenv` will be used to run Orca.

```sh
meson setup --force-fallback-for=spiel -Dspiel=true _build
meson compile -C _build
meson install -C _build
```

If you have an existing build directory, don't forget to use `--reconfigure`. If
you have problems after an update, you may need to re-build and re-install:

```sh
meson subprojects purge --confirm
meson setup --reconfigure --force-fallback-for=spiel -Dspiel=true _build 
meson compile --clean -C _build
meson install -C _build

# Ensure any old Spiel providers get restarted
flatpak kill ai.piper.Speech.Provider
flatpak kill org.espeak.Speech.Provider
```

Then install the Flatpak for one or more speech providers (i.e. piper or speak) by running the
commands in the [Spiel documentation](https://project-spiel.org/install.html)

To switch from Speech Dispatcher to Spiel, use `orca --replace --speech-system=spiel`. Using
this flag is highly recommended while Orca's Spiel support is experimental. If you would like
to use Spiel by default, you can select it in Orca's Preferences dialog. To then switch back
to Speech Dispatcher, use `orca --replace --speech-system=speechdispatcherfactory`.

```sh
# Enter the development environment
meson devenv -C _build

# Run Orca
orca --replace --speech-system=spiel

# Exit the development environment
exit
```

### Building Spiel from Source

For advanced users, Spiel and providers may be built from source. If you are
unsure, consider using the available Flatpaks and consult the documentation for
your distribution before proceeding.

1. Build and install Orca with Spiel

   Be sure to build Orca as described above, so the correct `libspeechprovider`
   version is available when building a provider in the next step. If you
   previously built Orca, follow the steps to update and re-build before
   continuing.

2. Next build and install a provider

   ```sh
   # Clone the repository, then select a provider in the "providers/" directory
   git clone https://github.com/eeejay/spiel-demos.git
   cd spiel-demos/providers/espeak

   # Build and install
   meson setup _build
   meson compile -C _build
   meson install -C _build
   ```

Now start Orca following the [instructions](#spiel-text-to-speech-support) above and
the Spiel providers you installed will start automatically.
