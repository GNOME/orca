# Orca
#
# Copyright 2004-2006 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

try:
    # This can fail due to gtk not being available.  We want to
    # be able to recover from that if possible.  The main driver
    # for this is to allow "orca --text-setup" to work even if
    # the desktop is not running.
    #
    import gtk
except:
    pass

import os, signal, sys
import string
import time

import atspi
import braille
import debug
import keynames
import keybindings
import mag
import rolenames
import settings
import speech
import threading

from input_event import BrailleEvent
from input_event import KeyboardEvent
from input_event import InputEventHandler

from orca_i18n import _           # for gettext support

# The user-settings module (see loadUserSettings).
#
_userSettings = None

# set each time a keyboard or braille event is received.
#

# The InputEvent instance representing the last input event.  This is
# set each time a keyboard or braille event is received.
#
lastInputEvent = None

# A new modifier to use (set by the press of any key in the
# settings.orcaModifierKeys list) to represent the Orca modifier.
#
MODIFIER_ORCA = 8

########################################################################
#                                                                      #
# METHODS FOR HANDLING PRESENTATION MANAGERS                           #
#                                                                      #
# A presentation manager is what reacts to AT-SPI object events as     #
# well as user input events (keyboard and Braille) to present info     #
# to the user.                                                         #
#                                                                      #
########################################################################

# The known presentation managers (set up in start())
#
_PRESENTATION_MANAGERS = None

# The current presentation manager, which is an index into the
# _PRESENTATION_MANAGERS list.
#
_currentPresentationManager = -1

def _switchToPresentationManager(index):
    """Switches to the given presentation manager.

    Arguments:
    - index: an index into _PRESENTATION_MANAGERS
    """

    global _currentPresentationManager

    if _currentPresentationManager >= 0:
        _PRESENTATION_MANAGERS[_currentPresentationManager].deactivate()

    _currentPresentationManager = index

    # Wrap the presenter index around.
    #
    if _currentPresentationManager >= len(_PRESENTATION_MANAGERS):
        _currentPresentationManager = 0
    elif _currentPresentationManager < 0:
        _currentPresentationManager = len(_PRESENTATION_MANAGERS) - 1

    _PRESENTATION_MANAGERS[_currentPresentationManager].activate()

def _switchToNextPresentationManager(script=None, inputEvent=None):
    """Switches to the next presentation manager.

    Arguments:
    - inputEvent: the InputEvent instance that caused this to be called.

    Returns True indicating the event should be consumed.
    """

    _switchToPresentationManager(_currentPresentationManager + 1)
    return True

########################################################################
#                                                                      #
# METHODS TO HANDLE APPLICATION LIST AND FOCUSED OBJECTS               #
#                                                                      #
########################################################################

# The Accessible that has visual focus.
#
locusOfFocus = None

def setLocusOfFocus(event, obj, notifyPresentationManager=True):
    """Sets the locus of focus (i.e., the object with visual focus) and
    notifies the current presentation manager of the change.

    Arguments:
    - event: if not None, the Event that caused this to happen
    - obj: the Accessible with the new locus of focus.
    - notifyPresentationManager: if True, propagate this event
    """

    global locusOfFocus

    if obj == locusOfFocus:
        return

    oldLocusOfFocus = locusOfFocus
    if oldLocusOfFocus and not oldLocusOfFocus.valid:
        oldLocusOfFocus = None

    locusOfFocus = obj
    if locusOfFocus and not locusOfFocus.valid:
        locusOfFocus = None

    if locusOfFocus:
        appname = ""
        if not locusOfFocus.app:
            appname = "None"
        else:
            appname = "'" + locusOfFocus.app.name + "'"

        debug.println(debug.LEVEL_FINE,
                      "LOCUS OF FOCUS: app=%s name='%s' role='%s'" \
                      % (appname, locusOfFocus.name, locusOfFocus.role))

        if event:
            debug.println(debug.LEVEL_FINE,
                          "                event='%s'" % event.type)
        else:
            debug.println(debug.LEVEL_FINE,
                          "                event=None")
    else:
        if event:
            debug.println(debug.LEVEL_FINE,
                          "LOCUS OF FOCUS: None event='%s'" % event.type)
        else:
            debug.println(debug.LEVEL_FINE,
                          "LOCUS OF FOCUS: None event=None")

    if notifyPresentationManager and _currentPresentationManager >= 0:
        _PRESENTATION_MANAGERS[_currentPresentationManager].\
            locusOfFocusChanged(event, oldLocusOfFocus, locusOfFocus)

def visualAppearanceChanged(event, obj):
    """Called (typically by scripts) when the visual appearance of an object
    changes and notifies the current presentation manager of the change.  This
    method should not be called for objects whose visual appearance changes
    solely because of focus -- setLocusOfFocus is used for that.  Instead, it
    is intended mostly for objects whose notional 'value' has changed, such as
    a checkbox changing state, a progress bar advancing, a slider moving, text
    inserted, caret moved, etc.

    Arguments:
    - event: if not None, the Event that caused this to happen
    - obj: the Accessible whose visual appearance changed.
    """

    if _currentPresentationManager >= 0:
        _PRESENTATION_MANAGERS[_currentPresentationManager].\
            visualAppearanceChanged(event, obj)

