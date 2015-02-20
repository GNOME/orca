#!/usr/bin/python

"""Test of learn mode."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(TypeAction("h"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))

sequence.append(KeyComboAction("F1"))
sequence.append(PauseAction(2000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("k"))
sequence.append(utils.AssertPresentationAction(
    "1. k for next link",
    ["BRAILLE LINE:  ' Welcome to Orca'",
     "     VISIBLE:  ' Welcome to Orca', cursor=2",
     "BRAILLE LINE:  ' Welcome to Orca'",
     "     VISIBLE:  ' Welcome to Orca', cursor=2",
     "SPEECH OUTPUT: 'Welcome to Orca",
     "Introducing the Orca screen reader",
     " link'"]))

sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(2000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("l"))
sequence.append(utils.AssertPresentationAction(
    "2. l for next list",
    ["BRAILLE LINE:  'List with 3 items'",
     "     VISIBLE:  'List with 3 items', cursor=0",
     "BRAILLE LINE:  ' The method for configuring Orca to be launched automatically as your preferred screen reader will depend upon which desktop environment you use. For instance, in GNOME 3.x this option can be found in the Universal Access Control Center panel on the Seeing page.'",
     "     VISIBLE:  ' The method for configuring Orca', cursor=0",
     "BRAILLE LINE:  ' The method for configuring Orca to be launched automatically as your preferred screen reader will depend upon which desktop environment you use. For instance, in GNOME 3.x this option can be found in the Universal Access Control Center panel on the Seeing page.'",
     "     VISIBLE:  ' The method for configuring Orca', cursor=0",
     "SPEECH OUTPUT: 'List with 3 items'",
     "SPEECH OUTPUT: '\u2022 The method for configuring Orca to be launched automatically as '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("l"))
sequence.append(utils.AssertPresentationAction(
    "3. l for next list",
    ["BRAILLE LINE:  'List with 11 items'",
     "     VISIBLE:  'List with 11 items', cursor=0",
     "BRAILLE LINE:  ' -h, --help: Show the help message'",
     "     VISIBLE:  ' -h, --help: Show the help messa', cursor=0",
     "BRAILLE LINE:  ' -h, --help: Show the help message'",
     "     VISIBLE:  ' -h, --help: Show the help messa', cursor=0",
     "SPEECH OUTPUT: 'List with 11 items'",
     "SPEECH OUTPUT: '\u2022 -h, --help: Show the help message'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("l"))
sequence.append(utils.AssertPresentationAction(
    "4. l for next list",
    ["BRAILLE LINE:  'List with 3 items'",
     "     VISIBLE:  'List with 3 items', cursor=0",
     "BRAILLE LINE:  ' speech'",
     "     VISIBLE:  ' speech', cursor=0",
     "BRAILLE LINE:  ' speech'",
     "     VISIBLE:  ' speech', cursor=0",
     "SPEECH OUTPUT: 'List with 3 items'",
     "SPEECH OUTPUT: '\u25e6 speech'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>l"))
sequence.append(utils.AssertPresentationAction(
    "5. shift+l for previous list",
    ["BRAILLE LINE:  'List with 3 items'",
     "     VISIBLE:  'List with 3 items', cursor=0",
     "BRAILLE LINE:  ' The method for configuring Orca to be launched automatically as your preferred screen reader will depend upon which desktop environment you use. For instance, in GNOME 3.x this option can be found in the Universal Access Control Center panel on the Seeing page.'",
     "     VISIBLE:  ' The method for configuring Orca', cursor=0",
     "BRAILLE LINE:  ' The method for configuring Orca to be launched automatically as your preferred screen reader will depend upon which desktop environment you use. For instance, in GNOME 3.x this option can be found in the Universal Access Control Center panel on the Seeing page.'",
     "     VISIBLE:  ' The method for configuring Orca', cursor=0",
     "SPEECH OUTPUT: 'List with 3 items'",
     "SPEECH OUTPUT: '\u2022 The method for configuring Orca to be launched automatically as '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>l"))
sequence.append(utils.AssertPresentationAction(
    "6. shift+l for previous list",
    ["BRAILLE LINE:  'Wrapping to bottom.'",
     "     VISIBLE:  'Wrapping to bottom.', cursor=0",
     "BRAILLE LINE:  'List with 1 item'",
     "     VISIBLE:  'List with 1 item', cursor=0",
     "BRAILLE LINE:  ' Getting Started'",
     "     VISIBLE:  ' Getting Started', cursor=0",
     "BRAILLE LINE:  ' Getting Started'",
     "     VISIBLE:  ' Getting Started', cursor=0",
     "SPEECH OUTPUT: 'Wrapping to bottom.'",
     "SPEECH OUTPUT: 'List with 1 item'",
     "SPEECH OUTPUT: 'Getting Started link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>l"))
sequence.append(utils.AssertPresentationAction(
    "7. shift+l for previous list",
    ["BRAILLE LINE:  'List with 3 items'",
     "     VISIBLE:  'List with 3 items', cursor=0",
     "BRAILLE LINE:  ' speech'",
     "     VISIBLE:  ' speech', cursor=0",
     "BRAILLE LINE:  ' speech'",
     "     VISIBLE:  ' speech', cursor=0",
     "SPEECH OUTPUT: 'List with 3 items'",
     "SPEECH OUTPUT: '\u25e6 speech'"]))

sequence.append(KeyComboAction("<Alt>F4"))
sequence.append(utils.AssertionSummaryAction())
sequence.start()
