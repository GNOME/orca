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
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the dojo tab container demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
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
    ["BRAILLE LINE:  'TabList Tab 1 Page Tab 2 Page Tab 3 Page Programmatically created tab Page Inlined Sub TabContainer Page Sub TabContainer from href Page'",
     "     VISIBLE:  'Tab 2 Page Tab 3 Page Programmat', cursor=1",
     "BRAILLE LINE:  'TabList Tab 1 Page Tab 2 Page Tab 3 Page Programmatically created tab Page Inlined Sub TabContainer Page Sub TabContainer from href Page'",
     "     VISIBLE:  'Tab 2 Page Tab 3 Page Programmat', cursor=1",
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
    ["BRAILLE LINE:  'TabList Tab 1 Page Tab 2 Page Tab 3 Page Programmatically created tab Page Inlined Sub TabContainer Page Sub TabContainer from href Page'",
     "     VISIBLE:  'Tab 2 Page Tab 3 Page Programmat', cursor=1",
     "SPEECH OUTPUT: 'tab list'",
     "SPEECH OUTPUT: 'Tab 2 page'",
     "SPEECH OUTPUT: 'item 2 of 7'",
     "SPEECH OUTPUT: ''"]))

########################################################################
# Use arrows to move between tabs: 'Tab 3'.  The following will be presented.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "arrow to tab 3", 
    ["BRAILLE LINE:  'TabList Tab 1 Page Tab 2 Page Tab 3 Page Programmatically created tab Page Inlined Sub TabContainer Page Sub TabContainer from href Page'",
     "     VISIBLE:  'Tab 3 Page Programmatically crea', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Tab 3 page'"]))
########################################################################
# Use arrows to move between tabs: 'Another Tab'.  The following will be presented.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "arrow to programmatically created tab", 
    ["BRAILLE LINE:  'TabList Tab 1 Page Tab 2 Page Tab 3 Page Programmatically created tab Page Inlined Sub TabContainer Page Sub TabContainer from href Page'",
     "     VISIBLE:  'Programmatically created tab Pag', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Programmatically created tab page'"]))

########################################################################
# Use arrows to move between tabs: 'Sub TabContainer'.  The following will be presented.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "arrow to sub tab container", 
    ["BRAILLE LINE:  'TabList Tab 1 Page Tab 2 Page Tab 3 Page Programmatically created tab Page Inlined Sub TabContainer Page Sub TabContainer from href Page'",
     "     VISIBLE:  'Inlined Sub TabContainer Page Su', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Inlined Sub TabContainer page'"]))
########################################################################
# Tab to 'SubTab2'.  The following will be presented.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "tab to tab 2 contents", 
    ["BRAILLE LINE:  'TabList SubTab 1 Page SubTab 2 Page'",
     "     VISIBLE:  'SubTab 2 Page', cursor=1",
     "BRAILLE LINE:  'TabList SubTab 1 Page SubTab 2 Page'",
     "     VISIBLE:  'SubTab 2 Page', cursor=1",
     "SPEECH OUTPUT: 'Inlined Sub TabContainer scroll pane'",
     "SPEECH OUTPUT: 'SubTab 2 page'"]))
    
########################################################################
# Tab to next tab container
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "tab to next tab container", 
    ["BRAILLE LINE:  'TabList First Page  $l Second Page Third Page  $l'",
     "     VISIBLE:  'First Page  $l Second Page Third', cursor=1",
     "BRAILLE LINE:  'TabList First Page  $l Second Page Third Page  $l'",
     "     VISIBLE:  'First Page  $l Second Page Third', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'First page'"]))

########################################################################
# Use arrows to move between tabs: 'SubTab1'.  The following will be presented
#
# BRAILLE LINE:  'SubTab 1 SubTab 2'
#      VISIBLE:  'SubTab 1 SubTab 2', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'SubTab 1 page'
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "arrow to tab 3", 
    ["BRAILLE LINE:  'First Page TabList  $l Second Page Third Page  $l'",
     "     VISIBLE:  'Third Page  $l', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Third page'"]))

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

sequence.append(utils.AssertionSummaryAction())

sequence.start()
