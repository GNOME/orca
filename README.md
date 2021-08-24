# Orca v41.rc

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

Orca v41.x is supported on GNOME 41.x only.  We highly suggest you
use the latest releases of GNOME because they contain accessibility
infrastructure and application bug fixes that help Orca work better.

Orca also has the following dependencies:

* Python 3         - Python platform
* pygobject-3.0    - Python bindings for the GObject library
* gtk+-3.0         - GTK+ toolkit
* json-py          - a JSON (<https://json.org/>) reader and writer in Python
* python-speechd   - Python bindings for Speech Dispatcher (optional)
* BrlTTY           - BrlTTY (<https://mielke.cc/brltty/>) support for braille (optional)
* BrlAPI           - BrlAPI support for braille (optional)
* liblouis         - Liblouis (<http://liblouis.org/>) support for contracted braille (optional)
* py-setproctitle  - Python library to set the process title (optional)
* gstreamer-1.0    - GStreamer - Streaming media framework (optional)

You are strongly encouraged to also have the latest stable versions
of AT-SPI2 and ATK for the GNOME 41.x release.


## NOTE FOR BRLTTY USERS:

Orca depends upon the Python bindings for BrlAPI available in BrlTTY v4.5
or better.  You can determine if the Python bindings for BrlAPI are
installed by running the following command:

```sh
python -c "import brlapi"
```

If you get an error, the Python bindings for BrlAPI are not installed.

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

## Scripting Orca

So, you want to write a script for Orca?  The best thing to do is 
start by looking at other scripts under the src/orca/scripts/ hierarchy
of the source tree.