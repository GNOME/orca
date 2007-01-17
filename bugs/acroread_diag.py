"""AT-SPI diagnostic script.  This standalone module talks
directly with the AT-SPI Registry via its IDL interfaces.
No Orca logic or code is stuck in the middle.

Steps to Reproduce:
1. Run this script by typing 'python diagnostics.py'
   in an xterm.
2. Launch the application you wish to test and create or
   open a document.
3. Move focus to (or select) an area of text you're interested in.
   NOTE: For Adobe Acrobat, the selection cursor must be active and
   in the document.
4. Press F11 to run the diagnostics.
5. Press F12 to terminate the script from within the application;
   or press Control C to do so from within the xterm.

Results:  
In the xterm window, you will see a lot of information about the 
text in the application window which has focus.focu
"""

import time

import bonobo
import ORBit

ORBit.load_typelib("Accessibility")
ORBit.CORBA.ORB_init()

import Accessibility
import Accessibility__POA

listeners = []
keystrokeListeners = []

registry = bonobo.get_object("OAFIID:Accessibility_Registry:1.0",
                             "Accessibility/Registry")

# Types of diagnostics to run:
diagRunTextDiagnostics = True

# Text diagnostic options:
diagIncludeBasicInfo = True
diagMaxCharsToDisplay = 200           # None means show all
diagSelectedText = True
diagSetCaretOffset = True
diagAttributes = True
diagIncludeDefAttribSet = False       # Tends to crash apps
diagSizeAndPosition = True
diagBoundaryTypes = True
diagPrintBoundaryDetails = False      # word, line, sentence, etc.

# Other options:
diagPrintTopObject = False

########################################################################
#                                                                      #
# Event listener classes for global and keystroke events               #
#                                                                      #
########################################################################

class EventListener(Accessibility__POA.EventListener):
    """Registers a callback directly with the AT-SPI Registry for the
    given event type.  Most users of this module will not use this
    class directly, but will instead use the addEventListener method.
    """

    def __init__(self, registry, callback, eventType):
        self.registry  = registry
        self.callback  = callback
        self.eventType = eventType
        self.register()

    def ref(self): pass

    def unref(self): pass

    def queryInterface(self, repo_id):
	thiz = None
        if repo_id == "IDL:Accessibility/EventListener:1.0":
            thiz = self._this()
	return thiz

    def register(self):
        self._default_POA().the_POAManager.activate()
        self.registry.registerGlobalEventListener(self._this(),
                                                  self.eventType)
        self.__registered = True
        return self.__registered

    def deregister(self):
        if not self.__registered:
            return
        self.registry.deregisterGlobalEventListener(self._this(),
                                                    self.eventType)
        self.__registered = False

    def notifyEvent(self, event):
        self.callback(event)

    def __del__(self):
        self.deregister()

class KeystrokeListener(Accessibility__POA.DeviceEventListener):
    """Registers a callback directly with the AT-SPI Registry for the
    given keystroke.  Most users of this module will not use this
    class directly, but will instead use the registerKeystrokeListeners
    method."""

    def keyEventToString(event):
        return ("KEYEVENT: type=%d\n" % event.type) \
               + ("          hw_code=%d\n" % event.hw_code) \
               + ("          modifiers=%d\n" % event.modifiers) \
               + ("          event_string=(%s)\n" % event.event_string) \
               + ("          is_text=%s\n" % event.is_text) \
               + ("          time=%f" % time.time())

    keyEventToString = staticmethod(keyEventToString)

    def __init__(self, registry, callback,
                 keyset, mask, type, synchronous, preemptive, isGlobal):
        self._default_POA().the_POAManager.activate()

        self.registry         = registry
        self.callback         = callback
        self.keyset           = keyset
        self.mask             = mask
        self.type             = type
        self.mode             = Accessibility.EventListenerMode()
        self.mode.synchronous = synchronous
        self.mode.preemptive  = preemptive
        self.mode._global     = isGlobal
        self.register()

    def ref(self): pass

    def unref(self): pass

    def queryInterface(self, repo_id):
	thiz = None
        if repo_id == "IDL:Accessibility/EventListener:1.0":
            thiz = self._this()
	return thiz

    def register(self):
        d = self.registry.getDeviceEventController()
        if d.registerKeystrokeListener(self._this(),
                                       self.keyset,
                                       self.mask,
                                       self.type,
                                       self.mode):
            self.__registered = True
        else:
            self.__registered = False
        return self.__registered

    def deregister(self):
        if not self.__registered:
            return
        d = self.registry.getDeviceEventController()
        d.deregisterKeystrokeListener(self._this(),
                                      self.keyset,
                                      self.mask,
                                      self.type)
        self.__registered = False

    def notifyEvent(self, event):
        """Called by the at-spi registry when a key is pressed or released.

        Arguments:
        - event: an at-spi DeviceEvent

        Returns True if the event has been consumed.
        """
        return self.callback(event)

    def __del__(self):
        self.deregister()