def isInActiveApp(obj):
    """Returns True if the given object is from the same application that
    currently has keyboard focus.

    Arguments:
    - obj: an Accessible object
    """

    if not obj:
        return False
    else:
        return locusOfFocus and (locusOfFocus.app == obj.app)

def findActiveWindow():
    """Traverses the list of known apps looking for one who has an
    immediate child (i.e., a window) whose state includes the active state.

    Returns the Python Accessible of the window that's active or None if
    no windows are active.
    """

    window = None
    apps = atspi.getKnownApplications()
    for app in apps:
        for i in range(0, app.childCount):
            state = app.child(i).state
            if state.count(atspi.Accessibility.STATE_ACTIVE) > 0:
                window = app.child(i)
                break

    return window

def _onChildrenChanged(e):
    """Tracks children-changed events on the desktop to determine when
    apps start and stop.

    Arguments:
    - e: at-spi event from the at-api registry
    """

    registry = atspi.Registry()
    if e.source == registry.desktop:

        # If the desktop is empty, the user has logged out-- shutdown Orca
        #
        try:
            if registry.desktop.childCount == 0:
                speech.speak(_("User logged out - shutting down."))
                shutdown()
                return
        except: # could be a CORBA.COMM_FAILURE
            debug.printException(debug.LEVEL_FINEST)
            shutdown()
            return

########################################################################
#                                                                      #
# Keyboard Event Recording Support                                     #
#                                                                      #
########################################################################

_recordingKeystrokes = False
_keystrokesFile = None

def _closeKeystrokeWindowAndRecord(entry, window):
    global _keystrokesFile
    window.destroy()
    entry_text = entry.get_text()
    _keystrokesFile = open(entry_text, 'w')

def _closeKeystrokeWindowAndCancel(window):
    global _recordingKeystrokes
    window.destroy()
    _recordingKeystrokes = False

def toggleKeystrokeRecording(script=None, inputEvent=None):
    """Toggles the recording of keystrokes on and off.  When the
    user presses the magic key (Pause), Orca will pop up a window
    requesting a filename.  When the user presses the close button,
    Orca will start recording keystrokes to the file and will continue
    recording them until the user presses the magic key again.

    This functionality is used primarily to help gather keystroke
    information for regression testing purposes.  The keystrokes are
    recorded in such a way that they can be played back via the
    src/tools/play_keystrokes.py utility.

    Arguments:
    - inputEvent: the key event (if any) which caused this to be called.

    Returns True indicating the event should be consumed.
    """

    global _recordingKeystrokes
    global _keystrokesFile

    if _recordingKeystrokes:
        # If the filename entry window is still up, we don't have a file
        # yet.
        #
        if _keystrokesFile:
            _keystrokesFile.close()
            _keystrokesFile = None
            _recordingKeystrokes = False
    else:
        _recordingKeystrokes = True
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_title("Keystroke Filename")

        vbox = gtk.VBox(False, 0)
        window.add(vbox)
        vbox.show()

        entry = gtk.Entry()
        entry.set_max_length(50)
        entry.set_editable(True)
        entry.set_text("keystrokes.txt")
        entry.select_region(0, len(entry.get_text()))
        # For now, do not allow "Return" to close the window - the reason
        # for this is that the key press closes the window, and the key
        # release will end up getting recorded.
        #
        #entry.connect("activate", _closeKeystrokeWindow, window)
        vbox.pack_start(entry, True, True, 0)
        entry.show()

        hbox = gtk.HBox(False, 0)
        vbox.add(hbox)
        hbox.show()

        ok = gtk.Button(stock=gtk.STOCK_OK)
        ok.connect("clicked", lambda w: _closeKeystrokeWindowAndRecord(\
            entry, \
            window))

        cancel = gtk.Button(stock=gtk.STOCK_CANCEL)
        cancel.connect("clicked", lambda w: _closeKeystrokeWindowAndCancel(\
            window))

        vbox.pack_start(cancel, True, True, 0)
        vbox.pack_start(ok, True, True, 0)

        ok.set_flags(gtk.CAN_DEFAULT)
        ok.grab_default()
        ok.show()
        cancel.show()

        window.set_modal(True)
        window.show()
    return True

########################################################################
#                                                                      #
# DEBUG support.                                                       #
#                                                                      #
########################################################################

def cycleDebugLevel(script=None, inputEvent=None):
    """Cycles the debug level at run time.

    Arguments:
    - inputEvent: the InputEvent instance that caused this to be called.

    Returns True indicating the event should be consumed.
    """

