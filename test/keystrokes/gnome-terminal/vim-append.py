#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(TypeAction("vim"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))

# KNOWN ISSUE: Sometimes we display the frame and sometimes we don't.
# It seems to be a timing issue.

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("a"))
sequence.append(utils.AssertPresentationAction(
    "1. A to append text",
    ["BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame '",
     "     VISIBLE:  '(frame |)', cursor=1",
     "SPEECH OUTPUT: '-- INSERT --                                                  0,1  '"]))

sequence.append(TypeAction("Hi H"))
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("i"))
sequence.append(utils.AssertPresentationAction(
    "2. Finish typing 'Hi Hi'",
    ["BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi Hi'",
     "     VISIBLE:  '(frame |)Hi Hi', cursor=(6|12)",
     "BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi Hi'",
     "     VISIBLE:  '(frame |)Hi Hi', cursor=(6|12)"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "3. BackSpace",
    ["BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi H'",
     "     VISIBLE:  '(frame |)Hi H', cursor=(5|11)",
     "BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi H'",
     "     VISIBLE:  '(frame |)Hi H', cursor=(5|11)",
     "BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi H'",
     "     VISIBLE:  '(frame |)Hi H', cursor=(5|11)",
     "SPEECH OUTPUT: 'i'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "4. BackSpace",
    ["BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi '",
     "     VISIBLE:  '(frame |)Hi ', cursor=(4|10)",
     "BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi '",
     "     VISIBLE:  '(frame |)Hi ', cursor=(4|10)",
     "BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi '",
     "     VISIBLE:  '(frame |)Hi ', cursor=(4|10)",
     "SPEECH OUTPUT: 'H'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "5. BackSpace",
    ["KNOWN ISSUE: We're speaking '4', possibly due to a heuristic",
     "BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi '",
     "     VISIBLE:  '(frame |)Hi ', cursor=(3|9)",
     "BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi '",
     "     VISIBLE:  '(frame |)Hi ', cursor=(3|9)",
     "BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi '",
     "     VISIBLE:  '(frame |)Hi ', cursor=(3|9)",
     "SPEECH OUTPUT: '4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("!"))
sequence.append(utils.AssertPresentationAction(
    "6. Type '!'",
    ["BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi!'",
     "     VISIBLE:  '(frame |)Hi!', cursor=(4|10)",
     "BRAILLE LINE:  'gnome-terminal-server application \w+@\w+:/tmp/gnome-terminal-wd frame Hi!'",
     "     VISIBLE:  '(frame |)Hi!', cursor=(4|10)"]))

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