########################################################################
#                                                                      #
# Testing functions.                                                   #
#                                                                      #
########################################################################

def getStateString(accessible):
    s = accessible.getState()
    stateSet = s._narrow(Accessibility.StateSet).getStates()
    stateString = "("
    if stateSet.count(Accessibility.STATE_INVALID):
        stateString += "INVALID "
    if stateSet.count(Accessibility.STATE_ACTIVE):
        stateString += "ACTIVE "
    if stateSet.count(Accessibility.STATE_ARMED):
        stateString += "ARMED "
    if stateSet.count(Accessibility.STATE_BUSY):
        stateString += "BUSY "
    if stateSet.count(Accessibility.STATE_CHECKED):
        stateString += "CHECKED "
    if stateSet.count(Accessibility.STATE_COLLAPSED):
        stateString += "COLLAPSED "
    if stateSet.count(Accessibility.STATE_DEFUNCT):
        stateString += "DEFUNCT "
    if stateSet.count(Accessibility.STATE_EDITABLE):
        stateString += "EDITABLE "
    if stateSet.count(Accessibility.STATE_ENABLED):
        stateString += "ENABLED "
    if stateSet.count(Accessibility.STATE_EXPANDABLE):
        stateString += "EXPANDABLE "
    if stateSet.count(Accessibility.STATE_EXPANDED):
        stateString += "EXPANDED "
    if stateSet.count(Accessibility.STATE_FOCUSABLE):
        stateString += "FOCUSABLE "
    if stateSet.count(Accessibility.STATE_FOCUSED):
        stateString += "FOCUSED "
    if stateSet.count(Accessibility.STATE_HAS_TOOLTIP):
        stateString += "HAS_TOOLTIP "
    if stateSet.count(Accessibility.STATE_HORIZONTAL):
        stateString += "HORIZONTAL "
    if stateSet.count(Accessibility.STATE_ICONIFIED):
        stateString += "ICONIFIED "
    if stateSet.count(Accessibility.STATE_MODAL):
        stateString += "MODAL "
    if stateSet.count(Accessibility.STATE_MULTI_LINE):
        stateString += "MULTI_LINE "
    if stateSet.count(Accessibility.STATE_MULTISELECTABLE):
        stateString += "MULTISELECTABLE "
    if stateSet.count(Accessibility.STATE_OPAQUE):
        stateString += "OPAQUE "
    if stateSet.count(Accessibility.STATE_PRESSED):
        stateString += "PRESSED "
    if stateSet.count(Accessibility.STATE_RESIZABLE):
        stateString += "RESIZABLE "
    if stateSet.count(Accessibility.STATE_SELECTABLE):
        stateString += "SELECTABLE "
    if stateSet.count(Accessibility.STATE_SELECTED):
        stateString += "SELECTED "
    if stateSet.count(Accessibility.STATE_SENSITIVE):
        stateString += "SENSITIVE "
    if stateSet.count(Accessibility.STATE_SHOWING):
        stateString += "SHOWING "
    if stateSet.count(Accessibility.STATE_SINGLE_LINE):
        stateString += "SINGLE_LINE "
    if stateSet.count(Accessibility.STATE_STALE):
        stateString += "STALE "
    if stateSet.count(Accessibility.STATE_TRANSIENT):
        stateString += "TRANSIENT "
    if stateSet.count(Accessibility.STATE_VERTICAL):
        stateString += "VERTICAL "
    if stateSet.count(Accessibility.STATE_VISIBLE):
        stateString += "VISIBLE "
    if stateSet.count(Accessibility.STATE_MANAGES_DESCENDANTS):
        stateString += "MANAGES_DESCENDANTS "
    if stateSet.count(Accessibility.STATE_INDETERMINATE):
        stateString += "INDETERMINATE "
    return stateString.strip() + ")"

