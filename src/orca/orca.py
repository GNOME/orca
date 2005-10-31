# Orca
#
# Copyright 2004-2005 Sun Microsystems Inc.
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

import gtk
import os, signal, sys

import a11y
import braille
import core
import debug
import focus_tracking_presenter
import hierarchical_presenter
import kbd
import keybindings
#import mag - [[[TODO: WDW - disable until I can figure out how to
#             resolve the GNOME reference in mag.py.  This is logged
#             as bugzilla bug 319643.]]]
import settings
import speech

from input_event import BrailleEvent
from input_event import KeyboardEvent
from input_event import InputEventHandler

from orca_i18n import _           # for gettext support

# If True, this module has been initialized.
#
_initialized = False

# Keybindings that Orca itself cares about.
#
_keybindings = None

# A new modifier to use (currently bound to the "Insert" key) to represent
# special Orca key sequences.
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

# The known presentation managers.
#
_PRESENTATION_MANAGERS = [focus_tracking_presenter,
                          hierarchical_presenter]

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


def _switchToNextPresentationManager(inputEvent=None):
    """Switches to the next presentation manager.

    Arguments:
    - inputEvent: the InputEvent instance that caused this to be called.

    Returns True indicating the event should be consumed.
    """

    global _currentPresentationManager

    _switchToPresentationManager(_currentPresentationManager + 1)

    return True

    
########################################################################
#                                                                      #
# METHODS TO HANDLE APPLICATION LIST AND FOCUSED OBJECTS               #
#                                                                      #
########################################################################

# List of all the running apps we know about.  Each element is a Python
# Accessible instance.
#
apps = []

# The Accessible that has visual focus.
#
locusOfFocus = None

def _buildAppList():
    """Retrieves the list of currently running apps for the desktop and
    populates the apps list attribute with these apps.
    """
    
    global apps

    debug.println(debug.LEVEL_FINEST,
                  "orca._buildAppList...")

    apps = []

    i = 0
    while i < core.desktop.childCount:
        acc = core.desktop.getChildAtIndex(i)
        try:
            app = a11y.makeAccessible(acc)
            if not app is None:
                apps.insert(0, app)
        except:
            debug.printException(debug.LEVEL_SEVERE)
        i += 1

    debug.println(debug.LEVEL_FINEST,
                  "...orca._buildAppList")


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
        if locusOfFocus.app is None:
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
    
    global apps
    
    for app in apps:
        i = 0
        while i < app.childCount:
            state = app.child(i).state
            if state.count(core.Accessibility.STATE_ACTIVE) > 0:
                return app.child(i)
            i += 1
            debug.println(debug.LEVEL_FINEST,
                          "orca.findActiveWindow %d" % i)


    return None


def onChildrenChanged(e):
    """Tracks children-changed events on the desktop to determine when
    apps start and stop.

    Arguments:
    - e: at-spi event from the at-api registry
    """
    
    if e.source == core.desktop:

        # If the desktop is empty, the user has logged out-- shutdown Orca
        #
        try:
            if core.desktop.childCount == 0:
                speech.say(_("User logged out - shutting down."))
                shutdown()
                return
        except: # could be a CORBA.COMM_FAILURE
            debug.printException(debug.LEVEL_FINEST)
            shutdown()
            return            

        # [[[TODO: WDW - Note the call to _buildAppList - that will update the
        # apps[] list.  If this logic is changed in the future, the apps list
        # will most likely needed to be updated here.]]]
        #
        _buildAppList()


########################################################################
#                                                                      #
# METHODS FOR PRE-PROCESSING AND MASSAGING BRAILLE EVENTS.             #
#                                                                      #
########################################################################
    
