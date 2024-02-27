# Orca v47.alpha

[TOC]

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

See also <http://wiki.gnome.org/Projects/Orca> for detailed information
on Orca, including how to run Orca, how to communicate with the Orca user
community, and where to log bugs and feature requests.

## Dependencies

Orca v47.x is supported on GNOME 47.x only.  We highly suggest you
use the latest releases of GNOME because they contain accessibility
infrastructure and application bug fixes that help Orca work better.

Orca also has the following dependencies:

* meson            - The build system used by Orca
* Python 3         - Python platform
* pygobject-3.0    - Python bindings for the GObject library
* gtk+-3.0         - GTK+ toolkit
* json-py          - a JSON (<https://json.org/>) reader and writer in Python
* python-speechd   - Python bindings for Speech Dispatcher (optional)
* BrlTTY           - BrlTTY (<https://mielke.cc/brltty/>) support for braille (optional)
* BrlAPI           - BrlAPI support for braille (optional)
* liblouis         - Liblouis (<https://liblouis.io/>) support for contracted braille (optional)
* py-setproctitle  - Python library to set the process title (optional)
* gstreamer-1.0    - GStreamer - Streaming media framework (optional)
* python3-psutil   - Process and system utilities (optional)
* libwnck3         - Used for mouse review (optional)

You are strongly encouraged to also have the latest stable versions
of AT-SPI2 and ATK for the GNOME 47.x release.

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
within Orca as well as at: <https://help.gnome.org/users/orca/stable/>

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

* `src/orca/data_and_time_presenter.py`
* `src/orca/flat_review_presenter.py`
* `src/orca/notification-presenter.py`
* `src/orca/object_navigator.py`

Please note: Historically features were implemented directly inside the scripts.
Moving features outside of scripts is still a work in progress. Thus if you're
wondering why some features are inside `src/orca/scripts/default.py` and others
are not, the answer is that we haven't yet gotten around to migrating the features
outside of `default.py`.

## Getting Orca to Speak Your Application's Custom Message

AT-SPI2 v2.46 added support for the `announcement` signal which can be used with
Orca v45.2 and later. Here's a simple example:

```python
#!/usr/bin/python3

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

def on_button_clicked(button):
    button.get_accessible().emit("announcement", "Hello world. I am an announcement.")

def on_activate(application):
    window = Gtk.ApplicationWindow(application=application)
    button = Gtk.Button(label="Make an announcement")
    button.connect("clicked", on_button_clicked)
    window.add(button)
    window.show_all()

app = Gtk.Application()
app.connect("activate", on_activate)
app.run(None)
```

If you are running Orca v45.2 or later, launch the sample application above and press the
"Make an announcement" button. You should hear Orca say "Hello world. I am an announcement."

Beginning with AT-SPI2 v2.50, the `announcement` signal was deprecated in favor of a new
`notification` signal to provide native applications similar functionality to ARIA's live
regions which allow web applications to specify that a notification is urgent/"assertive."

Here is an example of using the `notification` signal:

```python
#!/usr/bin/python3

import gi
gi.require_version("Atk", "1.0")
gi.require_version("Gtk", "3.0")

from gi.repository import Atk, Gtk

def on_button_clicked(button):
    button.get_accessible().emit("notification", "Hello world. I am a notification.", Atk.Live.POLITE)

def on_activate(application):
    window = Gtk.ApplicationWindow(application=application)
    button = Gtk.Button(label="Make a notification")
    button.connect("clicked", on_button_clicked)
    window.add(button)
    window.show_all()

app = Gtk.Application()
app.connect("activate", on_activate)
app.run(None)
```

You can fire the announcement signal in GTK 4 starting from 4.14 as well:

```python
#!/usr/bin/python3

import gi
gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

def on_button_clicked(button):
    button.announce("Hello world. I am a notification.", Gtk.AccessibleAnnouncementPriority.MEDIUM)

def on_activate(application):
    window = Gtk.ApplicationWindow(application=application)
    button = Gtk.Button(label="Make a notification")
    button.connect("clicked", on_button_clicked)
    window.set_child(button)
    window.present()

app = Gtk.Application()
app.connect("activate", on_activate)
app.run(None)
```

Note that in older GTK 4 releases there is no way how to do this, as you can't emit raw AT-SPI2 events, or do similar platform-specific things.

**Please note:** Because "assertive" messages can be disruptive if presented at the wrong
time, Orca *currently* treats an "assertive" notification from non-web applications the
same as a regular/"polite" notification. Adding support for "assertive" notifications from non-web
applications is planned and depends on Orca's
[live-region support being made global](https://gitlab.gnome.org/GNOME/orca/-/issues/431)
so that users have full control over when and how notifications are presented to them.

## Experimental Features

By default, Orca uses speech-dispatcher for its TTS support. In addition, there is
basic support for [Spiel](https://github.com/eeejay/spiel) which allows choosing
voices from multiple synthesizers, currently including eSpeak and Piper.

To test Spiel, configure Orca to build from the latest source. Once compiled,
`meson devenv` will be used to run Orca.

```
meson setup --force-fallback-for=spiel -Dspiel=true _build
meson compile -C _build
meson install -C _build
```

If you have existing build directory, don't forget to use `--reconfigure`. If
you have problems after an update, you may need to update and re-install:

```
meson subprojects update
meson setup --reconfigure --force-fallback-for=spiel -Dspiel=true _build 
meson compile --clean -C _build
meson install -C _build

# Ensure any old Spiel providers get restarted
flatpak kill ai.piper.Speech.Provider
flatpak kill org.espeak.Speech.Provider
```

Then install the Flatpak for one or more providers:

* [eSpeak](https://eeejay.github.io/spiel-demos/espeak.flatpakref)
* [Piper](https://eeejay.github.io/spiel-demos/piper.flatpakref)

To switch from Speech Dispatcher to Spiel, use `orca --replace --speech-system=spiel`. Using
this flag is highly recommended while Orca's Spiel support is experimental. If you would like
to use Spiel by default, you can select it in Orca's Preferences dialog. To then switch back
to Speech Dispatcher, use `orca --replace --speech-system=speechdispatcherfactory`.

```
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

Now start Orca following the [instructions](#experimental-features) above and
the Spiel providers you installed will start automatically.

