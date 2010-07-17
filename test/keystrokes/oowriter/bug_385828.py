#!/usr/bin/python

"""Test to verify bug #385828 is still fixed.
   Can not use agenda wizard in OpenOffice.org.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

######################################################################
# 1. Start oowriter.
#
sequence.append(WaitForWindowActivate("Untitled[ ]*1 - " + utils.getOOoName("Writer"),None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 2. Enter Alt-f, to display the File menu.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

######################################################################
# 3. Press "w" to open the Wizards submenu.
#
sequence.append(TypeAction("w"))
sequence.append(WaitForFocus("Letter...", acc_role=pyatspi.ROLE_MENU_ITEM))

######################################################################
# 4. Press "a" to bring up the Agenda... wizard.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("a"))
sequence.append(WaitForWindowActivate("aw-5blue (read-only) - " + utils.getOOoName("Writer"),None))
sequence.append(WaitForFocus("Page design", acc_role=pyatspi.ROLE_LABEL))
sequence.append(utils.AssertPresentationAction(
    "Press 'a' to bring up the Agenda... wizard",
    ["BRAILLE LINE:  " + utils.getOOoBrailleLine("Writer") + " Frame (1 dialog)'",
     "     VISIBLE:  'Frame (1 dialog)', cursor=1",
     "BRAILLE LINE:  " + utils.getOOoBrailleLine("Writer") + " Agenda Wizard Dialog'",
     "     VISIBLE:  'Agenda Wizard Dialog', cursor=1",
     "BRAILLE LINE:  " + utils.getOOoBrailleLine("Writer") + " Agenda Wizard Dialog Agenda Wizard OptionPane Steps Panel  \$l'",
     "     VISIBLE:  ' \$l', cursor=1",
     "SPEECH OUTPUT: 'frame 1 unfocused dialog'",
     "SPEECH OUTPUT: 'Agenda Wizard'",
     "SPEECH OUTPUT: 'Steps panel'"]))

######################################################################
# 5. Press Escape to put focus back in the document.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 6. Wait for things to get back to normal.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
