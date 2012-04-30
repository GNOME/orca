#!/usr/bin/python

"""Test to verify bug #364765 is still fixed.
   Escaping out of Wizards submenu in OOo Writer causes Orca to report 
   "Format menu".
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

######################################################################
# 1. Start oowriter.
#
sequence.append(WaitForWindowActivate("Untitled 1 - " + utils.getOOoName("Writer"), None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 2. Enter Alt-f, to display the File menu.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

######################################################################
# 3. Press W to open the Wizards submenu.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("w"))
sequence.append(WaitForFocus("Letter...", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "Press W to open the Wizards submenu",
    ["BRAILLE LINE:  'soffice Application Untitled 1 - " + utils.getOOoName("Writer") + " Frame Untitled 1 - " + utils.getOOoName("Writer") + " RootPane MenuBar Wizards Menu'",
     "     VISIBLE:  'Wizards Menu', cursor=1",
     "BRAILLE LINE:  'soffice Application Untitled 1 - " + utils.getOOoName("Writer") + " Frame Untitled 1 - " + utils.getOOoName("Writer") + " RootPane MenuBar File Menu Letter...'",
     "     VISIBLE:  'Letter...', cursor=1",
     "SPEECH OUTPUT: 'Wizards menu'",
     "SPEECH OUTPUT: 'Letter...'"]))

######################################################################
# 4. Press Escape to close the Wizards submenu.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("Wizards", acc_role=pyatspi.ROLE_MENU))
sequence.append(utils.AssertPresentationAction(
    "Press Escape to close the Wizards submenu",
    ["BRAILLE LINE:  'soffice Application Untitled 1 - " + utils.getOOoName("Writer") + " Frame Untitled 1 - " + utils.getOOoName("Writer") + " RootPane MenuBar Wizards Menu'",
     "     VISIBLE:  'Wizards Menu', cursor=1",
     "SPEECH OUTPUT: 'Wizards menu'"]))

######################################################################
# 5. Press Escape to close the File submenu.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("File", acc_role=pyatspi.ROLE_MENU))

######################################################################
# 6. Press Escape to put focus back in the document.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 7. Wait for things to get back to normal.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
