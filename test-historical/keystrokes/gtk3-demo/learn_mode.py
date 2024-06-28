#!/usr/bin/python

"""Test of learn mode."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Printing"))
sequence.append(KeyComboAction("Return"))

sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("h"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(TypeAction("f"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "1. Orca command: check text attributes",
    ["BRAILLE LINE:  'Reads the attributes associated with the current text character.'",
     "     VISIBLE:  'Reads the attributes associated ', cursor=0",
     "SPEECH OUTPUT: 'insert '",
     "SPEECH OUTPUT: 'f '",
     "SPEECH OUTPUT: 'Reads the attributes associated with the current text character.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(TypeAction(" "))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "2. Orca command: bring up preferences",
    ["BRAILLE LINE:  'Learn mode.  Press escape to exit.'",
     "     VISIBLE:  'Learn mode.  Press escape to exi', cursor=0",
     "BRAILLE LINE:  'Displays the preferences configuration dialog.'",
     "     VISIBLE:  'Displays the preferences configu', cursor=0",
     "SPEECH OUTPUT: 'insert '",
     "SPEECH OUTPUT: 'space '",
     "SPEECH OUTPUT: 'Displays the preferences configuration dialog.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "3. Orca command: flat review current word",
    ["BRAILLE LINE:  'Learn mode.  Press escape to exit.'",
     "     VISIBLE:  'Learn mode.  Press escape to exi', cursor=0",
     "BRAILLE LINE:  'Speaks the current flat review item or word.'",
     "     VISIBLE:  'Speaks the current flat review i', cursor=0",
     "SPEECH OUTPUT: 'begin '",
     "SPEECH OUTPUT: 'Speaks the current flat review item or word.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("5"))
sequence.append(utils.AssertPresentationAction(
    "4. Regular typing command",
    ["BRAILLE LINE:  'Learn mode.  Press escape to exit.'",
     "     VISIBLE:  'Learn mode.  Press escape to exi', cursor=0",
     "SPEECH OUTPUT: '5 '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Escape"))
sequence.append(utils.AssertPresentationAction(
    "5. Exit learn mode",
    ["BRAILLE LINE:  'Exiting learn mode.'",
     "     VISIBLE:  'Exiting learn mode.', cursor=0",
     "SPEECH OUTPUT: 'escape '",
     "SPEECH OUTPUT: 'Exiting learn mode.' voice=system"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
