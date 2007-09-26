#!/usr/bin/python

"""Test of where Am I output in a dialog box using Firefox.
"""

from macaroon.playback import *

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Open the "File" menu and press U for the Page Setup dialog
#
sequence.append(KeyComboAction("<Alt>f"))

sequence.append(WaitForFocus("New Window", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(TypeAction("u"))

sequence.append(WaitForWindowActivate("Page Setup",None))

########################################################################
# Currently we aren't getting proper focus events for this dialog.
# Therefore press Tab once to trigger a focus event before proceeding.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Shrink To Fit Page Width", acc_role=pyatspi.ROLE_CHECK_BOX))

########################################################################
# Do modified "Where Am I" via Orca_Modifier + KP_Enter to get the title
# The following should be presented in speech and braille:
#
# BRAILLE LINE:  'Minefield Application Page Setup Dialog ScrollPane <x> Shrink To Fit Page Width CheckBox'
#      VISIBLE:  '<x> Shrink To Fit Page Width Che', cursor=1
# SPEECH OUTPUT: 'Page Setup'
#
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(PauseAction(3000))

########################################################################
# Do double-click modified "Where Am I" via Orca_Modifier + KP_Enter to
# get the default button. The following should be presented in speech 
# and braille [[[BUG? depending on the timing, the first click command
# still gets spoken]]].
#
# BRAILLE LINE:  'Minefield Application Page Setup Dialog ScrollPane <x> Shrink To Fit Page Width CheckBox'
#      VISIBLE:  '<x> Shrink To Fit Page Width Che', cursor=1
# SPEECH OUTPUT: 'Default button is OK'
#
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(PauseAction(3000))

########################################################################
# Dismiss the dialog by pressing Escape and wait for the location bar
# to regain focus.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
