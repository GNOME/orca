#!/usr/bin/python

"""Test of status bar output of Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the local status bar test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "status-bar.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Status Bar Regression Test",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Tab to move to the first push button, "Who expects the Spanish
# Inquistion?".  When it has focus, press it with the space bar which
# will cause the status bar text to display the following text:
# "NOBODY expects the Spanish Inquisition!"
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Who expects the Spanish Inquisition?",
                             acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(TypeAction(" "))

########################################################################
# Double-click Orca_Modifier+KP_Enter to read the status bar.
# [[[Bug: Gecko's readPageSummary() should, I believe, only kick in for
# unmodified double-clicks of KP_Enter.  Currently it kicks in for both.
# See bug #480501.]]] [[[Bug? As has been observed in other tests, the
# double-click doesn't always "take".  Sometimes it's treated as a
# single click; other times it's treated as a double click, but we have
# already started speaking the single click stuff.]]]
#
# BRAILLE LINE:  'Who expects the Spanish Inquisition? Button'
#      VISIBLE:  'Who expects the Spanish Inquisit', cursor=1
# SPEECH OUTPUT: 'Status Bar Regression Test - Minefield'
# SPEECH OUTPUT: '1 form'
# SPEECH OUTPUT: '60 percent of document read'
#
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(PauseAction(3000))

########################################################################
# Press Tab to move to the second push button, "Our chief weapon is..."
# When it has focus, press it with the space bar which will cause the 
# the status bar to display the following text:
# "Surprise.  Surprise and fear. Fear and surprise... And ruthless 
# efficiency...  And an almost fanatical devotion to the Pope... And nice
# red uniforms."
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Our chief weapon is...",
                             acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(TypeAction(" "))

########################################################################
# Double-click Orca_Modifier+KP_Enter to read the status bar.
# (See comments above re bugs).
#
# BRAILLE LINE:  'Our chief weapon is... Button'
#      VISIBLE:  'Our chief weapon is... Button', cursor=1
# SPEECH OUTPUT: 'Status Bar Regression Test - Minefield'
# SPEECH OUTPUT: '1 form'
# SPEECH OUTPUT: '80 percent of document read'
#
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(PauseAction(3000))

########################################################################
# Press Tab to move to the third push button, "Fetch the COMFY CHAIR
# (AKA clear out the status bar)".  When it has focus, press it with the
# space bar which will cause the status bar text to be removed, which
# causes Firefox to display "Done".
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus( \
                  "Fetch the COMFY CHAIR (AKA clear out the status bar)",
                   acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(TypeAction(" "))

########################################################################
# Double-click Orca_Modifier+KP_Enter to read the status bar.
# (See comments above re bugs).
#
# BRAILLE LINE:  'Fetch the COMFY CHAIR (AKA clear out the status bar) Button'
#      VISIBLE:  'Fetch the COMFY CHAIR (AKA clear', cursor=1
# SPEECH OUTPUT: 'Status Bar Regression Test - Minefield'
# SPEECH OUTPUT: '1 form'
# SPEECH OUTPUT: '100 percent of document read'
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(PauseAction(3000))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
