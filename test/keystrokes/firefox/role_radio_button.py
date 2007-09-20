#!/usr/bin/python

"""Test of radio button output using Firefox.
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
# In the Page Setup dialog, focus should already be on the "Portrait"
# radio button.  Right Arrow to the "Landscape" radio button. The 
# following should be presented in speech and braille:
#
# BRAILLE LINE:  'Minefield Application Page Setup Dialog ScrollPane Orientation: Panel &=y Landscape RadioButton'
#     VISIBLE:  '&=y Landscape RadioButton', cursor=1
# SPEECH OUTPUT: 'Orientation: panel'
# SPEECH OUTPUT: 'Landscape selected radio button'
#
# Note that the Orientation panel was also announced because we currently
# do not get a focus event for the Portrait radio button which initially
# is focused when the dialog box appeared.  Thus it's new context as far
# as we're concerned. https://bugzilla.mozilla.org/show_bug.cgi?id=388187
#
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Landscape", acc_role=pyatspi.ROLE_RADIO_BUTTON))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'Minefield Application Page Setup Dialog ScrollPane Orientation: Panel &=y Landscape RadioButton'
#      VISIBLE:  '&=y Landscape RadioButton', cursor=1
# SPEECH OUTPUT: 'Orientation:'
# SPEECH OUTPUT: 'Landscape radio button'
# SPEECH OUTPUT: 'selected'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Left Arrow to return to the "Portrait" radio button.  The following 
# should be presented in speech and braille:
#
# BRAILLE LINE:  'Minefield Application Page Setup Dialog ScrollPane Orientation: Panel &=y Portrait RadioButton'
#      VISIBLE:  '&=y Portrait RadioButton', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Portrait selected radio button'
#
sequence.append(KeyComboAction("Left"))
sequence.append(WaitForFocus("Portrait", acc_role=pyatspi.ROLE_RADIO_BUTTON))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'Minefield Application Page Setup Dialog ScrollPane Orientation: Panel &=y Portrait RadioButton'
#     VISIBLE:  '&=y Portrait RadioButton', cursor=1
# SPEECH OUTPUT: 'Orientation:'
# SPEECH OUTPUT: 'Portrait radio button'
# SPEECH OUTPUT: 'selected'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Dismiss the dialog by pressing Escape and wait for the location bar
# to regain focus.
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