def cycleDebugLevel(script=None, inputEvent=None):
    global _debugLevel

    level = debug.debugLevel

    if level == debug.LEVEL_ALL:
        level = debug.LEVEL_FINEST
    elif level == debug.LEVEL_FINEST:
        level = debug.LEVEL_FINER
    elif level == debug.LEVEL_FINER:
        level = debug.LEVEL_FINE
    elif level == debug.LEVEL_FINE:
        level = debug.LEVEL_CONFIGURATION
    elif level == debug.LEVEL_CONFIGURATION:
        level = debug.LEVEL_INFO
    elif level == debug.LEVEL_INFO:
        level = debug.LEVEL_WARNING
    elif level == debug.LEVEL_WARNING:
        level = debug.LEVEL_SEVERE
    elif level == debug.LEVEL_SEVERE:
        level = debug.LEVEL_OFF
    elif level == debug.LEVEL_OFF:
        level = debug.LEVEL_ALL

    debug.debugLevel = level

    if level == debug.LEVEL_ALL:
        speech.speak(_("Debug level all."))
    elif level == debug.LEVEL_FINEST:
        speech.speak(_("Debug level finest."))
    elif level == debug.LEVEL_FINER:
        speech.speak(_("Debug level finer."))
    elif level == debug.LEVEL_FINE:
        speech.speak(("Debug level fine."))
    elif level == debug.LEVEL_CONFIGURATION:
        speech.speak("Debug level configuration.")
    elif level == debug.LEVEL_INFO:
        speech.speak("Debug level info.")
    elif level == debug.LEVEL_WARNING:
        speech.speak("Debug level warning.")
    elif level == debug.LEVEL_SEVERE:
        speech.speak("Debug level severe.")
    elif level == debug.LEVEL_OFF:
        speech.speak("Debug level off.")

    return True

def printApps(script=None, inputEvent=None):
    """Prints a list of all applications to stdout

    Arguments:
    - inputEvent: the InputEvent instance that caused this to be called.

    Returns True indicating the event should be consumed.
    """

    level = debug.LEVEL_OFF

    apps = atspi.getKnownApplications()
    debug.println(level, "There are %d Accessible applications" % len(apps))
    for app in apps:
        debug.printDetails(level, "  App: ", app, False)
        for i in range(0, app.childCount):
            child = app.child(i)
            debug.printDetails(level, "    Window: ", child, False)
            if child.parent != app:
                debug.println(level,
                              "      WARNING: child's parent is not app!!!")

    return True

def printActiveApp(script=None, inputEvent=None):
    """Prints the active application.

    Arguments:
    - inputEvent: the key event (if any) which caused this to be called.

    Returns True indicating the event should be consumed.
    """

    level = debug.LEVEL_OFF

    window = findActiveWindow()
    if not window:
        debug.println(level, "Active application: None")
    else:
        app = window.app
        if not app:
            debug.println(level, "Active application: None")
        else:
            debug.println(level, "Active application: %s" % app.name)

    return True

def printAncestry(script=None, inputEvent=None):
    """Prints the ancestry for the current locusOfFocus"""
    atspi.printAncestry(locusOfFocus)
    return True

def printHierarchy(script=None, inputEvent=None):
    """Prints the application for the current locusOfFocus"""
    if locusOfFocus:
        atspi.printHierarchy(locusOfFocus.app, locusOfFocus)
    return True

########################################################################
#                                                                      #
# METHODS FOR HANDLING LEARN MODE.                                     #
#                                                                      #
########################################################################

def enterLearnMode(script=None, inputEvent=None):
    """Turns learn mode on.  The user must press the escape key to exit
    learn mode.

    Returns True to indicate the input event has been consumed.
    """

    speech.speak(
        _("Entering learn mode.  Press any key to hear its function. " \
          + "To exit learn mode, press the escape key."))
    braille.displayMessage(_("Learn mode.  Press escape to exit."))
    settings.learnModeEnabled = True
    return True

def exitLearnMode(script=None, inputEvent=None):
    """Turns learn mode off.

    Returns True to indicate the input event has been consumed.
    """

    speech.speak(_("Exiting learn mode."))
    braille.displayMessage(_("Exiting learn mode."))
    settings.learnModeEnabled = False
    return True

########################################################################
#                                                                      #
# METHODS FOR PRE-PROCESSING AND MASSAGING KEYBOARD EVENTS.            #
#                                                                      #
# All keyboard events are funnelled through here first.  Orca itself   #
# might have global keybindings (e.g., to switch between presenters),  #
# but it will typically pass the event onto the currently active       #
# active presentation manager.                                         #
#                                                                      #
########################################################################

# Keybindings that Orca itself cares about.
#
_keyBindings = None

# True if the orca modifier key is currently pressed.
#
_orcaModifierPressed = False

def _isPrintableKey(event_string):
    """Return an indication of whether this is an alphanumeric or
       punctuation key.

    Arguments:
    - event: the event string

    Returns True if this is an alphanumeric or punctuation key.
    """

    reply = event_string in string.printable
    debug.println(debug.LEVEL_FINEST,
                  "orca._echoPrintableKey: returning: %s" % reply)
    return reply

def _isModifierKey(event_string):
    """Return an indication of whether this is a modifier key.

    Arguments:
    - event: the event string

    Returns True if this is a modifier key
    """

    # [[[TODO:richb - the Fn key on my laptop doesn't seem to generate an
    #    event.]]]

    modifierKeys = [ 'Alt_L', 'Alt_R', 'Control_L', 'Control_R', \
                     'Shift_L', 'Shift_R', 'Meta_L', 'Meta_R', "Insert" ]

    reply = event_string in modifierKeys
    debug.println(debug.LEVEL_FINEST,
                  "orca._echoModifierKey: returning: %s" % reply)
    return reply

