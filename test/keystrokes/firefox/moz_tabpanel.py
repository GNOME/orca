#!/usr/bin/python

"""Test of Mozilla ARIA tabpanel presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "Tabbed UI" frame.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the Mozilla ARIA slider demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://www.mozilla.org/access/dhtml/tabpanel"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Tabbed UI", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Give the widget a moment to construct itself
#
sequence.append(PauseAction(1000))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
# [[[Bug?: minor whitespace issue??]]]
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "basic whereAmI", 
    [ "BRAILLE LINE:  'Tab Zero  Page Tab One  Page Tab Two  Page Tab Three  Page Tab Four  Page'",
     "     VISIBLE:  'Tab Zero  Page Tab One  Page Tab', cursor=1",
     "SPEECH OUTPUT: 'tab list'",
     "SPEECH OUTPUT: 'Tab Zero page'",
     "SPEECH OUTPUT: 'item 1 of 5'",
     "SPEECH OUTPUT: ''"]))

########################################################################
# Move to tab 2.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "arrow to tab 2", 
    ["BRAILLE LINE:  'Tab Zero  Page Tab One  Page Tab Two  Page Tab Three  Page Tab Four  Page Tab Zero  Tab Zero ScrollPane'",
     "     VISIBLE:  'Tab One  Page Tab Two  Page Tab ', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Tab One  page'"]))
########################################################################
# Move to tab 3
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "arrow to tab 3", 
    [ "BRAILLE LINE:  'Tab Zero  Page Tab One  Page Tab Two  Page Tab Three  Page Tab Four  Page Tab One  Tab One ScrollPane'",
     "     VISIBLE:  'Tab Two  Page Tab Three  Page Ta', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Tab Two  page'"]))
########################################################################
# Move to tab 3 contents
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "tab to tab 3 contents", 
    ["BRAILLE LINE:  '&=y RadioButton Internal Portal Bookmark & y RadioButton External URL  '",
     "     VISIBLE:  '&=y RadioButton Internal Portal ', cursor=1",
     "SPEECH OUTPUT: 'Tab Two  Tab Two scroll pane'",
     "SPEECH OUTPUT: 'Internal Portal Bookmark'",
     "SPEECH OUTPUT: 'selected radio button'"]))
########################################################################
# Move back to tab 3
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(utils.AssertPresentationAction(
    "move back to tab 3", 
    ["BRAILLE LINE:  'Tab Zero  Page Tab One  Page Tab Two  Page Tab Three  Page Tab Four  Page'",
     "     VISIBLE:  'Tab Two  Page Tab Three  Page Ta', cursor=1",
     "BRAILLE LINE:  'Tab Zero  Page Tab One  Page Tab Two  Page Tab Three  Page Tab Four  Page'",
     "     VISIBLE:  'Tab Two  Page Tab Three  Page Ta', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Tab Two  page'"]))
########################################################################
# Move to tab 4
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "arrow to tab 4", 
    ["BRAILLE LINE:  'Tab Zero  Page Tab One  Page Tab Two  Page Tab Three  Page Tab Four  Page Tab Two  Tab Two ScrollPane'",
     "     VISIBLE:  'Tab Three  Page Tab Four  Page T', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Tab Three  page'"]))
########################################################################
# Move to tab 5
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "arrow to tab 5", 
    ["BRAILLE LINE:  'Tab Zero  Page Tab One  Page Tab Two  Page Tab Three  Page Tab Four  Page'",
     "     VISIBLE:  'Tab Four  Page', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Tab Four  page'"]))
########################################################################
# Close the demo
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_name="Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
