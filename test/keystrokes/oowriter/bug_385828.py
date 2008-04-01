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
sequence.append(WaitForWindowActivate("Untitled1 - OpenOffice.org Writer",None))
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
sequence.append(WaitForWindowActivate("aw-5blue (read-only) - OpenOffice.org Writer",None))
sequence.append(WaitForFocus("Page design", acc_role=pyatspi.ROLE_LABEL))
sequence.append(utils.AssertPresentationAction(
    "Press 'a' to bring up the Agenda... wizard",
    ["BRAILLE LINE:  'soffice Application aw-5blue (read-only) - OpenOffice.org Writer Frame'",
     "     VISIBLE:  'aw-5blue (read-only) - OpenOffic', cursor=1",
     "BRAILLE LINE:  'soffice Application Agenda Wizard Dialog'",
     "     VISIBLE:  'Agenda Wizard Dialog', cursor=1",
     "BRAILLE LINE:  'soffice Application Agenda Wizard Dialog Steps Panel Page design $l'",
     "     VISIBLE:  'Page design $l', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'aw-5blue (read-only) - OpenOffice.org Writer frame'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Agenda Wizard'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Page design label'"]))

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