def _isLockingKey(event_string):
    """Return an indication of whether this is a locking key.

    Arguments:
    - event: the event string

    Returns True if this is a locking key.
    """

    lockingKeys = [ "Caps_Lock", "Num_Lock", "Scroll_Lock" ]

    reply = event_string in lockingKeys
    debug.println(debug.LEVEL_FINEST,
                  "orca._echoLockingKey: returning: %s" % reply)
    return reply

def _isFunctionKey(event_string):
    """Return an indication of whether this is a function key.

    Arguments:
    - event: the event string

    Returns True if this is a function key.
    """

    # [[[TODO:richb - what should be done about the function keys on the left
    #    side of my Sun keyboard and the other keys (like Scroll Lock), which
    #    generate "Fn" key events?]]]

    functionKeys = [ "F1", "F2", "F3", "F4", "F5", "F6",
                     "F7", "F8", "F9", "F10", "F11", "F12" ]

    reply = event_string in functionKeys
    debug.println(debug.LEVEL_FINEST,
                  "orca._echoFunctionKey: returning: %s" % reply)
    return reply

def _isActionKey(event_string):
    """Return an indication of whether this is an action key.

    Arguments:
    - event: the event string

    Returns True if this is an action key.
    """

    actionKeys = [ "space", "Return", "Escape", "Tab", "BackSpace", "Delete",
                   "Left", "Right", "Up", "Down", "Page_Up", "Page_Down" ]

    reply = event_string in actionKeys
    debug.println(debug.LEVEL_FINEST,
                  "orca._echoActionKey: returning: %s" % reply)
    return reply

def _keyEcho(event):
    """If the keyEcho setting is enabled, check to see what type of key
    event it is and echo it via speech, if the user wants that type of
    key echoed.

    Uppercase keys will be spoken using the "uppercase" voice style,
    whereas lowercase keys will be spoken using the "default" voice style.

    Arguments:
    - event: an AT-SPI DeviceEvent
    """

    event_string = event.event_string
    debug.println(debug.LEVEL_FINEST,
                  "orca._keyEcho: string to echo: %s" % event_string)

    voices = settings.voices
    voice = voices[settings.DEFAULT_VOICE]

    # If key echo is enabled, then check to see what type of key event
    # it is and echo it via speech, if the user wants that type of key
    # echoed.
    #
    if settings.enableKeyEcho:
        if _isPrintableKey(event_string):
            if not settings.enablePrintableKeys:
                return

            if event_string.isupper():
                voice = voices[settings.UPPERCASE_VOICE]

        elif _isModifierKey(event_string):
            if not settings.enableModifierKeys:
                return

            # The control characters come through as control characters,
            # so we just turn them into their ASCII equivalent.  NOTE that
            # the upper case ASCII characters will be used (e.g., ctrl+a
            # will be turned into the string "A").  All these checks here
            # are to just do some sanity checking before doing the
            # conversion. [[[WDW - this is making assumptions about
            # mapping ASCII control characters to to UTF-8.]]]
            #
            if (event.modifiers & (1 << atspi.Accessibility.MODIFIER_CONTROL)) \
               and (not event.is_text) and (len(event_string) == 1):
                value = ord(event.event_string[0])
                if value < 32:
                    event_string = chr(value + 0x40)

        elif _isLockingKey(event_string):
            if not settings.enableLockingKeys:
                return

        elif _isFunctionKey(event_string):
            if not settings.enableFunctionKeys:
                return

        elif _isActionKey(event_string):
            if not settings.enableActionKeys:
                return

        else:
            debug.println(debug.LEVEL_FINEST,
                  "orca._keyEcho: event string not handled: %s" % event_string)
            return

        # Check to see if there are localized words to be spoken for
        # this key event.
        try:
            event_string = keynames.keynames[event_string]
        except:
            debug.printException(debug.LEVEL_FINEST)
            pass

        debug.println(debug.LEVEL_FINEST,
                      "orca._keyEcho: speaking: %s" % event_string)
        speech.speak(event_string, voice)