def start():
    """Starts event notification with the AT-SPI Registry.  This method
    only returns after 'stop' has been called.
    """
    bonobo.main()

def stop():
    """Unregisters any event or keystroke listeners registered with
    the AT-SPI Registry and then stops event notification with the
    AT-SPI Registry.
    """
    for listener in (listeners + keystrokeListeners):
        listener.deregister()
    bonobo.main_quit()

def registerEventListener(callback, eventType):
    global listeners
    listener = EventListener(registry, callback, eventType)
    listeners.append(listener)

def registerKeystrokeListeners(callback):
    """Registers a single callback for all possible keystrokes.
    """
    global keystrokeListeners
    for i in range(0, (1 << (Accessibility.MODIFIER_NUMLOCK + 1))):
        keystrokeListeners.append(
            KeystrokeListener(registry,
                              callback, # callback
                              [],       # keyset
                              i,        # modifier mask
                              [Accessibility.KEY_PRESSED_EVENT,
                               Accessibility.KEY_RELEASED_EVENT],
                              True,     # synchronous
                              True,     # preemptive
                              False))   # global

eventTypes = [
##     "focus:",
##     "mouse:rel",
##     "mouse:button",
##     "mouse:abs",
##     "keyboard:modifiers",
##     "object:property-change",
##     "object:property-change:accessible-name",
##     "object:property-change:accessible-description",
##     "object:property-change:accessible-parent",
##     "object:state-changed",
##     "object:state-changed:focused",
##     "object:selection-changed",
##     "object:children-changed"
##     "object:active-descendant-changed"
##     "object:visible-data-changed"
##     "object:text-selection-changed",
##     "object:text-caret-moved",
##     "object:text-changed",
##     "object:column-inserted",
##     "object:row-inserted",
##     "object:column-reordered",
##     "object:row-reordered",
##     "object:column-deleted",
##     "object:row-deleted",
##     "object:model-changed",
##     "object:link-selected",
##     "object:bounds-changed",
##     "window:minimize",
##     "window:maximize",
##     "window:restore",
##     "window:activate",
##     "window:create",
##     "window:deactivate",
##     "window:close",
##     "window:lower",
##     "window:raise",
##     "window:resize",
##     "window:shade",
##     "window:unshade",
##     "object:property-change:accessible-table-summary",
##     "object:property-change:accessible-table-row-header",
##     "object:property-change:accessible-table-column-header",
##     "object:property-change:accessible-table-summary",
##     "object:property-change:accessible-table-row-description",
##     "object:property-change:accessible-table-column-description",
##     "object:test",
##     "window:restyle",
##     "window:desktop-create",
##     "window:desktop-destroy"
]

def printTopObject(child):
    parent = child
    while parent:
	if not parent.parent:
            print "TOP OBJECT:", parent.name, parent.getRoleName()
        parent = parent.parent
	
def findActiveWindow():
    desktop = registry.getDesktop(0)
    window = None
    for j in range(0, desktop.childCount):
        app = desktop.getChildAtIndex(j)
        if app:
            for k in range(0, app.childCount):
                child = app.getChildAtIndex(k)
                s = child.getState()
                s = s._narrow(Accessibility.StateSet)
                state = s.getStates()
                if (state.count(Accessibility.STATE_ACTIVE) > 0) \
                   or (state.count(Accessibility.STATE_FOCUSED) > 0):
                    window = child
                    break
        if window:
           break
    if window:
        print "Active window name=%s role=%s state=%s" \
              % (window.name, window.getRoleName(), getStateString(window))
    else:
        print "NO ACTIVE WINDOW."

    return window

def runDiagnostics(root):

    if not root:
        print "not root"
        return

    if diagRunTextDiagnostics:
        runTextDiagnostics(root)

