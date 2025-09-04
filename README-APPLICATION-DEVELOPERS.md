# Tips for Application Developers

[TOC]

## Introduction

Please note: This document is a work in progress and will be expanded over time to include details
about what Orca expects from applications. In the meantime, it contains tips based on frequently-asked
questions. We hope you find them useful.

## A Request

If Orca is not presenting your application in the way you think it should, and the techniques in
this document do not apply, please file a bug against Orca so we can determine where the fix belongs.
It might be an Orca bug which we can fix for you. Otherwise, we can help you address it in your
application and update this document accordingly.

## Accessible Events

Orca has many commands and modes which make it possible for users to interact with your application.
However, the most basic need for applications is presentation of changes in location, such as focus
changes and navigation within text. In order for Orca to present such changes, it must be notified
via one or more accessible events. Unless you have created a custom widget, you should expect that
accessible events will be fired by your application's toolkit.

Examples of accessible events include:

* `window:activate` tells Orca that the user is in a different window. When the active window
  changes, Orca will announce the new window. Orca also keeps track of the active window in order
  to filter many accessibility events which get fired by apps other than the one currently
  being used.
* `object:state-changed:focused` tells Orca that the user has moved to a different widget. Orca
  presents newly-focused widgets. Orca also keeps track of the focused widget in order to filter
  out some accessibility events. As an example, the `object:state-changed:checked` event tells Orca
  that the `checked` state of a checkbox-like widget has changed. That change is likely not of
  interest to the user if that widget is not focused. Therefore Orca will present that change only
  if the widget emitting it is focused.
* `object:text-caret-moved` tells Orca that the user has moved to a different location in a text
  widget or document. Assuming the event is fired from the active object (focused text field or
  current document), Orca will present the new character, word, or line in response, using some
  heuristics to determine what unit of text should be presented.