def _processKeyboardEvent(event):
    """The primary key event handler for Orca.  Keeps track of various
    attributes, such as the lastInputEvent.  Also calls keyEcho as well
    as any local keybindings before passing the event on to the active
    presentation manager.  This method is called synchronously from the
    AT-SPI registry and should be performant.  In addition, it
    must return True if it has consumed the event (and False if not).

    Arguments:
    - event: an AT-SPI DeviceEvent

    Returns True if the event should be consumed.
    """

    global lastInputEvent
    global _orcaModifierPressed

    event_string = event.event_string

    # Log the keyboard event for future playback, if desired.
    #
    string = atspi.KeystrokeListener.keyEventToString(event)
    if _recordingKeystrokes and _keystrokesFile \
       and (event_string != "Pause"):
        _keystrokesFile.write(string + "\n")
    debug.printInputEvent(debug.LEVEL_FINE, string)

    orcaModifierKeys = settings.orcaModifierKeys

    if event.type == atspi.Accessibility.KEY_PRESSED_EVENT:
        # Key presses always interrupt speech.
        #
        speech.stop()

        _keyEcho(event)

        # We treat the Insert key as a modifier - so just swallow it and
        # set our internal state.
        #
        if orcaModifierKeys.count(event_string):
            _orcaModifierPressed = True
            return True

    elif (event.type == atspi.Accessibility.KEY_RELEASED_EVENT) \
         and orcaModifierKeys.count(event_string):
        _orcaModifierPressed = False
        return True

    # Orca gets first stab at the event.  Then, the presenter gets
    # a shot. [[[TODO: WDW - might want to let the presenter try first?
    # The main reason this is staying as is is that we may not want
    # scripts to override fundamental Orca key bindings.]]]
    #
    keyboardEvent = KeyboardEvent(event)
    if _orcaModifierPressed:
        keyboardEvent.modifiers |= (1 << MODIFIER_ORCA)

    consumed = False
    try:
        consumed = _keyBindings.consumeKeyboardEvent(None, keyboardEvent)
        if (not consumed) and (_currentPresentationManager >= 0):
            consumed = _PRESENTATION_MANAGERS[_currentPresentationManager].\
                       processKeyboardEvent(keyboardEvent)
        if (not consumed) and settings.learnModeEnabled:
            if event.type == atspi.Accessibility.KEY_PRESSED_EVENT:
                braille.displayMessage(event_string)
                speech.speak(event_string)
            elif (event.type == atspi.Accessibility.KEY_RELEASED_EVENT) \
                 and (event_string == "Escape"):
                exitLearnMode(None, keyboardEvent)
            consumed = True
    except:
        debug.printException(debug.LEVEL_SEVERE)

    lastInputEvent = keyboardEvent

    return consumed

########################################################################
#                                                                      #
# METHODS FOR PRE-PROCESSING AND MASSAGING BRAILLE EVENTS.             #
#                                                                      #
########################################################################

def _processBrailleEvent(command):
    """Called whenever a  key is pressed on the Braille display.

    Arguments:
    - command: the BrlAPI command for the key that was pressed.

    Returns True if the event was consumed; otherwise False
    """

    global lastInputEvent

    # [[[TODO: WDW - probably should add braille bindings to this module.]]]

    consumed = False

    # Braille key presses always interrupt speech.
    #
    speech.stop()

    event = BrailleEvent(command)
    lastInputEvent = event

    try:
        consumed = _PRESENTATION_MANAGERS[_currentPresentationManager].\
                   processBrailleEvent(event)
    except:
        debug.printException(debug.LEVEL_SEVERE)

    if (not consumed) and settings.learnModeEnabled:
        consumed = True

    return consumed

########################################################################
#                                                                      #
# METHODS FOR DRAWING RECTANGLES AROUND OBJECTS ON THE SCREEN          #
#                                                                      #
########################################################################

_display = None
_visibleRectangle = None

def drawOutline(x, y, width, height, erasePrevious=True):
    """Draws a rectangular outline around the accessible, erasing the
    last drawn rectangle in the process."""

    global _display
    global _visibleRectangle

    if not _display:
        try:
            _display = gtk.gdk.display_get_default()
        except:
            debug.printException(debug.LEVEL_FINEST)
            _display = gtk.gdk.display(":0")

        if not _display:
            debug.println(debug.LEVEL_SEVERE,
                          "orca.drawOutline could not open display.")
            return

    screen = _display.get_default_screen()
    root_window = screen.get_root_window()
    graphics_context = root_window.new_gc()
    graphics_context.set_subwindow(gtk.gdk.INCLUDE_INFERIORS)
    graphics_context.set_function(gtk.gdk.INVERT)
    graphics_context.set_line_attributes(3,                  # width
                                         gtk.gdk.LINE_SOLID, # style
                                         gtk.gdk.CAP_BUTT,   # end style
                                         gtk.gdk.JOIN_MITER) # join style

    # Erase the old rectangle.
    #
    if _visibleRectangle and erasePrevious:
        drawOutline(_visibleRectangle[0], _visibleRectangle[1],
                    _visibleRectangle[2], _visibleRectangle[3], False)
        _visibleRectangle = None

    # We'll use an invalid x value to indicate nothing should be
    # drawn.
    #
    if x < 0:
        _visibleRectangle = None
        return

    # The +1 and -2 stuff here is an attempt to stay within the
    # bounding box of the object.
    #
    root_window.draw_rectangle(graphics_context,
                               False, # Fill
                               x + 1,
                               y + 1,
                               max(1, width - 2),
                               max(1, height - 2))

    _visibleRectangle = [x, y, width, height]

def outlineAccessible(accessible, erasePrevious=True):
    """Draws a rectangular outline around the accessible, erasing the
    last drawn rectangle in the process."""

    if accessible:
        component = accessible.component
        if component:
            visibleRectangle = component.getExtents(0) # coord type = screen
            drawOutline(visibleRectangle.x, visibleRectangle.y,
                        visibleRectangle.width, visibleRectangle.height,
                        erasePrevious)
    else:
        drawOutline(-1, 0, 0, 0, erasePrevious)

