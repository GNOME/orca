#!/usr/bin/python

"""Test of checkbox output using Firefox.
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
# In the Page Setup dialog, tab to the first check box.  When that check
# box gets focus, the following should be presented in speech and 
# braille:
#
# BRAILLE LINE:  'Minefield Application Page Setup Dialog ScrollPane <x> Shrink To Fit Page Width CheckBox'
#      VISIBLE:  '<x> Shrink To Fit Page Width Che', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Shrink To Fit Page Width check box checked'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Shrink To Fit Page Width", acc_role=pyatspi.ROLE_CHECK_BOX))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'Minefield Application Page Setup Dialog ScrollPane <x> Shrink To Fit Page Width CheckBox'
#      VISIBLE:  '<x> Shrink To Fit Page Width Che', cursor=1
# SPEECH OUTPUT: 'Shrink To Fit Page Width check box'
# SPEECH OUTPUT: 'checked'
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Toggle the state of the check box by pressing Space. The following 
# should be presented in speech and braille:
#
# BRAILLE LINE:  'Minefield Application Page Setup Dialog ScrollPane < > Shrink To Fit Page Width CheckBox'
#      VISIBLE:  '< > Shrink To Fit Page Width Che', cursor=1
# SPEECH OUTPUT: 'not checked'
#
sequence.append(TypeAction(" "))

sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_CHECK_BOX,
                           5000))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'Minefield Application Page Setup Dialog ScrollPane < > Shrink To Fit Page Width CheckBox'
#      VISIBLE:  '< > Shrink To Fit Page Width Che', cursor=1
# SPEECH OUTPUT: 'Shrink To Fit Page Width check box'
# SPEECH OUTPUT: 'not checked'
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Toggle the state of the check box by pressing Space. The following 
# should be presented in speech and braille:
#
# BRAILLE LINE:  'Minefield Application Page Setup Dialog ScrollPane <x> Shrink To Fit Page Width CheckBox'
#      VISIBLE:  '<x> Shrink To Fit Page Width Che', cursor=1
# SPEECH OUTPUT: 'checked'
#
sequence.append(TypeAction(" "))

sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_CHECK_BOX,
                           5000))

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
