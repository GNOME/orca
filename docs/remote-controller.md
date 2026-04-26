# Orca Remote Controller (D-Bus Interface)

[TOC]

## Overview

Orca exposes a D-Bus service at:

- **Service Name**: `org.gnome.Orca1.Service`
- **Main Object Path**: `/org/gnome/Orca1/Service`
- **Module Object Paths**: `/org/gnome/Orca1/Service/ModuleName`
  (e.g., `/org/gnome/Orca1/Service/SpeechManager`)

See [remote-controller-commands.md](remote-controller-commands.md) for a complete
list of available commands.

## Dependencies

The D-Bus interface requires:

- **dasbus** - Python D-Bus library used by Orca for the remote controller implementation.
  ([Installation instructions](https://dasbus.readthedocs.io/en/latest/index.html))

## Service-Level Commands

Commands available directly on the main service (`/org/gnome/Orca1/Service`):

### Get Orca's Version

```bash
gdbus call --session --dest org.gnome.Orca1.Service \
    --object-path /org/gnome/Orca1/Service \
    --method org.gnome.Orca1.Service.GetVersion
```

**Returns:** String containing the version (and revision if available)

### Present a Custom Message in Speech and/or Braille

```bash
gdbus call --session --dest org.gnome.Orca1.Service \
    --object-path /org/gnome/Orca1/Service \
    --method org.gnome.Orca1.Service.PresentMessage "Your message here"
```

**Parameters:**

- `message` (string): The message to present to the user

**Returns:** Boolean indicating success

### Show Orca's Preferences GUI

```bash
gdbus call --session --dest org.gnome.Orca1.Service \
    --object-path /org/gnome/Orca1/Service \
    --method org.gnome.Orca1.Service.ShowPreferences
```

**Returns:** Boolean indicating success

### Quit Orca

```bash
gdbus call --session --dest org.gnome.Orca1.Service \
    --object-path /org/gnome/Orca1/Service \
    --method org.gnome.Orca1.Service.Quit
```

**Returns:** Boolean indicating if the quit request was accepted

## Discovering Modules and Their Capabilities

### List Registered Modules

Introspect the service root to enumerate the modules currently registered:

```bash
gdbus introspect --session --dest org.gnome.Orca1.Service \
    --object-path /org/gnome/Orca1/Service --recurse
```

The child `<node>` entries beneath the root path are the registered modules.

### Inspect a Single Module

```bash
gdbus introspect --session --dest org.gnome.Orca1.Service \
    --object-path /org/gnome/Orca1/Service/SpeechManager
```

The XML lists each method with its parameter types and each property with its
type and access mode.

## Interacting with Modules

Each module exposes **Commands** and **Properties**:

- **Commands**: Actions that perform a task. These typically correspond to
  Orca commands bound to a keystroke (e.g., `IncreaseRate`).
- **Properties**: Runtime-mutable values, often a setting (e.g., `Rate`).
  Setting a value does **not** cause it to become permanently saved.

### Calling a Module Command

```bash
# With user notification
gdbus call --session --dest org.gnome.Orca1.Service \
    --object-path /org/gnome/Orca1/Service/ModuleName \
    --method org.gnome.Orca1.ModuleName.CommandName true

# Without user notification (silent)
gdbus call --session --dest org.gnome.Orca1.Service \
    --object-path /org/gnome/Orca1/Service/ModuleName \
    --method org.gnome.Orca1.ModuleName.CommandName false
```

**Parameters:**

- `notify_user` (boolean): Whether to notify the user of the action (see
  section below)

**Returns:** Boolean indicating success.

#### Example: Toggle speech

```bash
gdbus call --session --dest org.gnome.Orca1.Service \
    --object-path /org/gnome/Orca1/Service/SpeechManager \
    --method org.gnome.Orca1.SpeechManager.ToggleSpeech true
```

### Calling a Parameterized Command

Parameterized commands take additional arguments before the trailing
`notify_user` boolean.

#### Example: Get voices for a specific language

```bash
gdbus call --session --dest org.gnome.Orca1.Service \
    --object-path /org/gnome/Orca1/Service/SpeechManager \
    --method org.gnome.Orca1.SpeechManager.GetVoicesForLanguage \
    "en-us" "" false
```

This returns a list of available voices for US English.

### Reading and Writing Properties

Use the `org.freedesktop.DBus.Properties` interface.

#### Read a single property

```bash
gdbus call --session --dest org.gnome.Orca1.Service \
    --object-path /org/gnome/Orca1/Service/ModuleName \
    --method org.freedesktop.DBus.Properties.Get \
    "org.gnome.Orca1.ModuleName" "PropertyName"
```

##### Example: Get the current speech rate

```bash
gdbus call --session --dest org.gnome.Orca1.Service \
    --object-path /org/gnome/Orca1/Service/SpeechManager \
    --method org.freedesktop.DBus.Properties.Get \
    "org.gnome.Orca1.SpeechManager" "Rate"
```

#### Read all properties at once

```bash
gdbus call --session --dest org.gnome.Orca1.Service \
    --object-path /org/gnome/Orca1/Service/ModuleName \
    --method org.freedesktop.DBus.Properties.GetAll \
    "org.gnome.Orca1.ModuleName"
```

#### Write a property

```bash
gdbus call --session --dest org.gnome.Orca1.Service \
    --object-path /org/gnome/Orca1/Service/ModuleName \
    --method org.freedesktop.DBus.Properties.Set \
    "org.gnome.Orca1.ModuleName" "PropertyName" "<value-as-variant>"
```

##### Example: Set the current speech rate

```bash
gdbus call --session --dest org.gnome.Orca1.Service \
    --object-path /org/gnome/Orca1/Service/SpeechManager \
    --method org.freedesktop.DBus.Properties.Set \
    "org.gnome.Orca1.SpeechManager" "Rate" "<90.0>"
```

### User Notification Applicability

**Setting `notify_user=true` is not a guarantee that feedback will be presented.**

Some commands inherently don't make sense to announce. For example:

```bash
# This command should simply stop speech, not announce that it is stopping speech.
gdbus call --session --dest org.gnome.Orca1.Service \
    --object-path /org/gnome/Orca1/Service/SpeechManager \
    --method org.gnome.Orca1.SpeechManager.InterruptSpeech true
```

In those cases Orca will ignore the value of `notify_user`.

**Setting `notify_user=false` is not a guarantee that Orca will remain silent**, though for the
most part Orca will try to respect this value. The exceptions are:

1. If executing the command has resulted in UI being shown, such as a dialog or menu, the
   newly-shown UI will be presented in speech and/or braille based on the user's settings.
   Failure to announce that the user has been removed from one window and placed in another
   could be extremely confusing.
2. If the *sole* purpose of the command is to announce something without making any other
   changes, e.g. `PresentTime`, executing it with `notify_user=false` makes no sense. Adding
   checks and early returns to handle this possibility does not seem worth doing. If you
   don't want Orca to present the time, don't ask Orca to present the time. 😃

### Navigator Module "Enabled" State Applicability

**In the Remote Controller, Navigator commands are expected to work even when not "enabled."**

Some of Orca's Navigator modules, namely Table Navigator, Caret Navigator, and Structural Navigator,
have an "enabled" state. The reason for this is very much tied to the keyboard-centric nature of
Orca's commands. For instance, if Orca always grabbed "H" (for heading navigation) and the arrow
keys (for caret navigation), normal interaction with applications would be completely broken. For
this reason, Navigator modules whose commands will prevent normal, native interaction with
applications are typically not enabled by default and can be easily disabled.

In contrast, performing Navigator commands via D-Bus does not prevent native interaction with
applications. For instance, one could use the Remote Controller to move to the next heading without
causing H to stop functioning in editable fields. For this reason, and to avoid a performance hit,
the decision was made to not check if (keyboard-centric) navigation commands were enabled. As a
result, it should be possible to use Remote Controller navigation even in "focus mode" or other
cases where Orca is not controlling the caret. This is by design.

Given the keyboard-centric nature of Orca's commands, there may be instances in which one uses the
Remote Controller for navigation and Orca fails to correctly update its location in response. If
Orca correctly updates its location when the same navigation command is executed via keyboard,
please report the Remote Controller failure as a new bug in Orca's gitlab.
