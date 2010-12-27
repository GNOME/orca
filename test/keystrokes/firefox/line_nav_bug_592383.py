# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of navigation around a paragraph with a multi-line-high
initial character.
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

sequence.append(TypeAction(utils.htmlURLPrefix + "bug-592383.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Test",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file",
    ["BRAILLE LINE:  'This is a normal paragraph.'",
     "     VISIBLE:  'This is a normal paragraph.', cursor=1",
     "SPEECH OUTPUT: 'This is a normal paragraph.'"]))

########################################################################
# Press Down Arrow to move line by line to the end.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Down",
    ["BRAILLE LINE:  'So is this one, but the next one will not be.'",
     "     VISIBLE:  'So is this one, but the next one', cursor=1",
     "SPEECH OUTPUT: 'So is this one, but the next one will not be.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down",
    ["BRAILLE LINE:  'W'",
     "     VISIBLE:  'W', cursor=1",
     "SPEECH OUTPUT: 'W' voice=uppercase"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Down",
    ["BRAILLE LINE:  '   hy did the chicken cross the road? Give up? It was to escape from the enormous capital letter at the beginning of this paragraph. These are the'",
     "     VISIBLE:  '   hy did the chicken cross the ', cursor=1",
     "SPEECH OUTPUT: '   hy did the chicken cross the road? Give up? It was to escape from the enormous capital letter at the beginning of this paragraph. These are the'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Down",
    ["BRAILLE LINE:  'things that keep chickens up at night. No. Really.They are.'",
     "     VISIBLE:  'things that keep chickens up at ', cursor=1",
     "SPEECH OUTPUT: 'things that keep chickens up at night. No. Really.They are.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Down",
    ["BRAILLE LINE:  'Here's another normal paragraph.'",
     "     VISIBLE:  'Here's another normal paragraph.', cursor=1",
     "SPEECH OUTPUT: 'Here's another normal paragraph.'"]))

########################################################################
# Press Control+End to move to the end.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>End"))
sequence.append(utils.AssertPresentationAction(
    "End of file", 
    ["BRAILLE LINE:  'Here's another normal paragraph.'",
     "     VISIBLE:  'Here's another normal paragraph.', cursor=32",
     "SPEECH OUTPUT: 'Here's another normal paragraph.'"]))

########################################################################
# Press Up Arrow to move line by line to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "1. Up",
    ["BRAILLE LINE:  'things that keep chickens up at night. No. Really.They are.'",
     "     VISIBLE:  'things that keep chickens up at ', cursor=1",
     "SPEECH OUTPUT: 'things that keep chickens up at night. No. Really.They are.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "2. Up",
    ["BRAILLE LINE:  '   hy did the chicken cross the road? Give up? It was to escape from the enormous capital letter at the beginning of this paragraph. These are the'",
     "     VISIBLE:  '   hy did the chicken cross the ', cursor=1",
     "SPEECH OUTPUT: '   hy did the chicken cross the road? Give up? It was to escape from the enormous capital letter at the beginning of this paragraph. These are the'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "3. Up",
    ["BRAILLE LINE:  'W'",
     "     VISIBLE:  'W', cursor=1",
     "SPEECH OUTPUT: 'W' voice=uppercase"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Up",
    ["BRAILLE LINE:  'So is this one, but the next one will not be.'",
     "     VISIBLE:  'So is this one, but the next one', cursor=1",
     "SPEECH OUTPUT: 'So is this one, but the next one will not be.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "5. Up",
    ["BRAILLE LINE:  'This is a normal paragraph.'",
     "     VISIBLE:  'This is a normal paragraph.', cursor=1",
     "SPEECH OUTPUT: 'This is a normal paragraph.'"]))

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