########################################################################
#                                                                      #
# METHODS FOR HANDLING INITIALIZATION, SHUTDOWN, AND USE.              #
#                                                                      #
########################################################################

def _toggleSilenceSpeech(script=None, inputEvent=None):
    """Toggle the silencing of speech.

    Returns True to indicate the input event has been consumed.
    """
    speech.stop()
    if settings.silenceSpeech:
        settings.silenceSpeech = False
        speech.speak(_("Speech enabled."))
    else:
        speech.speak(_("Speech disabled."))
        settings.silenceSpeech = True
    return True

def loadUserSettings(script=None, inputEvent=None):
    """Loads (and reloads) the user settings module, reinitializing
    things such as speech if necessary.

    Returns True to indicate the input event has been consumed.
    """

    global _userSettings

    # Shutdown the output drivers and give them a chance to die.
    speech.shutdown()
    braille.shutdown()
    mag.shutdown()
    time.sleep(1)

    reloaded = False
    if _userSettings:
        try:
            reload(_userSettings)
            reloaded = True
        except ImportError:
            debug.printException(debug.LEVEL_FINEST)
    else:
        try:
            _userSettings = __import__("user-settings")
        except ImportError:
            debug.printException(debug.LEVEL_FINEST)

    if settings.enableSpeech:
        try:
            speech.init()
            if reloaded:
                speech.speak(_("Orca user settings reloaded."))
            debug.println(debug.LEVEL_CONFIGURATION,
                          "Speech module has been initialized.")
        except:
            debug.printException(debug.LEVEL_SEVERE)
            debug.println(debug.LEVEL_SEVERE,
                          "Could not initialize connection to speech.")
    else:
        debug.println(debug.LEVEL_CONFIGURATION,
                      "Speech module has NOT been initialized.")

    if settings.enableBraille:
        try:
            braille.init(_processBrailleEvent, 7)
        except:
            debug.printException(debug.LEVEL_WARNING)
            debug.println(debug.LEVEL_WARNING,
                          "Could not initialize connection to braille.")

    if settings.enableMagnifier:
        try:
            mag.init()
            debug.println(debug.LEVEL_CONFIGURATION,
                          "Magnification module has been initialized.")
        except:
            debug.printException(debug.LEVEL_SEVERE)
            debug.println(debug.LEVEL_SEVERE,
                          "Could not initialize connection to magnifier.")
    else:
        debug.println(debug.LEVEL_CONFIGURATION,
                      "Magnification module has NOT been initialized.")

    return True

def _showPreferencesGUI(script=None, inputEvent=None):
    """Displays the user interace to configure Orca and set up
    user preferences using a GUI.

    Returns True to indicate the input event has been consumed.
    """

    try:
        module = __import__(settings.guiPreferencesModule,
                            globals(),
                            locals(),
                            [''])
        module.showPreferencesUI()
    except:
        debug.printException(debug.LEVEL_SEVERE)
        pass

    return True

def _showPreferencesConsole(script=None, inputEvent=None):
    """Displays the user interace to configure Orca and set up
    user preferences via a command line interface.

    Returns True to indicate the input event has been consumed.
    """

    try:
        module = __import__(settings.consolePreferencesModule,
                            globals(),
                            locals(),
                            [''])
        module.showPreferencesUI()
    except:
        debug.printException(debug.LEVEL_SEVERE)
        pass

    return True

# If True, this module has been initialized.
#
_initialized = False

