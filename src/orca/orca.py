# Orca
#
# Copyright 2004-2007 Sun Microsystems Inc.
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

"""The main module for the Orca screen reader."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2007 Sun Microsystems Inc."
__license__   = "LGPL"

# We're going to force the name of the app to "orca" so pygtk
# will end up showing us as "orca" to the AT-SPI.  If we don't
# do this, the name can end up being "-c".  See bug 364452 at
# http://bugzilla.gnome.org/show_bug.cgi?id=364452 for more
# information.
#
import sys
sys.argv[0] = "orca"

try:
    # This can fail due to gtk not being available.  We want to
    # be able to recover from that if possible.  The main driver
    # for this is to allow "orca --text-setup" to work even if
    # the desktop is not running.
    #
    import gtk
except:
    pass

import getopt
import os
import signal
import string
import time

import atspi
import braille
import debug
import httpserver
import keynames
import keybindings
import mag
import orca_state
import platform
import rolenames
import settings
import speech

from input_event import BrailleEvent
from input_event import KeyboardEvent
from input_event import MouseButtonEvent
from input_event import InputEventHandler

from orca_i18n import _           # for gettext support

if settings.debugMemoryUsage:
    import gc
    gc.set_debug(gc.DEBUG_UNCOLLECTABLE
                 | gc.DEBUG_COLLECTABLE
                 | gc.DEBUG_INSTANCES
                 | gc.DEBUG_OBJECTS
                 | gc.DEBUG_SAVEALL)

# The user-settings module (see loadUserSettings).
#
_userSettings = None

# Command line options that override any other settings.
#
_commandLineSettings = {}

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

def setLocusOfFocus(event, obj, notifyPresentationManager=True):
    """Sets the locus of focus (i.e., the object with visual focus) and
    notifies the current presentation manager of the change.

    Arguments:
    - event: if not None, the Event that caused this to happen
    - obj: the Accessible with the new locus of focus.
    - notifyPresentationManager: if True, propagate this event
    """

    if obj == orca_state.locusOfFocus:
        return

    oldLocusOfFocus = orca_state.locusOfFocus
    if oldLocusOfFocus and not oldLocusOfFocus.valid:
        oldLocusOfFocus = None

    orca_state.locusOfFocus = obj
    if orca_state.locusOfFocus and not orca_state.locusOfFocus.valid:
        orca_state.locusOfFocus = None

    if orca_state.locusOfFocus:
        appname = ""
        if not orca_state.locusOfFocus.app:
            appname = "None"
        else:
            appname = "'" + orca_state.locusOfFocus.app.name + "'"

        debug.println(debug.LEVEL_FINE,
                      "LOCUS OF FOCUS: app=%s name='%s' role='%s'" \
                      % (appname,
                         orca_state.locusOfFocus.name,
                         orca_state.locusOfFocus.role))

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
            locusOfFocusChanged(event,
                                oldLocusOfFocus,
                                orca_state.locusOfFocus)

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
                speech.speak(_("Goodbye."))
                shutdown()
                return
        except: # could be a CORBA.COMM_FAILURE
            debug.printException(debug.LEVEL_FINEST)
            shutdown()
            return

def _onMouseButton(e):
    """Tracks mouse button events, stopping any speech in progress.

    Arguments:
    - e: at-spi event from the at-api registry
    """

    event = atspi.Event(e)
    orca_state.lastInputEvent = MouseButtonEvent(event)

    # A mouse button event looks like: mouse:button:1p, where the
    # number is the button number and the 'p' is either 'p' or 'r',
    # meaning pressed or released.  We only want to stop speech on
    # button presses.
    #
    if event.type.endswith("p"):
        speech.stop()

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
        speech.speak("Debug level all.")
    elif level == debug.LEVEL_FINEST:
        speech.speak("Debug level finest.")
    elif level == debug.LEVEL_FINER:
        speech.speak("Debug level finer.")
    elif level == debug.LEVEL_FINE:
        speech.speak("Debug level fine.")
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

    if event_string == "space":
        reply = True
    else:
        unicodeString = event_string.decode("UTF-8")
        reply = (len(unicodeString) == 1) \
                and (unicodeString.isalnum() or unicodeString.isspace())
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
                     'Shift_L', 'Shift_R', 'Meta_L', 'Meta_R' ]
    modifierKeys.extend(settings.orcaModifierKeys)

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

    reply = event_string in lockingKeys \
            and not event_string in settings.orcaModifierKeys
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

    actionKeys = [ "Return", "Escape", "Tab", "BackSpace", "Delete",
                   "Page_Up", "Page_Down", "Home", "End" ]

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

    # If this keyboard event was for an object like a password text
    # field, then don't echo it.
    #
    if orca_state.locusOfFocus \
        and (orca_state.locusOfFocus.role == rolenames.ROLE_PASSWORD_TEXT):
        return

    event_string = event.event_string
    debug.println(debug.LEVEL_FINEST,
                  "orca._keyEcho: string to echo: %s" % event_string)

    voices = settings.voices
    voice = voices[settings.DEFAULT_VOICE]

    lockState = None

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

        elif _isLockingKey(event_string):
            if not settings.enableLockingKeys:
                return

            modifiers = event.modifiers
            if event_string == "Caps_Lock":
                if modifiers & (1 << atspi.Accessibility.MODIFIER_SHIFTLOCK):
                    lockState = " " + _("off")
                else:
                    lockState = " " + _("on")

            elif event_string == "Num_Lock":
                # [[[TODO: richb - we are not getting a correct modifier
                # state value returned when Num Lock is turned off.
                # Commenting out the speaking of the bogus on/off state
                # until this can be fixed.]]]
                #
                #if modifiers & (1 << atspi.Accessibility.MODIFIER_NUMLOCK):
                #    event_string += " " + _("off")
                #else:
                #    event_string += " " + _("on")
                pass

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
        #
        event_string = keynames.getKeyName(event_string)

        if lockState:
            event_string += lockState

        debug.println(debug.LEVEL_FINEST,
                      "orca._keyEcho: speaking: %s" % event_string)

        # We keep track of the time as means to let others know that
        # we are probably echoing a key and should not be interrupted.
        #
        orca_state.lastKeyEchoTime = time.time()

        speech.speak(event_string, voice)

def _processKeyCaptured(event):
    """Called when a new key event arrives and orca_state.capturingKeys=True.
    (used for key bindings redefinition)
    """

    if event.type == 0:
        if _isModifierKey(event.event_string) \
               or event.event_string == "Return":
            pass
        elif event.event_string == "Escape":
            orca_state.capturingKeys = False
        else:
            # Translators: this is a spoken prompt letting the user know
            # Orca has recorded a new key combination (e.g., Alt+Ctrl+g)
            # based upon their input.
            #
            speech.speak(_("Key captured: %s. Press enter to confirm.") \
                         % str(event.event_string))
            orca_state.lastCapturedKey = event
    else:
        pass
    return False

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
    global _orcaModifierPressed

    orca_state.lastInputEventTimestamp = event.timestamp

    # Log the keyboard event for future playback, if desired.
    # Note here that the key event_string being output is
    # exactly what we received.  The KeyboardEvent object,
    # however, will translate the event_string for control
    # characters to their upper case ASCII equivalent.
    #
    string = atspi.KeystrokeListener.keyEventToString(event)
    if _recordingKeystrokes and _keystrokesFile \
       and (event.event_string != "Pause") \
       and (event.event_string != "F21"):
        _keystrokesFile.write(string + "\n")
    debug.printInputEvent(debug.LEVEL_FINE, string)

    keyboardEvent = KeyboardEvent(event)

    # See if this is one of our special Orca modifier keys.
    #
    # [[[TODO: WDW - Note that just looking at the keycode should
    # suffice, but there is a "feature" in the Java Access Bridge
    # where it chooses to emit Java platform-independent keycodes
    # instead of the keycodes for the base platform:
    #
    # http://bugzilla.gnome.org/show_bug.cgi?id=106004
    # http://bugzilla.gnome.org/show_bug.cgi?id=318615
    #
    # So...we need to workaround this problem.
    #
    # If you make the following expression True we will get a positive
    # match for all keysyms associated with a given keysym specified
    # as an Orca modifier key.
    #
    # For example, assume the Orca modifier is set to \ for some
    # reason.  The key that has \ on it produces \ without the Shift
    # key and | with the Shift key.  If the following expression is
    # True, both the \ and | will be viewed as the Orca modifier.  If
    # the following expression is False, only the \ will be viewed as
    # the Orca modifier (i.e., Shift+\ will still function as the |
    # character).  In general, I think we want to avoid sucking in all
    # possible keysyms because it can have unexpected results.]]]
    #
    if False:
        allPossibleKeysyms = []
        for keysym in settings.orcaModifierKeys:
            allPossibleKeysyms.extend(keybindings.getAllKeysyms(keysym))
    else:
        allPossibleKeysyms = settings.orcaModifierKeys

    isOrcaModifier = allPossibleKeysyms.count(keyboardEvent.event_string) > 0

    if event.type == atspi.Accessibility.KEY_PRESSED_EVENT:
        # Key presses always interrupt speech.
        #
        speech.stop()

        # If learn mode is enabled, it will echo the keys.
        #
        if not settings.learnModeEnabled:
            _keyEcho(keyboardEvent)

        # We treat the Insert key as a modifier - so just swallow it and
        # set our internal state.
        #
        if isOrcaModifier:
            _orcaModifierPressed = True

    elif isOrcaModifier \
        and (keyboardEvent.type == atspi.Accessibility.KEY_RELEASED_EVENT):
        _orcaModifierPressed = False

    if _orcaModifierPressed:
        keyboardEvent.modifiers = keyboardEvent.modifiers \
                                  | (1 << settings.MODIFIER_ORCA)


    # Orca gets first stab at the event.  Then, the presenter gets
    # a shot. [[[TODO: WDW - might want to let the presenter try first?
    # The main reason this is staying as is is that we may not want
    # scripts to override fundamental Orca key bindings.]]]
    #
    consumed = False
    try:
        if orca_state.capturingKeys:
            _processKeyCaptured(keyboardEvent)
        else:
            consumed = _keyBindings.consumeKeyboardEvent(None, keyboardEvent)
            if (not consumed) and (_currentPresentationManager >= 0):
                consumed = _PRESENTATION_MANAGERS[_currentPresentationManager].\
                           processKeyboardEvent(keyboardEvent)
            if (not consumed) and settings.learnModeEnabled:
                if keyboardEvent.type \
                    == atspi.Accessibility.KEY_PRESSED_EVENT:
                    clickCount = orca_state.activeScript.getClickCount(\
                                                orca_state.lastInputEvent,
                                                keyboardEvent)
                    if clickCount == 2:
                        orca_state.activeScript.phoneticSpellCurrentItem(\
                            keyboardEvent.event_string)
                    else:
                        # Check to see if there are localized words to be
                        # spoken for this key event.
                        #
                        braille.displayMessage(keyboardEvent.event_string)
                        event_string = keyboardEvent.event_string
                        event_string = keynames.getKeyName(event_string)
                        speech.speak(event_string)
                consumed = True
    except:
        debug.printException(debug.LEVEL_SEVERE)

    orca_state.lastInputEvent = keyboardEvent

    # If this is a key event for a non-modifier key, save a handle to it.
    # This is needed to help determine user actions when a multi-key chord
    # has been pressed, and we might get the key events in different orders.
    # See comment #15 of bug #435201 for more details.
    #
    if not _isModifierKey(keyboardEvent.event_string):
        orca_state.lastNonModifierKeyEvent = keyboardEvent

    return consumed or isOrcaModifier

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

    # [[[TODO: WDW - probably should add braille bindings to this module.]]]

    consumed = False

    # Braille key presses always interrupt speech.
    #
    speech.stop()

    event = BrailleEvent(command)
    orca_state.lastInputEvent = event

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
        # Translators: this is a spoken prompt letting the user know
        # that speech synthesis has been turned back on.
        #
        speech.speak(_("Speech enabled."))
    else:
        # Translators: this is a spoken prompt letting the user know
        # that speech synthesis has been temporarily turned off.
        #
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
    #
    httpserver.shutdown()
    speech.shutdown()
    braille.shutdown()
    mag.shutdown()

    if _currentPresentationManager >= 0:
        _PRESENTATION_MANAGERS[_currentPresentationManager].deactivate()

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

    # If any settings were added to the command line, they take
    # precedence over everything else.
    #
    for key in _commandLineSettings:
        settings.__dict__[key] = _commandLineSettings[key]

    if settings.enableSpeech:
        try:
            speech.init()
            if reloaded:
                # Translators: there is a keystroke to reload the user
                # preferences.  This is a spoken prompt to let the user
                # know when the preferences has been reloaded.
                #
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
            braille.init(_processBrailleEvent, settings.tty)
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

    # We don't want the Caps_Lock modifier to act as a locking
    # modifier if it used as the Orca modifier key.  In addition, if
    # the KP_Insert key is used as the Orca modifier key, we want to
    # make sure we clear any other keysyms that might be in use on
    # that key since we won't be able to detect them as being the Orca
    # modifier key.  For example, KP_Insert produces "KP_Insert" when
    # pressed by itself, but Shift+KP_Insert produces "0".
    #
    # The original values are saved/reset in the orca shell script.
    #
    # [[[TODO: WDW - we probably should just to a 'xmodmap -e "%s = %s"'
    # for all of the orcaModifierKeys, but saving/restoring the values
    # becomes a little more difficult.  If we could assume a writeable
    # filesystem (we cannot), we could do a 'xmodmap -pke > /tmp/foo'
    # to save the keymap and a 'xmodmap /tmp/foo' to restore it.
    # For now, we'll just look at the Orca modifier keys we support
    # (Caps Lock, KP_Insert, and Insert).]]]
    #
    for keyName in settings.orcaModifierKeys:
        if keyName == "Caps_Lock":
            os.system('xmodmap -e "clear Lock"')
        if keyName in ["Caps_Lock", "KP_Insert", "Insert"]:
            command = 'xmodmap -e "keysym %s = %s"' % (keyName, keyName)
            os.system(command)

    if _currentPresentationManager >= 0:
        _PRESENTATION_MANAGERS[_currentPresentationManager].activate()

    _showMainWindowGUI()

    httpserver.init()

    return True

def _showAppPreferencesGUI(script=None, inputEvent=None):
    """Displays the user interace to configure the settings for a
    specific applications within Orca and set up those app-specific
    user preferences using a GUI.

    Returns True to indicate the input event has been consumed.
    """

    try:
        module = __import__(settings.appGuiPreferencesModule,
                            globals(),
                            locals(),
                            [''])
        module.showPreferencesUI()
    except:
        debug.printException(debug.LEVEL_SEVERE)
        pass

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

def _showMainWindowGUI(script=None, inputEvent=None):
    """Displays the Orca main window.

    Returns True to indicate the input event has been consumed.
    """

    try:
        module = __import__(settings.mainWindowModule,
                            globals(),
                            locals(),
                            [''])
        if settings.showMainWindow:
            module.showMainUI()
        else:
            module.hideMainUI()
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

def quitOrca(script=None, inputEvent=None):
    """Quit Orca. Check if the user wants to confirm this action.
    If so, show the confirmation GUI otherwise just shutdown.

    Returns True to indicate the input event has been consumed.
    """

    if settings.quitOrcaNoConfirmation:
        shutdown()
    else:
        try:
            module = __import__(settings.quitModule,
                                globals(),
                                locals(),
                                [''])
            module.showQuitUI()
        except:
            debug.printException(debug.LEVEL_SEVERE)
            pass

    return True

def _showFindGUI(script=None, inputEvent=None):
    """Displays the user interace to perform an Orca Find.

    Returns True to indicate the input event has been consumed.
    """

    try:
        module = __import__(settings.findModule,
                            globals(),
                            locals(),
                            [''])
        module.showFindUI()
    except:
        debug.printException(debug.LEVEL_SEVERE)
        pass

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

    # Do not hang on initialization if we can help it.
    #
    if settings.timeoutCallback and (settings.timeoutTime > 0):
        signal.signal(signal.SIGALRM, settings.timeoutCallback)
        signal.alarm(settings.timeoutTime)

    # Note that we have moved the Orca specific keybindings to the default
    # script, so _keyBindings is currently empty. The logic is retained
    # here, just in case we wish to reinstate them in the future.
    #
    _keyBindings = keybindings.KeyBindings()

    # Create and load an app's script when it is added to the desktop
    #
    registry.registerEventListener(_onChildrenChanged,
                                   "object:children-changed:")

    # We also want to stop speech when a mouse button is pressed.
    #
    registry.registerEventListener(_onMouseButton,
                                   "mouse:button")

    loadUserSettings()

    registry.registerKeystrokeListeners(_processKeyboardEvent)

    if settings.timeoutCallback and (settings.timeoutTime > 0):
        signal.alarm(0)

    _initialized = True
    return True

def start(registry):
    """Starts Orca.
    """

    global _PRESENTATION_MANAGERS

    if not _initialized:
        init(registry)

    # Do not hang on startup if we can help it.
    #
    if settings.timeoutCallback and (settings.timeoutTime > 0):
        signal.signal(signal.SIGALRM, settings.timeoutCallback)
        signal.alarm(settings.timeoutTime)

    if not _PRESENTATION_MANAGERS:
        import focus_tracking_presenter
        _PRESENTATION_MANAGERS = \
            [focus_tracking_presenter.FocusTrackingPresenter()]

    _switchToPresentationManager(0) # focus_tracking_presenter

    if settings.timeoutCallback and (settings.timeoutTime > 0):
        signal.alarm(0)

    registry.start()

def abort(exitCode=1):
    os._exit(exitCode)

def timeout(signum=None, frame=None):
    debug.println(debug.LEVEL_SEVERE,
                  "TIMEOUT: something has hung.  Aborting.")
    debug.printStack(debug.LEVEL_ALL)
    abort(50)

def shutdown(script=None, inputEvent=None):
    """Exits Orca.  Unregisters any event listeners and cleans up.  Also
    quits the bonobo main loop and resets the initialized state to False.

    Returns True if the shutdown procedure ran or False if this module
    was never initialized.
    """

    global _initialized

    if not _initialized:
        return False

    # Try to say goodbye, but be defensive if something has hung.
    #
    if settings.timeoutCallback and (settings.timeoutTime > 0):
        signal.signal(signal.SIGALRM, settings.timeoutCallback)
        signal.alarm(settings.timeoutTime)

    # Translators: this is what Orca speaks and brailles when it quits.
    #
    speech.speak(_("Goodbye."))
    braille.displayMessage(_("Goodbye."))

    # Deregister our event listeners
    #
    registry = atspi.Registry()
    registry.deregisterEventListener(_onChildrenChanged,
                                     "object:children-changed:")
    registry.deregisterEventListener(_onMouseButton,
                                     "mouse:button")

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

    if settings.timeoutCallback and (settings.timeoutTime > 0):
        signal.alarm(0)

    _initialized = False
    return True

exitCount = 0
def shutdownOnSignal(signum, frame):
    global exitCount

    debug.println(debug.LEVEL_ALL,
                  "Shutting down and exiting due to signal = %d" \
                  % signum)

    debug.println(debug.LEVEL_ALL, "Current stack is:")
    debug.printStack(debug.LEVEL_ALL)

    # Well...we'll try to exit nicely, but if we keep getting called,
    # something bad is happening, so just quit.
    #
    if exitCount:
        abort(signum)
    else:
        exitCount += 1

    # Try to do a graceful shutdown if we can.
    #
    if settings.timeoutCallback and (settings.timeoutTime > 0):
        signal.signal(signal.SIGALRM, settings.timeoutCallback)
        signal.alarm(settings.timeoutTime)

    try:
        if _initialized:
            shutdown()
        else:
            # We always want to try to shutdown speech since the
            # speech servers are very persistent about living.
            #
            speech.shutdown()
            shutdown()
        cleanExit = True
    except:
        cleanExit = False

    if settings.timeoutCallback and (settings.timeoutTime > 0):
        signal.alarm(0)

    if not cleanExit:
        abort(signum)

def abortOnSignal(signum, frame):
    debug.println(debug.LEVEL_ALL,
                  "Aborting due to signal = %d" \
                  % signum)
    abort(signum)

def usage():
    """Prints out usage information."""
    print "Usage: orca [OPTION...]"
    print
    print "-?, --help                   Show this help message"
    print "-v, --version                %s" % platform.version
    print "-s, --setup, --gui-setup     Set up user preferences"
    print "-t, --text-setup             Set up user preferences (text version)"
    print "-n, --no-setup               Skip set up of user preferences"
    print "-u, --user-prefs-dir=dirname Use alternate directory for user preferences"
    print "-e, --enable=[speech|braille|braille-monitor|magnifier|main-window] Force use of option"
    print "-d, --disable=[speech|braille|braille-monitor|magnifier|main-window] Prevent use of option"
    print "-q, --quit                   Quits Orca (if shell script used)"
    print
    print "If Orca has not been previously set up by the user, Orca\nwill automatically launch the preferences set up unless\nthe -n or --no-setup option is used."
    print
    print "Report bugs to orca-list@gnome.org."
    pass

def main():
    """The main entry point for Orca.  The exit codes for Orca will
    loosely be based on signals, where the exit code will be the
    signal used to terminate Orca (if a signal was used).  Otherwise,
    an exit code of 0 means normal completion and an exit code of 50
    means Orca exited because of a hang."""

    global _commandLineSettings

    # Method to call when we think something might be hung.
    #
    settings.timeoutCallback = timeout

    # Various signal handlers we want to listen for.
    #
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
        if gtk.gdk.display_get_default():
            desktopRunning = True
    except:
        pass

    # Parse the command line options.
    #
    # Run the preferences setup if the user has specified
    # "--setup" or "--text-setup" on the command line.  If the
    # desktop is not running, we will fallback to the console-based
    # method as appropriate.
    #
    bypassSetup     = False
    setupRequested  = False
    showGUI         = False

    # We hack a little here because the shell script to start orca can
    # conflate all of command line arguments into one string, which is
    # not what we want.  We detect this by seeing if the length of the
    # argument list is 1.
    #
    arglist = sys.argv[1:]
    if len(arglist) == 1:
        arglist = arglist[0].split()

    try:
        # ? is for help
        # e is for enabling a feature
        # d is for disabling a feature
        # h is for help
        # u is for alternate user preferences location
        # s is for setup
        # n is for no setup
        # t is for text setup
        # v is for version
        #
        opts, args = getopt.getopt(
            arglist,
            "?stnvd:e:u:",
            ["help",
             "user-prefs-dir=",
             "enable=",
             "disable=",
             "setup",
             "gui-setup",
             "text-setup",
             "no-setup",
             "version"])
        for opt, val in opts:
            if opt in ("-u", "--user-prefs-dir"):
                userPrefsDir = val.strip();
                try:
                    os.chdir(userPrefsDir)
                    settings.userPrefsDir = userPrefsDir
                except:
                    debug.printException(debug.LEVEL_FINEST)

            if opt in ("-e", "--enable"):
                feature = val.strip()
                if feature == "speech":
                    _commandLineSettings["enableSpeech"] = True
                elif feature == "braille":
                    _commandLineSettings["enableBraille"] = True
                elif feature == "braille-monitor":
                    _commandLineSettings["enableBrailleMonitor"] = True
                elif feature == "magnifier":
                    _commandLineSettings["enableMagnifier"] = True
                elif feature == "main-window":
                    _commandLineSettings["showMainWindow"] = True
                else:
                    usage()
                    os._exit(2)

            if opt in ("-d", "--disable"):
                feature = val.strip()
                if feature == "speech":
                    _commandLineSettings["enableSpeech"] = False
                elif feature == "braille":
                    _commandLineSettings["enableBraille"] = False
                elif feature == "braille-monitor":
                    _commandLineSettings["enableBrailleMonitor"] = False
                elif feature == "magnifier":
                    _commandLineSettings["enableMagnifier"] = False
                elif feature == "main-window":
                    _commandLineSettings["showMainWindow"] = False
                else:
                    usage()
                    os._exit(2)

            if opt in ("-s", "--gui-setup", "--setup"):
                setupRequested = True
                showGUI = desktopRunning
            if opt in ("-t", "--text-setup"):
                setupRequested = True
                showGUI = False
            if opt in ("-n", "--no-setup"):
                bypassSetup = True
            if opt in ("-?", "--help"):
                usage()
                os._exit(0)
            if opt in ("-v", "--version"):
                print "Orca %s" % platform.version
                os._exit(0)
    except:
        debug.printException(debug.LEVEL_OFF)
        usage()
        os._exit(2)

    # Do not run Orca if accessibility has not been enabled.
    # We do allow, however, one to force Orca to run via the
    # "-n" switch.  The main reason is so that things such
    # as accessible login can work -- in those cases, the gconf
    # setting is typically not set since the gdm user does not
    # have a home.
    #
    a11yEnabled = settings.isAccessibilityEnabled()
    if (not bypassSetup) and (not a11yEnabled):
        _showPreferencesConsole()
        abort()

    if setupRequested and (not bypassSetup) and (not showGUI):
        _showPreferencesConsole()

    if not desktopRunning:
        print "Cannot start Orca because it cannot connect"
        print "to the Desktop.  Please make sure the DISPLAY"
        print "environment variable has been set."
        return 1

    userprefs = settings.userPrefsDir
    sys.path.insert(0, userprefs)
    sys.path.insert(0, '') # current directory

    registry = atspi.Registry()
    init(registry)

    try:
        message = _("Welcome to Orca.")
        speech.speak(message)
        braille.displayMessage(message)
    except:
        debug.printException(debug.LEVEL_SEVERE)

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

    start(registry) # waits until we stop the registry
    return 0

if __name__ == "__main__":
    sys.exit(main())
