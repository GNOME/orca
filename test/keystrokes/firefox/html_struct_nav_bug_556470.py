# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of table structural navigation with empty tables.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the local blockquote test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "bug-556470.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

sequence.append(PauseAction(3000))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file", 
    ["BRAILLE LINE:  'hi, this is a paragraph'",
     "     VISIBLE:  'hi, this is a paragraph', cursor=1",
     "SPEECH OUTPUT: 'hi, this is a paragraph'"]))

########################################################################
# Press t to move amongst the tables
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("t"))
sequence.append(utils.AssertPresentationAction(
    "1. t", 
    ["BRAILLE LINE:  'col 1 col 2 col 3'",
     "     VISIBLE:  'col 1 col 2 col 3', cursor=1",
     "SPEECH OUTPUT: 'Table with 2 rows 3 columns'",
     "SPEECH OUTPUT: 'col 1 column header'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("t"))
sequence.append(utils.AssertPresentationAction(
    "2. t", 
    ["BRAILLE LINE:  '1 2 4'",
     "     VISIBLE:  '1 2 4', cursor=1",
     "SPEECH OUTPUT: 'Table with 2 rows 3 columns'",
     "SPEECH OUTPUT: '1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("t"))
sequence.append(utils.AssertPresentationAction(
    "3. t",
    ["BRAILLE LINE:  'Wrapping to top.'",
     "     VISIBLE:  'Wrapping to top.', cursor=0",
     "BRAILLE LINE:  'col 1 col 2 col 3'",
     "     VISIBLE:  'col 1 col 2 col 3', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to top.'",
     "SPEECH OUTPUT: 'Table with 2 rows 3 columns'",
     "SPEECH OUTPUT: 'col 1 column header'"]))

########################################################################
# Press Shift+t to move amongst the tables
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>t"))
sequence.append(utils.AssertPresentationAction(
    "1. shift+t", 
    ["BRAILLE LINE:  'Wrapping to bottom.'",
     "     VISIBLE:  'Wrapping to bottom.', cursor=0",
     "BRAILLE LINE:  '1 2 4'",
     "     VISIBLE:  '1 2 4', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to bottom.'",
     "SPEECH OUTPUT: 'Table with 2 rows 3 columns'",
     "SPEECH OUTPUT: '1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>t"))
sequence.append(utils.AssertPresentationAction(
    "2. shift+t", 
    ["BRAILLE LINE:  'col 1 col 2 col 3'",
     "     VISIBLE:  'col 1 col 2 col 3', cursor=1",
     "SPEECH OUTPUT: 'Table with 2 rows 3 columns'",
     "SPEECH OUTPUT: 'col 1 column header'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>t"))
sequence.append(utils.AssertPresentationAction(
    "3. shift+t",
    ["BRAILLE LINE:  'Wrapping to bottom.'",
     "     VISIBLE:  'Wrapping to bottom.', cursor=0", 
     "BRAILLE LINE:  '1 2 4'",
     "     VISIBLE:  '1 2 4', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to bottom.'",
     "SPEECH OUTPUT: 'Table with 2 rows 3 columns'",
     "SPEECH OUTPUT: '1'"]))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
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
