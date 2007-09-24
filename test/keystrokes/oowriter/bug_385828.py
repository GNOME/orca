#!/usr/bin/python

"""Test to verify bug #385828 is still fixed.
   Can not use agenda wizard in OpenOffice.org.
"""

from macaroon.playback import *

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
# BRAILLE LINE:  'soffice Application Agenda Wizard Dialog Agenda Wizard OptionPane Steps Panel Page design Label'
# VISIBLE:  'Page design Label', cursor=1
# SPEECH OUTPUT: 'aw-5blue (read-only) - OpenOffice.org Writer frame'
# SPEECH OUTPUT: 'Agenda Wizard Please choose the page design for the agenda 1. Page design 2. General information 3. Headings to include 4. Names 5. Agenda items 6. Name and location'
# SPEECH OUTPUT: 'Page design label'
#
sequence.append(TypeAction("a"))
sequence.append(WaitForWindowActivate("aw-5blue (read-only) - OpenOffice.org Writer",None))
sequence.append(WaitForFocus("Page design", acc_role=pyatspi.ROLE_LABEL))

######################################################################
# 5. Press Escape to put focus back in the document.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 6. Wait for things to get back to normal.
#
sequence.append(PauseAction(3000))

sequence.start()
