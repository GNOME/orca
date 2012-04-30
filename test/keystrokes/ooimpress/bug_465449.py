#!/usr/bin/python

"""Test to verify bug #465449 is still fixed.
   OOo simpress crashes when trying to change view modes.
"""

from macaroon.playback import *

sequence = MacroSequence()

######################################################################
# 1. Start ooimpress. There is a bug_465449.params file that will
#    automatically load subtlewave.ods.
#
# BRAILLE LINE:  'soffice Application subtlewaves - OpenOffice.org Impress Frame subtlewaves - OpenOffice.org Impress RootPane ScrollPane'
# VISIBLE:  'ScrollPane', cursor=1
# SPEECH OUTPUT: 'frame'
# SPEECH OUTPUT: 'root pane'
# SPEECH OUTPUT: 'scroll pane'
#
sequence.append(WaitForWindowActivate("subtlewaves - OpenOffice.org Impress", None))

######################################################################
# 2. Enter Alt-v, down arrow and Return to change to an Outline view.
#
# BRAILLE LINE:  'soffice Application subtlewaves - OpenOffice.org Impress Frame subtlewaves - OpenOffice.org Impress RootPane ScrollPane'
# VISIBLE:  'ScrollPane', cursor=1
# SPEECH OUTPUT: 'View menu'
# SPEECH OUTPUT: 'scroll pane'
#
sequence.append(KeyComboAction("<Alt>v"))
sequence.append(WaitForFocus("Normal", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Outline", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("Paragraph 0", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 3. Enter Alt-f, Alt-c to close the presentation window.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("<Alt>c"))
sequence.append(WaitForFocus("Save", acc_role=pyatspi.ROLE_PUSH_BUTTON))

######################################################################
# 4. Enter Tab and Return to discard any changes.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Discard", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Return"))

######################################################################
# 5. Wait for things to get back to normal.
#
sequence.append(PauseAction(3000))

sequence.start()
