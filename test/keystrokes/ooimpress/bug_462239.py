#!/usr/bin/python

"""Test to verify bug #462239 is still fixed.
   OpenOffice OOo-dev 2.3.0 Presentation application crashes when trying 
   to open an existing presentation.
"""

from macaroon.playback import *

sequence = MacroSequence()

######################################################################
# 1. Start ooimpress. There is a bug_462239.params file that will
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
# 2. Enter Alt-f, Alt-c to close the presentation window.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("<Alt>c"))
sequence.append(WaitAction("object:property-change:accessible-name",
                           None,
                           None,
                           pyatspi.ROLE_ROOT_PANE,
                           30000))

######################################################################
# 3. Wait for things to get back to normal.
#
sequence.append(PauseAction(3000))

sequence.start()