If you are interested in seeing what accessible events your application is firing, you can use
[Accerciser](https://gitlab.gnome.org/GNOME/accerciser)'s event monitor.

## What Orca Presents In Response To Location Changes

### As a General Rule

When an accessible event informs Orca that the object of interest, or the user's location therein,
has changed, Orca will generally present two things:

1. The new ancestors of the object of interest, if any
2. The object of interest, or the new location, and any role-specific relevant details

For instance if the user tabs into a group of checkboxes labelled "Permissions" and lands on the
unchecked "Allow access to microphone" checkbox, Orca will say:

* "Permissions panel"
* "Allow access to microphone checkbox. Not checked."

If the user then tabs to another widget in the "Permissions" group, Orca will only present that
widget and will not repeat "Permissions."

What Orca presents for any given object depends on the role of that object. However, for UI
components, Orca will always present the accessible name and, by default, the accessible
description. (The latter can be disabled by the user either globally or on a per-app basis,
though it is always available on demand via Orca's "Where Am I?" command.)

### Presentation of "Selected"/"Not selected" in UI

In most groups of selectable items, selection follows focus. In other words, arrowing to an item
causes it to become both focused and selected. In these instances, Orca deliberately does not say
"selected" because that is the expected state, and most users dislike "chattiness." However, Orca
should announce "not selected" when the user navigates to a selectable item that did not become
selected as a result of navigation. This presentation can be seen by using Ctrl+Arrow in Caja to
move among items without selecting them.

The way Orca determines that "not selected" should be announced is by finding the "selectable"
accessible state present and the "selected" state absent on the item which just claimed focus.
If the "selectable" state is absent, Orca will not say "not selected" because doing so makes no sense
on an object which is not selectable.

Orca should also announce when the selected state of the focused item subsequently changes. For
instance, after using Ctrl+Arrow to move to an item without selecting it, one can use Ctrl+Space to
toggle that item's selected state. When it becomes selected, Orca will say "selected". When it
becomes unselected, Orca will say "unselected".

What causes Orca to make this announcement is an `object:state-changed:selected` event being fired
by the item whose state changed. If the event is not fired, Orca will be unaware that the state
changed and remain silent in response. For standard toolkit widgets, using the toolkit's API to
toggle the selection should cause the accessible state to be updated and the accessible event to
be fired. If that is not the case, there may be a toolkit bug. For custom widgets, it is likely that
you will need to make these updates within your application.

### Status Bars and Focusable List Items

There are a couple of instances in which Orca will also include the descendants of a UI
component in the presentation of that component:

1. Status bars. Because status bars are normally not focusable, Orca provides a
["Where Am I?" command](https://gnome.pages.gitlab.gnome.org/orca/help/commands_where_am_i.html)
to speak the contents of the status bar.
2. Focusable list items. GTK `ListItem`s containing multiple descendants are becoming increasingly
common in applications. Some application developers have stated that Orca should automatically present
all of the displayed information inside a `ListItem` when it becomes focused. This change was made
in Orca v47.

Because some application developers use the accessible name as a means to make Orca present the
full contents of the list item, Orca has filtering which attempts to eliminate presentation of
descendants whose contents are in reflected in the name. Since the release of Orca v47, it was
discovered that this filtering is insufficient for some applications. It is being increased in
Orca v47.2. However, we recommend that application developers do not expose the full contents of
a focusable list item in that item's accessible name, and to file a bug if Orca fails to present
the list item correctly.

### Tables

When a user navigates among rows in a table/grid, sometimes the full row should be presented;
other times just the current cell/item. It can be difficult to programmatically determine which
makes sense for any given application. In addition, user needs and preferences vary. For these
reasons, the amount Orca reads when arrowing up or down in a container with the accessible `table`
role is a [user-configurable option](https://gnome.pages.gitlab.gnome.org/orca/help/preferences_speech.html)
which can be set on a [per-application basis](https://gnome.pages.gitlab.gnome.org/orca/help/preferences_introduction.html)
and customized by the type of table (GUI, spreadsheet, and document).

## Speaking Your Application's Non-Focusable Static Text

### Technique: Use An Accessible Description

If your application has static, on-screen text of an explanatory nature and you do not want to make
that text focusable, it is still possible to have Orca present it automatically using the accessible
`description` property or the `described-by` relationship.

Examples:

* If the focused object is a search input, and the text to be presented is "*n* matches found",
  set "*n* matches found" as the accessible description of the search input and update that
  description each time the count changes. In response, the toolkit should fire an
  `object:property-change:accessible-description` event which Orca will handle by presenting the
  new description.

* If there is an on-screen message associated with a group of widgets, set the accessible description
  of that group to the on-screen message. As stated in the previous section, Orca will present the
  name and description of new ancestors prior to presenting the focused object.

When using this technique, keep in mind that the description is the last thing presented for any
object. Taking the "Permissions" group example from the previous section, that means Orca will say:

* "Permissions panel", followed by the description of that group
* "Allow access to microphone checkbox. Not checked.", followed by the description of the checkbox

If the static text should not be presented last, a different technique might be advisable.

**Note:** Orca v47.alpha or later is required to have Orca present the accessible description, and
any changes to that description, on *ancestors* of the object of interest. In Orca v46 and earlier,
Orca only presents the name of ancestors and description changes on the object of interest.

### Can I Use Details/Details-For And Error-Message/Error-For Relations?

The `details`/`details-for` and `error-message`/`error-for` relation types were created for ARIA,
and there was no indication that they might be of interest to developers of native applications.
As a result, support in Orca for these new relation types had been implemented only for web apps.

Orca v49 has global support for `error-message`/`error-for`. Global support for `details`/`details-for`
is still pending. See [issue #514](https://gitlab.gnome.org/GNOME/orca/-/issues/514).

### Why Is Orca Speaking My Labels As Static Text?

Using the accessible `description` property to get screen readers to automatically announce text in
a newly-shown dialog originated as a web-browser practice, e.g. for alerts. Historically, application
developers simply used toolkit labels, e.g. `GtkLabel`, to add static text. And those developers,
and Orca users, expected Orca to read that text automatically.

In order to distinguish static text labels from widget labels, Orca checks the accessible relations
of the label. If it finds any relation, Orca assumes the label is NOT static text. Otherwise Orca
applies some additional heuristics to filter out false positives. But in the end, Orca may conclude
incorrectly that the unrelated label is indeed static text which should be read automatically.

While less than ideal, keeping this functionality in place is important, because there are *many*
applications that do not use the new `description` approach and likely will not be updated to do so.
Breaking the user experience in all of those apps would be bad. However, **it's easy to ensure Orca
doesn't mistakenly treat your labels as static text to be read automatically:**

* Orca v47.alpha and later prefers the `description` as the source of static text. If your app
  uses that technique, Orca will not search for unrelated labels to present.
* Any label that is not static text should have the accessible `label-for` relationship pointing to
  the widget it labels. That will prevent all versions of Orca from concluding it is static text
  that should be automatically presented.

## Speaking Your Application's Custom Message/Announcement

AT-SPI2/ATK v2.46 added an `announcement` signal which can be used with Orca v45.2 and later.
Simple examples are provided below.

### Announcement Example: GTK 3

```python
#!/usr/bin/python

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

Beginning with ATK v2.50, the `announcement` signal was deprecated in favor of a new
`notification` signal to provide native applications similar functionality to ARIA's live
regions which allow web applications to specify that a notification is urgent/"assertive."

Here is an example of using the `notification` signal:

```python
#!/usr/bin/python

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

### Announcement Example: GTK 4 (Minimum Version: 4.14)

```python
#!/usr/bin/python

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

Note that in older GTK 4 releases there is no way how to do this, as you can't emit raw AT-SPI2
events, or do similar platform-specific things.

### Announcement Example: Qt 6 (Minimum Version: 6.8)

```python
#!/usr/bin/python

import sys
from PySide6.QtCore import Slot
from PySide6.QtGui import QAccessible, QAccessibleAnnouncementEvent
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton

@Slot()
def on_button_clicked(checked):
    announcement_event = QAccessibleAnnouncementEvent(button, "Hello world. I am a notification.")
    # prio could be set like this (Polite is the default anyway)
    announcement_event.setPoliteness(QAccessible.AnnouncementPoliteness.Polite)
    QAccessible.updateAccessibility(announcement_event)

app = QApplication(sys.argv)
main_window = QMainWindow()
button = QPushButton("Make a notification", main_window)
button.resize(200, 50)
button.clicked.connect(on_button_clicked)

main_window.show()
app.exec()
```

### Announcement Example: Headless Application using Dasbus for DBus Communication

In an application without a GUI, you can pretend to be enough of an accessible object to fire this
event as well. To hear the result, Orca must be running first, though.

```python
#!/usr/bin/python3
from dasbus.connection import SessionMessageBus, AddressedMessageBus
from dasbus.loop import EventLoop
from dasbus.server.interface import dbus_class, dbus_interface, dbus_signal
from dasbus.typing import Int32, UInt32, Variant, Structure, Dict, List, Tuple, ObjPath, get_variant
import threading
import time

ANNOUNCER_PATH = "/com/example/Announcer"

@dbus_interface("org.a11y.atspi.Application")
class Application:
    """A minimal accessible application to fulfill AT-SPI2's expectations that events come from a
    valid accessible application."""

    @property
    def ToolkitName(self) -> str:
        return "Announcer"

@dbus_interface("org.a11y.atspi.Event.Object")
class ObjectEvents:
    """Just a holder for the one needed signal."""

    @dbus_signal
    def Announcement(self, subtype: str, detail1: int, detail2: int, value: Variant, props: Structure):
        pass

@dbus_interface("org.a11y.atspi.Accessible")
class Accessible:
    """A minimal accessible object to fulfill AT-SPI2's expectations that events come from a valid
    accessible object."""

    def GetState(self) -> list[UInt32]:
        return [1<<25, 0] # ATSPI_STATE_SHOWING

    @property
    def Name(self) -> str:
        return "Announcer"

    @property
    def Parent(self) -> Tuple[str, ObjPath]:
        return "", ObjPath("/org/a11y/atspi/null")

    def GetRole(self) -> UInt32:
        return 75 # ATSPI_ROLE_APPLICATION

    def GetAttributes(self) -> Dict[str, str]:
        return {}

@dbus_class
class Announcer(Accessible, Application, ObjectEvents):
    pass

CacheEntry = Tuple[Tuple[str, ObjPath], Tuple[str, ObjPath], Tuple[str, ObjPath], Int32, Int32, List[str], str, UInt32, str, List[UInt32]]

@dbus_interface("org.a11y.atspi.Cache")
class Cache:
    """A minimal accessible objects cache to fulfill AT-SPI2's expectations that events come from an
    accessible application which has a valid accessible objects cache."""

    def GetItems(self) -> List[CacheEntry]:
        return []

session_bus = SessionMessageBus()
a11y_bus_info_provider = session_bus.get_proxy("org.a11y.Bus", "/org/a11y/bus")
address = a11y_bus_info_provider.GetAddress()
a11y_bus = AddressedMessageBus(address)
announcer = Announcer()
a11y_bus.publish_object(ANNOUNCER_PATH, announcer)
a11y_bus.publish_object("/org/a11y/atspi/cache", Cache())
loop = EventLoop()
threading.Thread(target=loop.run, daemon=True).start()
print("About to announce Hello, world!")
announcer.Announcement("", 1, 0, get_variant(str, "Hello, world!"), [])
# Give the announcement time to be processed
time.sleep(0.5)
print("Done announcing Hello, world!")
```

**New in Orca v49.0:** For headless applications, Orca now provides a much simpler D-Bus API
called `PresentMessage` that eliminates the need for the complex AT-SPI2 setup shown above.
See [README-REMOTE-CONTROLLER.md](README-REMOTE-CONTROLLER.md) for details on using this
streamlined interface.

## Providing Context-Sensitive Help Messages

AT-SPI2/ATK v2.52 added support for setting and retrieving "help text" on accessible objects.
Help text makes it possible to provide context-sensitive information that might not be
immediately obvious to the user. For instance in a slide presentation editor, when the user tabs to a
placeholder on a slide, an appropriate message might be "You are on a placeholder. Use the arrow
keys to reposition it on the slide. Press Return to edit its contents." (As the user moves the
placeholder on the slide, the Announcement feature described above could be used to inform the user
of the new location.)

Please note: Help text should *not* be used to announce mnemonics. Mnemonics are expected to be
exposed to Orca via the accessible Action interface via the toolkit. Orca has a setting, disabled
by default, to present mnemonics to the user.

Help text is supported in Orca v46 and later. Prior to Orca v47.alpha, this feature was disabled by
default. Starting with Orca v47.alpha, help text is presented by default when focus changes, but
that presentation can be disabled by the user either globally or on per-app basis. However, even
when disabled for focus changes, users can always obtain the help text on demand by using Orca's
"Where Am I?" command.

### Help Message Example: GTK 3

```python
#!/usr/bin/python

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

def on_activate(application):
    window = Gtk.ApplicationWindow(application=application)
    box = Gtk.HBox()
    window.add(box)
    label = Gtk.Label(label="Type something here:")
    box.add(label)
    entry = Gtk.Entry()
    box.add(entry)

    # Setting the mnemonic widget will cause the accessible labelled-by relation to be
    # set. Orca uses that to say "Type something here:" when the entry gains focus.
    label.set_mnemonic_widget(entry)

    # This text is presented by Orca as a "tutorial message."
    entry.get_accessible().set_help_text("Enter 10 characters.")
    window.show_all()

app = Gtk.Application()
app.connect("activate", on_activate)
app.run(None)
```

### Help Message Example: GTK 4 (Minimum Version: 4.16)

```python
#!/usr/bin/python

import gi
gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

def on_activate(application):
    window = Gtk.ApplicationWindow(application=application)
    box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
    window.set_child(box)
    label = Gtk.Label(label="Type something here:")
    box.append(label)
    entry = Gtk.Entry()
    box.append(entry)

    # Setting the mnemonic widget will cause the accessible labelled-by relation to be
    # set. Orca uses that to say "Type something here:" when the entry gains focus.
    label.set_mnemonic_widget(entry)

    # This text is presented by Orca as a "tutorial message."
    entry.update_property([Gtk.AccessibleProperty.HELP_TEXT], ["Enter 10 characters."])
    window.present()

app = Gtk.Application()
app.connect("activate", on_activate)
app.run(None)
```

### Help Message Example: Qt 6 (Minimum Version: 6.8)

```python
#!/usr/bin/python
import sys
from PySide6.QtWidgets import QMainWindow, QLabel, QLineEdit, QHBoxLayout, QApplication, QWidget

app = QApplication(sys.argv)
window = QMainWindow()
central_widget = QWidget()
box = QHBoxLayout(central_widget)
window.setCentralWidget(central_widget)
label = QLabel("Type something here:")
box.addWidget(label)
entry = QLineEdit()
box.addWidget(entry)

# Setting the label's buddy will cause the accessible label-for relation to be
# set. Orca uses that to say "Type something here:" when the entry gains focus.
label.setBuddy(entry)

# This text is presented by Orca as a "tutorial message."
entry.setWhatsThis("Enter 10 characters.")
window.show()

app.exec()
```

## Tools For Debugging

We recommend using [Accerciser](https://gitlab.gnome.org/GNOME/accerciser) for examining the
information and events exposed by applications to assistive technologies.

For instances in which a plain-text dump would be preferable, Orca's `tools/` directory contains
some simple command-line utilities:

* **[dump-tree.py](tools/dump-tree.py)** - Dumps the full accessibility tree for the specified
  application.

* **[dump-focused-object.py](tools/dump-focused-object.py)** - Dumps basic information about the
  newly-focused object and its ancestors each time focus changes.

* **[dump-window-events.py](tools/dump-window-events.py)** - Dumps basic info in response to
  `window:activate` and `window:deactivate` events, which all accessible apps should be firing.
