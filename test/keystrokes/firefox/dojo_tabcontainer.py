#!/usr/bin/python

"""Test of Dojo tab container presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "TabContainer Demo" frame.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the dojo tab container demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction(utils.DojoURLPrefix + "layout/test_TabContainer.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("TabContainer Demo", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Give the widget a moment to construct itself
#
sequence.append(PauseAction(5000))

########################################################################
# Tab to 'Tab 2'.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "tab to tab 2", 
    ["BRAILLE LINE:  'Tab 1 Page Tab 2 Page Tab 3 Page Inlined Sub TabContainer Page Sub TabContainer from href Page SplitContainer from href Page'",
     "     VISIBLE:  'Tab 2 Page Tab 3 Page Inlined Su', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Tab 2 page'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "basic whereAmI", 
    ["BRAILLE LINE:  'Tab 1 Page Tab 2 Page Tab 3 Page Inlined Sub TabContainer Page Sub TabContainer from href Page SplitContainer from href Page'",
     "     VISIBLE:  'Tab 2 Page Tab 3 Page Inlined Su', cursor=1",
     "SPEECH OUTPUT: 'tab list'",
     "SPEECH OUTPUT: 'Tab 2 page'",
     "SPEECH OUTPUT: 'item 2 of 6'",
     "SPEECH OUTPUT: ''"]))

########################################################################
# Use arrows to move between tabs: 'Tab 3'.  The following will be presented.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "arrow to tab 3", 
    ["BRAILLE LINE:  'Tab 1 Page Tab 2 Page Tab 3 Page Inlined Sub TabContainer Page Sub TabContainer from href Page SplitContainer from href Page Tab 3 Page'",
     "     VISIBLE:  'Tab 3 Page Inlined Sub TabContai', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Tab 3 page'"]))
########################################################################
# Use arrows to move between tabs: 'Another Tab'.  The following will be presented.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "arrow to programmatically created tab", 
    ["BRAILLE LINE:  'Tab 1 Page Tab 2 Page Tab 3 Page Inlined Sub TabContainer Page Sub TabContainer from href Page SplitContainer from href Page Inlined Sub TabContainer Page'",
     "     VISIBLE:  'Inlined Sub TabContainer Page Su', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Inlined Sub TabContainer page'"]))

########################################################################
# Use arrows to move between tabs: 'Sub TabContainer'.  The following will be presented.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "arrow to sub tab container", 
    ["BRAILLE LINE:  'Tab 1 Page Tab 2 Page Tab 3 Page Inlined Sub TabContainer Page Sub TabContainer from href Page SplitContainer from href Page'",
     "     VISIBLE:  'Sub TabContainer from href Page ', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Sub TabContainer from href page'",
     "SPEECH OUTPUT: 'Subtab #1  This is a nested tab container BUT loaded via an href.'"]))

########################################################################
# Tab to 'SubTab2'.  The following will be presented.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "tab to tab 2 contents", 
    ["BRAILLE LINE:  'Subtab #1 Page Subtab #2 Page'",
     "     VISIBLE:  'Subtab #1 Page Subtab #2 Page', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Subtab #1 page'"]))

########################################################################
# Close the demo
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
