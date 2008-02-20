#!/usr/bin/python

"""Test to verify bug #450210 is still fixed.
   StarOffice.py needs null-check for self.getFrame(event.source).
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

######################################################################
# 1. Start oowriter.
#
sequence.append(WaitForWindowActivate("Untitled1 - OpenOffice.org Writer",None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 2. Enter Alt-f, to display the File menu.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

######################################################################
# 3. Press "o" to open the Open File Chooser.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("o"))
sequence.append(WaitAction("focus:",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           30000))
sequence.append(utils.AssertPresentationAction(
    "Press 'o' to open the Open File Chooser",
    ["BRAILLE LINE:  'soffice Application Open Dialog'",
     "     VISIBLE:  'soffice Application Open Dialog', cursor=21",
     "BRAILLE LINE:  'soffice Application Open Dialog Location:  $l'",
     "     VISIBLE:  'Location:  $l', cursor=11",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Open Version:'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Location: text '"]))

######################################################################
# 4. Press Escape to dismiss the Open File Chooser.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 5. Wait for things to get back to normal.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