def processBrailleEvent(command):
    """Called whenever a  key is pressed on the Braille display.
    
    Arguments:
    - command: the BrlAPI command for the key that was pressed.

    Returns True if the event was consumed; otherwise False
    """

    global lastInputEvent
    
    # [[[TODO: WDW - probably should add braille bindings to this module.]]]
    
    consumed = False

    # Braille key presses always interrupt speech - If say all mode is
    # enabled, a key press stops it as well and postions the caret at
    # where the speech stopped.
    #
    if speech.sayAllEnabled:
        speech.stopSayAll()
    else:
        speech.stop()

    event = BrailleEvent(command)
    lastInputEvent = event
    
    try:
        consumed = _PRESENTATION_MANAGERS[_currentPresentationManager].\
                   processBrailleEvent(event)
    except:
        debug.printException(debug.LEVEL_SEVERE)

    if (not consumed) and settings.getSetting("learnModeEnabled", False):
        # [[[TODO: WDW - add a toString to braille.py.]]]
        consumed = True

    return consumed


########################################################################
#                                                                      #
# DEBUG support.                                                       #
#                                                                      #
########################################################################
    
def printApps(inputEvent=None):
    """Prints a list of all applications to stdout

    Arguments:
    - inputEvent: the InputEvent instance that caused this to be called.

    Returns True indicating the event should be consumed.
    """

    level = debug.LEVEL_OFF
    
    debug.println(level, "There are %d Accessible applications" % len(apps))
    for app in apps:
        a11y.printDetails(level, "  App: ", app, False)
        i = 0
        while i < app.childCount:
            child = app.child(i)
            a11y.printDetails(level, "    Window: ", child, False)
            if child.parent != app:
                debug.println(level,
                              "      WARNING: child's parent is not app!!!")
            i += 1

    return True


def printAccessibleTree(level, indent, root):
    a11y.printDetails(level, indent, root, False)
    i = 0
    while i < root.childCount:
        child = root.child(i)
        if child == root:
            debug.println(level,
                          indent + "  " + "WARNING CHILD == PARENT!!!")
        elif child is None:
            debug.println(level,
                          indent + "  " + "WARNING CHILD IS NONE!!!")
        elif child.parent != root:
            debug.println(level,
                          indent + "  " + "WARNING CHILD.PARENT != PARENT!!!")
        else:
            printAccessibleTree(level, indent + "  ", child)
        i += 1

    
def printAccessiblePaintedTree(level, indent, root):
    a11y.printDetails(level, indent, root, False)

    extents = root.extents
    if extents:
        debug.println(level, \
                      indent + " extents: (x=%d y=%d w=%d h=%d)" \
                      % (extents.x, extents.y, extents.width, extents.height))
        
    #if root.text:
    #    extents = root.text.getCharacterExtents(0,0)
    #    debug.println(level, \
    #                  indent + " text extents: (x=%d y=%d w=%d h=%d)" \
    #                  % (extents[0], extents[1], extents[2], extents[3]))

    i = 0
    while i < root.childCount:
        child = root.child(i)
        if child == root:
            debug.println(level,
                          indent + "  " + "WARNING CHILD == PARENT!!!")
        elif child is None:
            debug.println(level,
                          indent + "  " + "WARNING CHILD IS NONE!!!")
        elif child.parent != root:
            debug.println(level,
                          indent + "  " + "WARNING CHILD.PARENT != PARENT!!!")
        elif child.state.count(core.Accessibility.STATE_SHOWING):    
            printAccessiblePaintedTree(level, indent + "  ", child)
        i += 1


def printActiveApp(inputEvent=None):
    """Prints the active application.

    Arguments:
    - inputEvent: the key event (if any) which caused this to be called.

    Returns True indicating the event should be consumed.
    """
    
    level = debug.LEVEL_OFF
    
    window = findActiveWindow()
    if window is None:
        debug.println(level, "Active application: None")
    else:
        app = window.app
        if app is None:
            debug.println(level, "Active application: None")
        else:
            debug.println(level, "Active application: %s" % app.name)
            printAccessibleTree(level, "  ", findActiveWindow())

    return True


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


def toggleKeystrokeRecording(inputEvent=None):
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
# METHODS FOR HANDLING THE INITIALIZATION, SHUTDOWN, AND USE.          #
#                                                                      #
########################################################################

