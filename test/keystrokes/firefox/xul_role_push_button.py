#!/usr/bin/python

"""Test of push button output using Firefox.
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
# In the Page Setup dialog, shift+tab once to move to the page tabs.
#
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(WaitForFocus("Format & Options", acc_role=pyatspi.ROLE_PAGE_TAB))

########################################################################
# Shift+tab again to move to the OK push button. The following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'Minefield Application Page Setup Dialog OK Button'
#      VISIBLE:  'OK Button', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'OK button'
#
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(WaitForFocus("OK", acc_role=pyatspi.ROLE_PUSH_BUTTON))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'Minefield Application Page Setup Dialog OK Button'
#      VISIBLE:  'OK Button', cursor=1
# SPEECH OUTPUT: 'OK'
# SPEECH OUTPUT: 'button'
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Shift+tab again to move to the Cancel push button. The following 
# should be presented in speech and braille:
#
# BRAILLE LINE:  'Minefield Application Page Setup Dialog Cancel Button'
#      VISIBLE:  'Cancel Button', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Cancel button'
#
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(WaitForFocus("Cancel", acc_role=pyatspi.ROLE_PUSH_BUTTON))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'Minefield Application Page Setup Dialog Cancel Button'
#      VISIBLE:  'Cancel Button', cursor=1
# SPEECH OUTPUT: 'Cancel'
# SPEECH OUTPUT: 'button'
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Dismiss the dialog by pressing Space on the Cancel button and wait 
# for the location bar to regain focus.
#
sequence.append(TypeAction(" "))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
