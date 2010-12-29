# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of Orca's support for mouseovers.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "inline: Tab Panel Example 1" frame.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the UIUC Tab Panel demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction(utils.htmlURLPrefix + "mouseover.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file", 
    ["BRAILLE LINE:  'Mouseover which will present an traditional alert:'",
     "     VISIBLE:  'Mouseover which will present an ', cursor=1",
     "SPEECH OUTPUT: 'Mouseover which will present an traditional alert:'"]))

########################################################################
# Down Arrow to the image.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Down Arrow to Image",
    ["BRAILLE LINE:  'Orca Logo Image'",
     "     VISIBLE:  'Orca Logo Image', cursor=1",
     "SPEECH OUTPUT: 'Orca Logo image'"]))

########################################################################
# Route the mouse pointer to the image, triggering a javascript alert.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Divide"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Route the pointer to the image",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application \[JavaScript Application\] Dialog'",
     "     VISIBLE:  '[JavaScript Application] Dialog', cursor=1",
     "BRAILLE LINE:  '" + utils.firefoxAppNames + " Application \[JavaScript Application\] Dialog OK Button'",
     "     VISIBLE:  'OK Button', cursor=1",
     "SPEECH OUTPUT: 'New item has been added'",
     "SPEECH OUTPUT: '[JavaScript Application] Welcome to mouseover-enabled Orca!'",
     "SPEECH OUTPUT: 'OK button'"]))

########################################################################
# Dismiss the alert.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Escape"))
sequence.append(utils.AssertPresentationAction(
    "Escape to dismiss the dialog.",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application MouseOvers - " + utils.firefoxFrameNames + " Frame'",
     "     VISIBLE:  'MouseOvers - " + utils.firefoxFrameNames + "(| Fra| Frame)', cursor=1",
     "BRAILLE LINE:  'Orca Logo Image'",
     "     VISIBLE:  'Orca Logo Image', cursor=1",
     "SPEECH OUTPUT: 'MouseOvers - " + utils.firefoxFrameNames + " frame'",
     "SPEECH OUTPUT: 'Orca Logo image'"]))

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