def enterLearnMode(inputEvent=None):
    """Turns learn mode on.  The user must press the escape key to exit
    learn mode.

    Returns True to indicate the input event has been consumed.
    """

    speech.say(
        _("Entering learn mode.  Press any key to hear its function. " \
          + "To exit learn mode, press the escape key."))
    braille.displayMessage(_("Learn mode.  Press escape to exit."))
    settings.setLearnModeEnabled(True)
    return True


def exitLearnMode(inputEvent=None):
    """Turns learn mode off.

    Returns True to indicate the input event has been consumed.
    """

    speech.say(_("Exiting learn mode."))
    braille.displayMessage(_("Exiting learn mode."))
    settings.setLearnModeEnabled(False)
    return True


def init():
    """Initialize the orca module, which initializes a11y, kbd, speech,
    and braille modules.  Also builds up the application list, registers
    for at-spi events, and creates scripts for all known applications.

    Returns True if the initialization procedure has run, or False if this
    module has already been initialized.
    """
    
    global _initialized
    global _keybindings
    global apps
    
    if _initialized:
        return False

    a11y.init()
    
    kbd.init(processKeyboardEvent)

    _keybindings = keybindings.KeyBindings()
    
    enterLearnModeHandler = InputEventHandler(\
        enterLearnMode,
        _("Enters learn mode.  Press escape to exit learn mode."))
    _keybindings.add(keybindings.KeyBinding("F1", \
                                            1 << MODIFIER_ORCA, \
                                            1 << MODIFIER_ORCA, \
                                            enterLearnModeHandler))

    decreaseSpeechRateHandler = InputEventHandler(\
        speech.decreaseSpeechRate,
        _("Decreases the speech rate."))
    _keybindings.add(keybindings.KeyBinding("Left", \
                                            1 << MODIFIER_ORCA, \
                                            1 << MODIFIER_ORCA,
                                            decreaseSpeechRateHandler))

    increaseSpeechRateHandler = InputEventHandler(\
        speech.increaseSpeechRate,
        _("Increases the speech rate."))
    _keybindings.add(keybindings.KeyBinding("Right", \
                                            1 << MODIFIER_ORCA, \
                                            1 << MODIFIER_ORCA,
                                            increaseSpeechRateHandler))
    
    shutdownHandler = InputEventHandler(shutdown, _("Quits Orca"))
    _keybindings.add(keybindings.KeyBinding("F12", \
                                            0, \
                                            0,
                                            shutdownHandler))
    _keybindings.add(keybindings.KeyBinding("SunF37", \
                                            0, \
                                            0,
                                            shutdownHandler))

    keystrokeRecordingHandler = InputEventHandler(\
        toggleKeystrokeRecording,
        _("Toggles keystroke recording on and off."))
    _keybindings.add(keybindings.KeyBinding("Pause", \
                                            0, \
                                            0,
                                            keystrokeRecordingHandler))

    listAppsHandler = InputEventHandler(
        printApps,
        _("Prints a debug listing of all known applications to the console where Orca is running."))
    _keybindings.add(keybindings.KeyBinding("F5", \
                                            1 << MODIFIER_ORCA, \
                                            1 << MODIFIER_ORCA,
                                            listAppsHandler))

    printActiveAppHandler = InputEventHandler(\
        printActiveApp,
        _("Prints debug information about the currently active application to the console where Orca is running."))
    _keybindings.add(keybindings.KeyBinding("F6", \
                                            1 << MODIFIER_ORCA, \
                                            1 << MODIFIER_ORCA,
                                            printActiveAppHandler))

    nextPresentationManagerHandler = InputEventHandler(\
        _switchToNextPresentationManager,
        _("Switches to the next presentation manager."))
    _keybindings.add(keybindings.KeyBinding("F8", \
                                            1 << MODIFIER_ORCA, \
                                            1 << MODIFIER_ORCA,
                                            nextPresentationManagerHandler))

    if settings.getSetting("useSpeech", True):
        try:
            speech.init()
            debug.println(debug.LEVEL_CONFIGURATION,
                          "Speech module has been initialized.")
        except:
            debug.println(debug.LEVEL_SEVERE,
                          "Could not initialize connection to speech.")
    else:
        debug.println(debug.LEVEL_CONFIGURATION,
                      "Speech module has NOT been initialized.")
        
    if settings.getSetting("useBraille", False):
        try:
            braille.init(processBrailleEvent, 7)
        except:
            debug.println(debug.LEVEL_SEVERE,
                          "Could not initialize connection to braille.")

    if settings.getSetting("useMagnifier", False):
        try:
            mag.init()
            debug.println(debug.LEVEL_CONFIGURATION,
                          "Magnification module has been initialized.")
        except:
            debug.println(debug.LEVEL_SEVERE,
                          "Could not initialize connection to magnifier.")
    else:
        debug.println(debug.LEVEL_CONFIGURATION,
                      "Magnification module has NOT been initialized.")

    # Build list of accessible apps.
    #
    _buildAppList()

    # Create and load an app's script when it is added to the desktop
    #
    core.registerEventListener(onChildrenChanged, "object:children-changed:")

    _initialized = True
    return True