def init(registry):
    """Initialize the orca module, which initializes speech, braille,
    and mag modules.  Also builds up the application list, registers
    for AT-SPI events, and creates scripts for all known applications.

    Returns True if the initialization procedure has run, or False if this
    module has already been initialized.
    """

    global _initialized
    global _keyBindings

    if _initialized:
        return False

    _keyBindings = keybindings.KeyBindings()

    enterLearnModeHandler = InputEventHandler(\
        enterLearnMode,
        _("Enters learn mode.  Press escape to exit learn mode."))
    _keyBindings.add(keybindings.KeyBinding("F1", \
                                            1 << MODIFIER_ORCA, \
                                            1 << MODIFIER_ORCA, \
                                            enterLearnModeHandler))

    decreaseSpeechRateHandler = InputEventHandler(\
        speech.decreaseSpeechRate,
        _("Decreases the speech rate."))
    _keyBindings.add(keybindings.KeyBinding("Left", \
                                            1 << MODIFIER_ORCA, \
                                            1 << MODIFIER_ORCA,
                                            decreaseSpeechRateHandler))

    increaseSpeechRateHandler = InputEventHandler(\
        speech.increaseSpeechRate,
        _("Increases the speech rate."))
    _keyBindings.add(keybindings.KeyBinding("Right", \
                                            1 << MODIFIER_ORCA, \
                                            1 << MODIFIER_ORCA,
                                            increaseSpeechRateHandler))

    shutdownHandler = InputEventHandler(shutdown, _("Quits Orca"))
    _keyBindings.add(keybindings.KeyBinding("F12", \
                                            0, \
                                            0,
                                            shutdownHandler))
    _keyBindings.add(keybindings.KeyBinding("SunF37", \
                                            0, \
                                            0,
                                            shutdownHandler))

    keystrokeRecordingHandler = InputEventHandler(\
        toggleKeystrokeRecording,
        _("Toggles keystroke recording on and off."))
    _keyBindings.add(keybindings.KeyBinding("Pause", \
                                            0, \
                                            0,
                                            keystrokeRecordingHandler))

    preferencesSettingsHandler = InputEventHandler(\
        _showPreferencesGUI,
        _("Displays the preferences configuration dialog."))
    _keyBindings.add(keybindings.KeyBinding(
        "space", \
        (1 << MODIFIER_ORCA | 1 << atspi.Accessibility.MODIFIER_CONTROL),
        1 << MODIFIER_ORCA,
        preferencesSettingsHandler))

    loadUserSettingsHandler = InputEventHandler(\
        loadUserSettings,
        _("Reloads user settings and reinitializes services as necessary."))
    _keyBindings.add(keybindings.KeyBinding(
        "space", \
        (1 << MODIFIER_ORCA | 1 << atspi.Accessibility.MODIFIER_CONTROL),
        (1 << MODIFIER_ORCA | 1 << atspi.Accessibility.MODIFIER_CONTROL),
        loadUserSettingsHandler))

    toggleSilenceSpeechHandler = InputEventHandler(\
        _toggleSilenceSpeech,
        _("Toggles the silencing of speech."))
    _keyBindings.add(keybindings.KeyBinding(
        "s", \
        1 << MODIFIER_ORCA,
        1 << MODIFIER_ORCA,
        toggleSilenceSpeechHandler))

    listAppsHandler = InputEventHandler(
        printApps,
        _("Prints a debug listing of all known applications to the console where Orca is running."))
    _keyBindings.add(keybindings.KeyBinding(
        "F5",
        (1 << MODIFIER_ORCA | 1 << atspi.Accessibility.MODIFIER_CONTROL),
        1 << MODIFIER_ORCA,
        listAppsHandler))

    cycleDebugLevelHandler = InputEventHandler(
        cycleDebugLevel,
        _("Cycles the debug level at run time."))
    _keyBindings.add(keybindings.KeyBinding(
        "F5",
        (1 << MODIFIER_ORCA | 1 << atspi.Accessibility.MODIFIER_CONTROL),
        (1 << MODIFIER_ORCA | 1 << atspi.Accessibility.MODIFIER_CONTROL),
        cycleDebugLevelHandler))

    printActiveAppHandler = InputEventHandler(\
        printActiveApp,
        _("Prints debug information about the currently active application to the console where Orca is running."))
    _keyBindings.add(keybindings.KeyBinding("F6", \
                                            1 << MODIFIER_ORCA, \
                                            1 << MODIFIER_ORCA,
                                            printActiveAppHandler))

    printAncestryHandler = InputEventHandler(\
        printAncestry,
        _("Prints debug information about the ancestry of the object with focus"))
    _keyBindings.add(keybindings.KeyBinding(
        "F7",
        (1 << MODIFIER_ORCA | 1 << atspi.Accessibility.MODIFIER_CONTROL),
        1 << MODIFIER_ORCA,
        printAncestryHandler))

    printHierarchyHandler = InputEventHandler(\
        printHierarchy,
        _("Prints debug information about the application with focus"))

    _keyBindings.add(keybindings.KeyBinding(
        "F7",
        (1 << MODIFIER_ORCA | 1 << atspi.Accessibility.MODIFIER_CONTROL),
        (1 << MODIFIER_ORCA | 1 << atspi.Accessibility.MODIFIER_CONTROL),
        printHierarchyHandler))

    nextPresentationManagerHandler = InputEventHandler(\
        _switchToNextPresentationManager,
        _("Switches to the next presentation manager."))
    _keyBindings.add(keybindings.KeyBinding("F8", \
                                            1 << MODIFIER_ORCA, \
                                            1 << MODIFIER_ORCA,
                                            nextPresentationManagerHandler))

    # Create and load an app's script when it is added to the desktop
    #
    registry.registerEventListener(_onChildrenChanged,
                                   "object:children-changed:")

    loadUserSettings()

    registry.registerKeystrokeListeners(_processKeyboardEvent)

    _initialized = True
    return True

def start(registry):
    """Starts Orca.
    """

    global _PRESENTATION_MANAGERS

    if not _initialized:
        init(registry)

    try:
        speech.speak(_("Welcome to Orca."))
        braille.displayMessage(_("Welcome to Orca."))
    except:
        debug.printException(debug.LEVEL_SEVERE)

    if not _PRESENTATION_MANAGERS:

        # [[[WDW - comment out hierarchical_presenter for now.  It
        # relies on the list of known applications, and we've disabled
        # that due to a hang in a call to getChildAtIndex in
        # atspi.getKnownApplications.]]]
        #
        #import focus_tracking_presenter
        #import hierarchical_presenter
        #_PRESENTATION_MANAGERS = \
        #    [focus_tracking_presenter.FocusTrackingPresenter(),
        #     hierarchical_presenter.HierarchicalPresenter()]

        import focus_tracking_presenter
        _PRESENTATION_MANAGERS = \
            [focus_tracking_presenter.FocusTrackingPresenter()]

    _switchToPresentationManager(0) # focus_tracking_presenter

    registry.start()