def runTextDiagnostics(root):

    if not root:
        return

    if root.getRole() != Accessibility.ROLE_TEXT:
        for i in range(0, root.childCount):
            runTextDiagnostics(root.getChildAtIndex(i))
    
    s = root.getState()
    s = s._narrow(Accessibility.StateSet)
    state = s.getStates()
    if state.count(Accessibility.STATE_FOCUSED):
        text = root.queryInterface("IDL:Accessibility/Text:1.0")
        if text:
            print "text found"
            text = text._narrow(Accessibility.Text)
            if diagIncludeBasicInfo:
                showBasicInfo(text)
            if diagSelectedText:
                testSelection(text)
            if diagSetCaretOffset:
                desiredOffset = max(0, text.caretOffset - 10)
                testSetCaretOffset(text, desiredOffset)
            if diagAttributes:
                testAttributes(text, diagIncludeDefAttribSet)
            if diagSizeAndPosition:
                testSizeAndPosition(text)
            if diagBoundaryTypes:
                testBoundaryTypes(text)

def showBasicInfo(text):

    if not text:
        return

    length = text.characterCount
    caretOffset = text.caretOffset
    print "\nTEXT WITH FOCUS:"
    print "Number of characters: %d" % length
    print "Caret offset: %d" % caretOffset

    if diagMaxCharsToDisplay and diagMaxCharsToDisplay < length:
        half = diagMaxCharsToDisplay/2
        string = "%s ... %s" % \
           (text.getText(0, half), text.getText(length - half, length))
    else:
        string = text.getText(0, -1)
    print "Text: \n%s" % string

def testSelection(text):

    if not text:
        return

    nSelections = text.getNSelections()
    print "\nTEXT SELECTION INFORMATION:"
    print "Number of selected areas reported: %d" % nSelections
    if nSelections:
        print "Selected text is:"
        for i in range(0, nSelections):
            [startOffset, endOffset] = text.getSelection(i)
            print "    %s" % text.getText(startOffset,endOffset)
    else:
        print "\n******************************************************"
        print "*   ALERT: If text was selected when you ran the     *"
        print "*          diagnostics, this information is not      *"
        print "*          being exposed by at-spi.                  *"
        print "******************************************************"

def testSetCaretOffset(text, desiredOffset):

    if not text:
        return

    print "\nATTEMPTING TO SET THE CARET OFFSET...."
    success = text.setCaretOffset(desiredOffset)
    if not success:
        print "\n******************************************************"
        print "*   WARNING:  Was not able to set the caret offset   *"
        print "******************************************************"
    else:
        print "Done."

def testAttributes(text, includeDefAttribSet=False):

    if not text:
        return

    caretOffset = text.caretOffset
    [charAttributes, start, end] = text.getAttributes(caretOffset)
    attributeRun = text.getAttributeRun(0,True)
    defaultAttributes = text.getDefaultAttributes()
    print "\nATTRIBUTE INFORMATION:"
    print "\nattributes at the caret: %s" % charAttributes
    if not len(charAttributes):
        print "\n******************************************************"
        print "*     ALERT:  No information was received from       *"
        print "*             getAttributes. This can occur when     *"
        print "*             the text at the caret has the default  *"
        print "*             formatting.  If the text at the caret  *"
        print "*             has non-default formatting, it is not  *"
        print "*             being exposed by at-spi.               *"
        print "******************************************************"

    print "\nattribute run: %s" % str(attributeRun)
    if not len(attributeRun[0]):
        print "\n******************************************************"
        print "*     WARNING:  No information is being provided.    *"
        print "*               by getAttributeRun                   *"
        print "******************************************************"

    print "\ndefault attributes: %s " % str(defaultAttributes)
    if not len(defaultAttributes):
        print "\n******************************************************"
        print "*     WARNING:  No information is being provided.    *"
        print "*               by getDefaultAttributes              *"
        print "******************************************************"

    if includeDefAttribSet:
        print "\nattempting to use getDefaultAttributeSet....", \
              "Note that this might crash the application."
        defaultAttributeSet = text.getDefaultAttributeSet()
        print "\ndefault attribute set: %s" % str(defaultAttributeSet)
        if not len(defaultAttributeSet):
            print "\n******************************************************"
            print "*     WARNING:  No information is being provided.    *"
            print "*               by getDefaultAttributeSet            *"
            print "******************************************************"

