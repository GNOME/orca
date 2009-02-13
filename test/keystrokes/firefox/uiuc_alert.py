#!/usr/bin/python

"""Test of UIUC button presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "text/html: Button Example 1" frame.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the UIUC button demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://test.cita.uiuc.edu/aria/alertdialog/view_class.php?title=Alert%20Dialog%20Example%201:%20Number%20Guessing%20Game&ginc=includes/alertdialog1_class.inc&gcss=css/alertdialog1_class.css&gjs=../js/globals.js,../js/widgets_class.js,js/alertdialog1_class.js"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("class: Alert Dialog Example 1: Number Guessing Game", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

sequence.append(PauseAction(6000))

########################################################################
# Tab to the text area, enter some text and press return.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Guess a number between 1 and 10", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("12"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("Alert Box", acc_role=pyatspi.ROLE_ALERT))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Open Alert Box", 
    ["BRAILLE LINE:  'Alert Box'",
     "     VISIBLE:  'Alert Box', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Alert Box12 is not between 1 and 10 '"]))

########################################################################
# Down arrow through the message and close button.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Down to message", 
    ["BRAILLE LINE:  '12 is not between 1 and 10'",
     "     VISIBLE:  '12 is not between 1 and 10', cursor=1",
     "SPEECH OUTPUT: '12 is not between 1 and 10'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Down to close button", 
    ["BRAILLE LINE:  'Close Button'",
     "     VISIBLE:  'Close Button', cursor=1",
     "SPEECH OUTPUT: 'Close button'"]))

########################################################################
# Close the alert.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Close Alert", 
    ["BRAILLE LINE:  'Guess a number between 1 and 10 12 $l'",
     "     VISIBLE:  'Guess a number between 1 and 10 ', cursor=0",
     "BRAILLE LINE:  'Guess a number between 1 and 10 12 $l'",
     "     VISIBLE:  'Guess a number between 1 and 10 ', cursor=0",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Guess a number between 1 and 10 text 12'"]))

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