def abort():
    os._exit(1)

def timeout():
    print "TIMEOUT: Hung while trying to shutdown.  Aborting."
    abort()

def shutdown(script=None, inputEvent=None):
    """Exits Orca.  Unregisters any event listeners and cleans up.  Also
    quits the bonobo main loop and resets the initialized state to False.

    Returns True if the shutdown procedure ran or False if this module
    was never initialized.
    """

    global _initialized

    if not _initialized:
        return False

    # [[[TODO: WDW - the timer stuff is an experiment to see if
    # we can recover from hangs.  It's only experimental, so it's
    # commented out for now.]]]
    #
    #timer = threading.Timer(5.0, timeout)
    #timer.start()

    speech.speak(_("goodbye."))
    braille.displayMessage(_("Goodbye."))

    # Deregister our event listeners
    #
    registry = atspi.Registry()
    registry.deregisterEventListener(_onChildrenChanged,
                                     "object:children-changed:")

    if _currentPresentationManager >= 0:
        _PRESENTATION_MANAGERS[_currentPresentationManager].deactivate()

    # Shutdown all the other support.
    #
    if settings.enableSpeech:
        speech.shutdown()
    if settings.enableBraille:
        braille.shutdown();
    if settings.enableMagnifier:
        mag.shutdown();

    registry.stop()

    #timer.cancel()
    #del timer

    _initialized = False
    return True

exitCount = 0
def shutdownOnSignal(signum, frame):
    global exitCount

    #print "Shutting down and exiting due to signal =", signum

    # Well...we'll try to exit nicely, but if we keep getting called,
    # something bad is happening, so just quit.
    #
    if exitCount:
        abort()
    else:
        exitCount += 1

    # Try to do a graceful shutdown if we can.
    #
    try:
        if _initialized:
            shutdown()
            return
        else:
            # We always want to try to shutdown speech since the
            # speech servers are very persistent about living.
            #
            speech.shutdown()
            shutdown()
            os._exit(0)
    except:
        abort()

def abortOnSignal(signum, frame):
    #print "Aborting due to signal =", signum
    abort()

def main():
    signal.signal(signal.SIGHUP, shutdownOnSignal)
    signal.signal(signal.SIGINT, shutdownOnSignal)
    signal.signal(signal.SIGTERM, shutdownOnSignal)
    signal.signal(signal.SIGQUIT, shutdownOnSignal)
    signal.signal(signal.SIGSEGV, abortOnSignal)

    # See if the desktop is running.  If it is, the import of gtk will
    # succeed.  If it isn't, the import will fail.
    #
    desktopRunning = False
    try:
        import gtk
        desktopRunning = True
    except:
        pass

    # Run the preferences setup if the user has specified
    # "--setup" or "--text-setup" on the command line.  If the
    # desktop is not running, we will fallback to the console-based
    # method as appropriate.
    #
    bypassSetup     = False
    setupRequested  = False
    showGUI         = False
    for arg in sys.argv:
        if (arg == _("--gui-setup")) or (arg == _("--setup")):
            setupRequested = True
            showGUI = desktopRunning
        elif arg == _("--text-setup"):
            setupRequested = True
            showGUI = False
        elif arg == _("--no-setup"):
            bypassSetup = True

    if setupRequested and (not bypassSetup) and (not showGUI):
        _showPreferencesConsole()
            
    if not desktopRunning:
        print "Cannot start Orca because it cannot connect"
        print "to the Desktop.  Please make sure the DISPLAY"
        print "environment variable has been set."
        return 1

    userprefs = os.path.join(os.environ["HOME"], ".orca")
    sys.path.insert(0, userprefs)
    sys.path.insert(0, '') # current directory

    registry = atspi.Registry()
    init(registry)

    # Check to see if the user wants the configuration GUI. It's
    # done here so that the user's existing preferences can be used
    # to set the initial GUI state.  We'll also force the set to
    # be run if the preferences file doesn't exist, unless the
    # user has bypassed any setup via the --no-setup switch.
    #
    if setupRequested and (not bypassSetup) and showGUI:
        _showPreferencesGUI()
    elif (not _userSettings) and (not bypassSetup):
        if desktopRunning:
            _showPreferencesGUI()
        else:
            _showPreferencesConsole()
        
    # Do not run Orca if accessibility has not been enabled.
    #
    import commands
    a11yEnabled = commands.getoutput(\
        "gconftool-2 --get /desktop/gnome/interface/accessibility")
    if a11yEnabled != "true":
        os.system("gconftool-2 --type bool --set " \
                  + "/desktop/gnome/interface/accessibility true")
        message = _("Accessibility has just been enabled for this session.")
        print message
        speech.speak(message)
        braille.displayMessage(message)
        message = _("Please logout and log back in and rerun orca.")
        print message
        speech.speak(message)
        braille.displayMessage(message)
        abort()

    start(registry) # waits until we stop the registry
    return 0

if __name__ == "__main__":
    sys.exit(main())