def testSizeAndPosition(text):

    if not text:
        return

    charExtentsFailed = False
    rangeExtentsFailed = False

    caretOffset = text.caretOffset
    [xScreen, yScreen, widthScreen, heightScreen] = \
              text.getCharacterExtents(caretOffset, 0)
    [xWindow, yWindow, widthWindow, heightWindow] = \
              text.getCharacterExtents(caretOffset, 1)

    [word, startOffset, endOffset] = \
       text.getTextAtOffset(caretOffset,Accessibility.TEXT_BOUNDARY_WORD_START)
    [boxXScreen, boxYScreen, boxWidthScreen, boxHeightScreen] = \
              text.getRangeExtents(startOffset, endOffset, 0)
    [boxXWindow, boxYWindow, boxWidthWindow, boxHeightWindow] = \
              text.getRangeExtents(startOffset, endOffset, 1)

    print "\nSIZE AND POSITION INFORMATION:"
    print "\ncharacter extents with respect to the screen:"
    print "   x: %d, y: %d, width: %d, height: %d" % \
       (xScreen, yScreen, widthScreen, heightScreen)
    if (xScreen == yScreen == widthScreen == heightScreen):
        print "\n******************************************************"
        print "*     WARNING:  No information is being provided.    *"
        print "*               by getCharacterExtents               *"
        print "******************************************************"
        charExtentsFailed = True

    print "\ncharacter extents with respect to the window:"
    print "   x: %d, y: %d, width: %d, height: %d" % \
       (xWindow, yWindow, widthWindow, heightWindow)
    if (xWindow == yWindow == widthWindow == heightWindow):
        print "\n******************************************************"
        print "*     WARNING:  No information is being provided.    *"
        print "*               by getCharacterExtents               *"
        print "******************************************************"

    print "\ntrying getOffsetAtPoint with respect to the screen:"
    if not charExtentsFailed:
        print "(the resulting value should match the caret offset)"
        offset = text.getOffsetAtPoint(xScreen, yScreen, 0)
        print "   offset is: %d and caretOffset is: %d" % \
                    (offset, caretOffset)
        if offset != caretOffset:
            print "\n******************************************************"
            print "*     WARNING:  A potentially invalid value is being *"
            print "*               returned by getOffsetAtPoint         *"
            print "******************************************************"
    else:
        zeroCount = 0
        loopCount = 0
        print "(using arbitrary values for x, y as getCharacterExtents failed)"
        for i in range(200, 800, 100):
            offset = text.getOffsetAtPoint(i, i, 0)
            loopCount += 1
            if offset == 0:
                zeroCount += 1
            print "   Character offset at point(%d, %d) is: %d" % \
                  (i, i, offset)
        if zeroCount and zeroCount == loopCount:
            print "\n******************************************************"
            print "*     ALERT:  It is likely that no information is    *"
            print "*             being received from getOffsetAtPoint.  *"
            print "*             When the point falls outside of the    *"
            print "*             specified bounds, the expected value   *"
            print "*             is -1 and not 0.                       *"
            print "******************************************************"

    print "\nrange extents of the current word with respect to the screen:"
    print "   x: %d, y: %d, width: %d, height: %d" % \
       (boxXScreen, boxYScreen, boxWidthScreen, boxHeightScreen)
    if (boxXScreen == boxYScreen == boxWidthScreen == boxHeightScreen):
        print "\n******************************************************"
        print "*     WARNING:  No information is being provided.    *"
        print "*               by getRangeExtents                   *"
        print "******************************************************"
        rangeExtentsFailed = True

    print "\nrange extents of the current word with respect to the window:"
    print "   x: %d, y: %d, width: %d, height: %d" % \
       (boxXWindow, boxYWindow, boxWidthWindow, boxHeightWindow)
    if (boxXWindow == boxYWindow == boxWidthWindow == boxHeightWindow):
        print "\n******************************************************"
        print "*     WARNING:  No information is being provided.    *"
        print "*               by getRangeExtents                   *"
        print "******************************************************"

