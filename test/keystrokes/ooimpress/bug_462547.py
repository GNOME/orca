#!/usr/bin/python

"""Test to verify bug #462547 is still fixed.
   OOo-dev 2.3.0 simpress application startup wizard hangs the desktop.
"""

from macaroon.playback import *

sequence = MacroSequence()

######################################################################
# 1. Start ooimpress. Wait for the first screen of the startup wizard
#    to appear.
#
# BRAILLE LINE:  'soffice Application Presentation Wizard Dialog Presentation Wizard OptionPane Next >> Button'
# VISIBLE:  'Next >> Button', cursor=1
# SPEECH OUTPUT: 'Presentation Wizard'
# SPEECH OUTPUT: 'Next >> button'
#
sequence.append(WaitForWindowActivate("Presentation Wizard", None))
sequence.append(WaitForFocus("Next", acc_role=pyatspi.ROLE_PUSH_BUTTON))

######################################################################
# 2. Press Space to get to the second screen of the startup wizard.
#
# BRAILLE LINE:  'soffice Application Presentation Wizard Dialog Presentation Wizard OptionPane Next >> Button'
# VISIBLE:  'Next >> Button', cursor=1
# SPEECH OUTPUT: 'Next >> button'
#
sequence.append(KeyComboAction("space"))

######################################################################
# 3. Press Space to get to the final screen of the startup wizard.
#
# BRAILLE LINE:  'soffice Application Presentation Wizard Dialog Presentation Wizard OptionPane Create Button'
# VISIBLE:  'Create Button', cursor=1
# SPEECH OUTPUT: 'Next >> button'
# SPEECH OUTPUT: 'Create button'
#
sequence.append(KeyComboAction("space"))
sequence.append(WaitForFocus("Create", acc_role=pyatspi.ROLE_PUSH_BUTTON))

######################################################################
# 4. Press Space to start up ooimpress with an empty presentation.
#
# BRAILLE LINE:  'soffice Application Untitled1 - OpenOffice.org Impress Frame Untitled1 - OpenOffice.org Impress RootPane ScrollPane'
# VISIBLE:  'ScrollPane', cursor=1
# SPEECH OUTPUT: 'Untitled1 - OpenOffice.org Impress frame'
# SPEECH OUTPUT: 'panel'
# SPEECH OUTPUT: 'scroll pane'
#
sequence.append(KeyComboAction("space"))
sequence.append(WaitForWindowActivate("Untitled1 - OpenOffice.org Impress", None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_SCROLL_PANE))

######################################################################
# 5. Enter Alt-f, Alt-c to close the presentation window.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("<Alt>c"))
sequence.append(WaitForFocus("Save", acc_role=pyatspi.ROLE_PUSH_BUTTON))

######################################################################
# 6. Enter Tab and Return to discard the current changes.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Discard", acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(KeyComboAction("Return"))

######################################################################
# 7. Wait for things to get back to normal.
#
sequence.append(PauseAction(3000))

sequence.start()
