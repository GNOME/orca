#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(TypeAction("vim"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("a"))
sequence.append(utils.AssertPresentationAction(
    "1. A to append text",
    ["BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame '",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: '-- INSERT --                                                  0,1  '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("Hi Hi"))
sequence.append(utils.AssertPresentationAction(
    "2. Type 'Hi Hi'",
    ["BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame H'",
     "     VISIBLE:  'H', cursor=2",
     "BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame H'",
     "     VISIBLE:  'H', cursor=2",
     "BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi'",
     "     VISIBLE:  'Hi', cursor=3",
     "BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi'",
     "     VISIBLE:  'Hi', cursor=3",
     "BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi'",
     "     VISIBLE:  'Hi', cursor=3",
     "BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi H'",
     "     VISIBLE:  'Hi H', cursor=5",
     "BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi H'",
     "     VISIBLE:  'Hi H', cursor=5",
     "BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi Hi'",
     "     VISIBLE:  'Hi Hi', cursor=6",
     "BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi Hi'",
     "     VISIBLE:  'Hi Hi', cursor=6"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "3. BackSpace",
    ["BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi H'",
     "     VISIBLE:  'Hi H', cursor=5",
     "BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi H'",
     "     VISIBLE:  'Hi H', cursor=5",
     "BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi H'",
     "     VISIBLE:  'Hi H', cursor=5",
     "SPEECH OUTPUT: 'i'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "4. BackSpace",
    ["BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi '",
     "     VISIBLE:  'Hi ', cursor=4",
     "BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi '",
     "     VISIBLE:  'Hi ', cursor=4",
     "BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi '",
     "     VISIBLE:  'Hi ', cursor=4",
     "SPEECH OUTPUT: 'H'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "5. BackSpace",
    ["BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi '",
     "     VISIBLE:  'Hi ', cursor=3",
     "BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi '",
     "     VISIBLE:  'Hi ', cursor=3",
     "BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi '",
     "     VISIBLE:  'Hi ', cursor=3",
     "SPEECH OUTPUT: '4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("!"))
sequence.append(utils.AssertPresentationAction(
    "6. Type '!'",
    ["BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi!'",
     "     VISIBLE:  'Hi!', cursor=4",
     "BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi!'",
     "     VISIBLE:  'Hi!', cursor=4"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "7. Return",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