def testBoundaryTypes(text):

    if not text:
        return

    print "\nCHECKING SUPPORT FOR TEXT BOUNDARY TYPES...."
    caretOffset = text.caretOffset
    ch = ["Character", Accessibility.TEXT_BOUNDARY_CHAR]
    ws = ["Word start", Accessibility.TEXT_BOUNDARY_WORD_START]
    ss = ["Sentence start", Accessibility.TEXT_BOUNDARY_SENTENCE_START]
    ls = ["Line start", Accessibility.TEXT_BOUNDARY_LINE_START]
    boundaryType = [ch, ws, ss, ls]

    if diagPrintBoundaryDetails:
        print "Using getTextAtOffset"
    for boundary in boundaryType:
        [string, startOffset, endOffset] = \
              text.getTextAtOffset(caretOffset, boundary[1])
        boundary.append(string)
        if diagPrintBoundaryDetails:
            print "%s: <%s>" % (boundary[0], string)

    if diagPrintBoundaryDetails:
        print "\nUsing getTextBeforeOffset"
    for boundary in boundaryType:
        [string, startOffset, endOffset] = \
              text.getTextBeforeOffset(caretOffset, boundary[1])
        boundary.append(string)
        if diagPrintBoundaryDetails:
            print "%s: <%s>" % (boundary[0], string)

    if diagPrintBoundaryDetails:
        print "\nUsing getTextAfterOffset"
    for boundary in boundaryType:
        [string, startOffset, endOffset] = \
              text.getTextAfterOffset(caretOffset, boundary[1])
        boundary.append(string)
        if diagPrintBoundaryDetails:
            print "%s: <%s>" % (boundary[0], string)

    lineIndex = boundaryType.index(ls)
    line = boundaryType[lineIndex][2]
    sentenceIndex = boundaryType.index(ss)
    sentence = boundaryType[sentenceIndex][2]
    if sentence == line and sentence.endswith("\n"):
        print "\n******************************************************"
        print "*  WARNING:  TEXT_BOUNDARY_SENTENCE_START might not  *"
        print "*            be in use.                              *"
        print "******************************************************"
    else:
        print "\n    NOTE: TEXT_BOUNDARY_SENTENCE_START is supported."

    typeSupportCount = 0
    for boundary in boundaryType:
        if boundary[3] == boundary[4]:
            typeSupportCount +=1
    if typeSupportCount == len(boundaryType):
        print "\n******************************************************"
        print "*  WARNING: getTextBeforeOffset & getTextAfterOffset *"
        print "*           might not be in use: They were identical *"
        print "*           %d/%d times.                               *" % \
              (typeSupportCount, len(boundaryType))
        print "******************************************************"
    else:
        print "\n    NOTE: getTextBeforeOffset and", \
              "getTextAfterOffset seem to be supported."

def notifyEvent(event):
        print event.type, event.source.name, event.source.getRoleName(), \
              event.detail1, event.detail2,  \
              event.any_data
        if diagPrintTopObject:
            printTopObject(event.source)

def notifyKeystroke(event):
#    print "keystroke type=%d hw_code=%d modifiers=%d event_string=(%s) " \
#          "is_text=%s" \
#          % (event.type, event.hw_code, event.modifiers, event.event_string,
#             event.is_text)
    if event.event_string == "F12" or event.event_string == "SunF37":
        shutdownAndExit()
    elif event.event_string == "F11" or event.event_string == "SunF36":
        if event.type == Accessibility.KEY_PRESSED_EVENT:
            print "F11 pressed."
            runDiagnostics(findActiveWindow())
        return True
    return False

def shutdownAndExit(signum=None, frame=None):
    stop()
    print "\nGoodbye."

def test():
    print "\nMove focus to text within the application you are testing."
    print "If you are testing text selection, be sure to select the"
    print "text prior to running the diagnostics." 
    print "\nPress F11 to run the diagnostics."
    print "\nPress F12 to terminate the script from within the"
    print "application, or CTRL C to do so from within the xterm."
    for eventType in eventTypes:
        registerEventListener(notifyEvent, eventType)
    registerKeystrokeListeners(notifyKeystroke)
    start()

if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGINT, shutdownAndExit)
    signal.signal(signal.SIGQUIT, shutdownAndExit)
    test()
