#!/usr/bin/python

"""Test of learn mode.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))

########################################################################
# Once gtk-demo is running, enter learn mode and press some keys.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("h"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Enter learn mode",
    ["BRAILLE LINE:  'Learn mode.  Press escape to exit.'",
     "     VISIBLE:  'Learn mode.  Press escape to exi', cursor=0",
     "SPEECH OUTPUT: 'Entering learn mode.  Press any key to hear its function.  To exit learn mode, press the escape key.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(TypeAction("f"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Orca command: check text attributes",
    ["BRAILLE LINE:  'KP_Insert'",
     "     VISIBLE:  'KP_Insert', cursor=0",
     "BRAILLE LINE:  'Reads the attributes associated with the current text character.'",
     "     VISIBLE:  'Reads the attributes associated ', cursor=0",
     "SPEECH OUTPUT: 'insert'",
     "SPEECH OUTPUT: 'Reads the attributes associated with the current text character.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(TypeAction(" "))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Orca command: bring up preferences",
    ["BRAILLE LINE:  'KP_Insert'",
     "     VISIBLE:  'KP_Insert', cursor=0",
     "BRAILLE LINE:  'KP_Insert'",
     "     VISIBLE:  'KP_Insert', cursor=0",
     "BRAILLE LINE:  'Displays the preferences configuration dialog.'",
     "     VISIBLE:  'Displays the preferences configu', cursor=0",
     "SPEECH OUTPUT: 'insert'",
     "SPEECH OUTPUT: 'Displays the preferences configuration dialog.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "Orca command: flat review current word",
    ["BRAILLE LINE:  'KP_Insert'",
     "     VISIBLE:  'KP_Insert', cursor=0",
     "BRAILLE LINE:  'Speaks the current flat review item or word.'",
     "     VISIBLE:  'Speaks the current flat review i', cursor=0",
     "SPEECH OUTPUT: 'Speaks the current flat review item or word.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("5"))
sequence.append(utils.AssertPresentationAction(
    "Regular typing command",
    ["BRAILLE LINE:  'KP_Insert'",
     "     VISIBLE:  'KP_Insert', cursor=0",
     "BRAILLE LINE:  '5'",
     "     VISIBLE:  '5', cursor=0",
     "SPEECH OUTPUT: '5'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Escape"))
sequence.append(utils.AssertPresentationAction(
    "Exit learn mode",
    ["BRAILLE LINE:  'Escape'",
     "     VISIBLE:  'Escape', cursor=0",
     "BRAILLE LINE:  'Exiting learn mode.'",
     "     VISIBLE:  'Exiting learn mode.', cursor=0",
     "SPEECH OUTPUT: 'escape'",
     "SPEECH OUTPUT: 'Exiting learn mode.'"]))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
