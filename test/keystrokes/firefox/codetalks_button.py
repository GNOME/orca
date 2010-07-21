#!/usr/bin/python

"""Test of Codetalks button test presentation using Firefox.
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
# Load the Codetalks button demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://codetalks.org/source/widgets/button/button.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("ARIA Button", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Tab to the "ARIA documentation" link
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("ARIA documentation", acc_role=pyatspi.ROLE_LINK))

########################################################################
# Tab to the "Tracking number" entry
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Tracking number", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(utils.AssertPresentationAction(
    "Tab to Tracking number text entry", 
    ["BRAILLE LINE:  'Tracking number Tracking number  $l'",
     "     VISIBLE:  'Tracking number  $l', cursor=17",
     "SPEECH OUTPUT: 'Order tracking panel Tracking number text '"]))

########################################################################
# Tab to the "Check Now" push button
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Check Now", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Tab to Check Now push button",
    ["BRAILLE LINE:  'Check Now Button $l'",
     "     VISIBLE:  'Check Now Button $l', cursor=1",
     "SPEECH OUTPUT: 'Check Now button'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "basic whereamI", 
    ["BRAILLE LINE:  'Check Now Button $l'",
     "     VISIBLE:  'Check Now Button $l', cursor=1",
     "SPEECH OUTPUT: 'Check Now button Check to see if your order has been shipped.'"]))

########################################################################
# Now push the button.  The following will be presented.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("OK", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Popup dialog", 
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application The page at http://codetalks.org says: Dialog'",
     "     VISIBLE:  'The page at http://codetalks.org', cursor=1",
     "BRAILLE LINE:  '" + utils.firefoxAppNames + " Application The page at http://codetalks.org says: Dialog OK Button'",
     "     VISIBLE:  'OK Button', cursor=1",
     "SPEECH OUTPUT: 'The page at http://codetalks.org says: Button pressed'",
     "SPEECH OUTPUT: 'OK button'"]))

########################################################################
# Dismiss the dialog.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("Check Now", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Dismiss dialog", 
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application ARIA Button - " + utils.firefoxFrameNames + " Frame'",
     "     VISIBLE:  'ARIA Button - " + utils.firefoxFrameNames + " Frame', cursor=1",
     "BRAILLE LINE:  'Check Now Button $l'",
     "     VISIBLE:  'Check Now Button $l', cursor=1",
     "SPEECH OUTPUT: 'ARIA Button - " + utils.firefoxFrameNames + " frame'",
     "SPEECH OUTPUT: 'Order tracking panel Check Now button'"]))

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
