#!/usr/bin/python

"""Test of page tab output using Firefox.
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
# In the Page Setup dialog, shift+tab to the page tabs. The following 
# should be presented in speech and braille:
#
# BRAILLE LINE:  'Minefield Application Page Setup Dialog Format & Options'
#      VISIBLE:  'Format & Options', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Format & Options page'
#
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(WaitForFocus("Format & Options", acc_role=pyatspi.ROLE_PAGE_TAB))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
# BRAILLE LINE:  'Minefield Application Page Setup Dialog Format & Options'
#      VISIBLE:  'Format & Options', cursor=1
# SPEECH OUTPUT: 'tab list'
# SPEECH OUTPUT: 'Format & Options page'
# SPEECH OUTPUT: 'item 1 of 2'
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Right Arrow to move to the second page tab.  The following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'Minefield Application Page Setup Dialog Margins & Header/Footer'
#      VISIBLE:  'Margins & Header/Footer', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Margins & Header/Footer page'
#
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Margins & Header/Footer", acc_role=pyatspi.ROLE_PAGE_TAB))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'Minefield Application Page Setup Dialog Margins & Header/Footer'
#     VISIBLE:  'Margins & Header/Footer', cursor=1
# SPEECH OUTPUT: 'tab list'
# SPEECH OUTPUT: 'Margins & Header/Footer page'
# SPEECH OUTPUT: 'item 2 of 2'
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Left Arrow to return to the first page tab.  The following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'Minefield Application Page Setup Dialog Format & Options'
#      VISIBLE:  'Format & Options', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Format & Options page'
#
sequence.append(KeyComboAction("Left"))
sequence.append(WaitForFocus("Format & Options", acc_role=pyatspi.ROLE_PAGE_TAB))

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
