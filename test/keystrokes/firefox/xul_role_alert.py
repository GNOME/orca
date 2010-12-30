#!/usr/bin/python

"""Test of alert output of Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "javascript:alert('I am an alert') and press Return.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction("javascript:alert('I am an alert')"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(2000))
sequence.append(utils.AssertPresentationAction(
    "Press Return to make the alert appear",
    ["BRAILLE LINE:  'about:blank HtmlPane'",
     "     VISIBLE:  'about:blank HtmlPane', cursor=1",
     "BRAILLE LINE:  'about:blank'",
     "     VISIBLE:  'about:blank', cursor=0",
     "BRAILLE LINE:  'about:blank HtmlPane'",
     "     VISIBLE:  'about:blank HtmlPane', cursor=1",
     "BRAILLE LINE:  '" + utils.firefoxAppNames + " Application \[JavaScript Application\] Dialog'",
     "     VISIBLE:  '[JavaScript Application] Dialog', cursor=1",
     "BRAILLE LINE:  '" + utils.firefoxAppNames + " Application \[JavaScript Application\] Dialog OK Button'",
     "     VISIBLE:  'OK Button', cursor=1",
     "SPEECH OUTPUT: 'about:blank html content'",
     "SPEECH OUTPUT: 'about:blank page'",
     "SPEECH OUTPUT: 'about:blank html content'",
     "SPEECH OUTPUT: '[JavaScript Application] I am an alert'",
     "SPEECH OUTPUT: 'OK button'"]))

########################################################################
# Dismiss the alert by pressing Return
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "Press Return to dismiss the alert",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame'",
     "     VISIBLE:  '" + utils.firefoxFrameNames + " Frame', cursor=1",
     "BRAILLE LINE:  'about:blank HtmlPane'",
     "     VISIBLE:  'about:blank HtmlPane', cursor=1",
     "SPEECH OUTPUT: '" + utils.firefoxFrameNames + " frame'",
     "SPEECH OUTPUT: 'about:blank html content'"]))

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