def start():
    """Starts Orca and also the bonobo main loop.

    Returns False only if this module has not been initialized.
    """

    global _initialized
    
    if not _initialized:
        return False

    try:
        speech.say(_("Welcome to Orca."))
        braille.displayMessage(_("Welcome to Orca."))
    except:
        debug.printException(debug.LEVEL_SEVERE)
    
    _switchToPresentationManager(0) # focus_tracking_presenter

    core.bonobo.main()


def shutdown(inputEvent=None):
    """Exits Orca.  Unregisters any event listeners and cleans up.  Also
    quits the bonobo main loop and resets the initialized state to False.

    Returns True if the shutdown procedure ran or False if this module
    was never initialized.
    """
    
    global _initialized
    global apps

    if not _initialized:
        return False

    speech.say(_("goodbye."))
    braille.displayMessage(_("Goodbye."))

    # Deregister our event listeners
    #
    core.unregisterEventListener(onChildrenChanged,
                                 "object:children-changed:")

    if _currentPresentationManager >= 0:
        _PRESENTATION_MANAGERS[_currentPresentationManager].deactivate()


    # Shutdown all the other support.
    #
    kbd.shutdown() # automatically unregisters processKeyboardEvent
    a11y.shutdown()
    if settings.getSetting("useSpeech", True):
        speech.shutdown()
    if settings.getSetting("useBraille", False):
        braille.shutdown();
    if settings.getSetting("useMagnifier", False):
        mag.shutdown();

    core.bonobo.main_quit()

    _initialized = False
    return True


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
    
    if _display is None:
        try:
            _display = gtk.gdk.display_get_default()
        except:
            debug.printException(debug.LEVEL_FINEST)
            _display = gtk.gdk.display(":0")

        if _display is None:
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
            _visibleRectangle = component.getExtents(0) # coord type = screen
            drawOutline(_visibleRectangle.x, _visibleRectangle.y,
                        _visibleRectangle.width, _visibleRectangle.height,
                        erasePrevious)
    else:
        drawOutline(-1, 0, 0, 0, erasePrevious)
        

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

# The InputEvent instance representing the last input event.
#
lastInputEvent = None

# True if the insert key is currently pressed.  We will use the insert
# key as a modifier for Orca, and it will be presented as the "insert"
# modifier string.
#
_insertPressed = False


def _keyEcho(key):
    """If the keyEcho setting is enabled, echoes the key via speech.
    Uppercase keys will be spoken using the "uppercase" voice style,
    whereas lowercase keys will be spoken using the "default" voice style.

    Arguments:
    - key: a string representing the key name to echo.
    """
    
    if not settings.getSetting("keyEcho", False):
        return
    if key.isupper():
        speech.say(key, "uppercase")
    else:
        speech.say(key)

def processKeyboardEvent(event):
    """The primary key event handler for Orca.  Keeps track of various
    attributes, such as the lastInputEvent and insertPressed.  Also calls
    keyEcho as well as any function that may exist in the _keybindings
    dictionary for the key event.  This method is called synchronously
    from the at-spi registry and should be performant.  In addition, it
    must return True if it has consumed the event (and False if not).
    
    Arguments:
    - event: an at-spi DeviceEvent

    Returns True if the event should be consumed.
    """
    
    global lastInputEvent
    global _insertPressed
    global _currentPresentationManager
    global _recordingKeystrokes
    global _keystrokesFile
    
    keystring = ""

    # Log the keyboard event for future playback, if desired.
    #
    string = kbd.keyEventToString(event)
    if _recordingKeystrokes and _keystrokesFile \
       and (event.event_string != "Pause"):
        _keystrokesFile.write(string + "\n")
    debug.printInputEvent(debug.LEVEL_FINE, string)
    
    if event.type == core.Accessibility.KEY_PRESSED_EVENT:

        # Key presses always interrupt speech - If say all mode is
        # enabled, a key press stops it as well and postions the
        # caret at where the speech stopped.
        #
        if speech.sayAllEnabled:
            speech.stopSayAll()
        else:
            speech.stop()

        # The control characters come through as control characters,
        # so we just turn them into their ASCII equivalent.  NOTE that
        # the upper case ASCII characters will be used (e.g., ctrl+a
        # will be turned into the string "A").  All these checks here
        # are to just do some sanity checking before doing the
        # conversion. [[[WDW - this is making assumptions about
        # mapping ASCII control characters to to UTF-8.]]]
        #
        if (event.modifiers & (1 << core.Accessibility.MODIFIER_CONTROL)) \
           and (not event.is_text) and (len(event.event_string) == 1):
            value = ord(event.event_string[0])
            if value < 32:
                event_string = chr(value + 0x40)

        _keyEcho(event.event_string)    
    
        # We treat the Insert key as a modifier - so just swallow it and
        # set our internal state.
        #
        if event.event_string == "Insert":
            _insertPressed = True
            return True

    elif event.type == core.Accessibility.KEY_RELEASED_EVENT \
         and (event.event_string == "Insert"):
        _insertPressed = False
        return True
        
    # Orca gets first stab at the event.  Then, the presenter gets
    # a shot. [[[TODO: WDW - might want to let the presenter try first?
    # The main reason this is staying as is is that we may not want
    # scripts to override fundamental Orca key bindings.]]]
    #
    keyboardEvent = KeyboardEvent(event)
    if _insertPressed:
        keyboardEvent.modifiers |= (1 << MODIFIER_ORCA)

    consumed = _keybindings.consumeKeyboardEvent(keyboardEvent)
    if (not consumed) and (_currentPresentationManager >= 0):
        consumed = _PRESENTATION_MANAGERS[_currentPresentationManager].\
                   processKeyboardEvent(keyboardEvent)
        
    if (not consumed) and settings.getSetting("learnModeEnabled", False):
        if event.type == core.Accessibility.KEY_PRESSED_EVENT:
            braille.displayMessage(event.event_string)
            speech.say(event.event_string)
        elif (event.type == core.Accessibility.KEY_RELEASED_EVENT) \
             and (event.event_string == "Escape"):
            exitLearnMode(keyboardEvent)
        consumed = True
            
    lastInputEvent = keyboardEvent

    return consumed


def shutdownAndExit(signum, frame):
    print "Goodbye."
    try:
	shutdown()
    except:
        pass
    sys.exit()


def main():
    userprefs = os.path.join (os.environ["HOME"], ".orca")
    sys.path.insert (0, userprefs)
    signal.signal(signal.SIGINT, shutdownAndExit)
    signal.signal(signal.SIGQUIT, shutdownAndExit)
    init()
    start()


if __name__ == "__main__":
    main()
