#!/usr/bin/python

"""Test of menus in Java's SwingSet2.
"""

from macaroon.playback.keypress_mimic import *

sequence = MacroSequence()

##########################################################################
# We wait for the demo to come up and for focus to be on the toggle button
#
#sequence.append(WaitForWindowActivate("SwingSet2",None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))

# Wait for entire window to get populated.
sequence.append(PauseAction(5000))

sequence.append(KeyComboAction("<Alt>f"))

##########################################################################
# Expected output when File menu is invoked.
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane File Menu'
#      VISIBLE:  'File Menu', cursor=1
# 
# SPEECH OUTPUT: 'Swing demo menu bar menu bar'
# SPEECH OUTPUT: 'File menu'
sequence.append(WaitForFocus("File", acc_role=pyatspi.ROLE_MENU))

########################################################################
# [[[Bug 483208: Exception raised when performing where am I]]]
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech:
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

sequence.append(KeyComboAction("Right"))

##########################################################################
# Expected output when Look & Feel menu is in focus.
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Look & Feel Menu'
#      VISIBLE:  'Look & Feel Menu', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Look & Feel menu'
sequence.append(WaitForFocus("Look & Feel", acc_role=pyatspi.ROLE_MENU))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech:
#
# SPEECH OUTPUT: 'Swing demo menu bar menu bar'
# SPEECH OUTPUT: 'Look & Feel'
# SPEECH OUTPUT: 'menu'
# SPEECH OUTPUT: ''
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

sequence.append(KeyComboAction("Right"))

##########################################################################
# Expected output when Themes menu is in focus.
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Themes Menu'
#      VISIBLE:  'Themes Menu', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Themes menu'
sequence.append(WaitForFocus("Themes", acc_role=pyatspi.ROLE_MENU))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech:
#
# SPEECH OUTPUT: 'Swing demo menu bar menu bar'
# SPEECH OUTPUT: 'Themes'
# SPEECH OUTPUT: 'menu'
# SPEECH OUTPUT: ''
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

sequence.append(KeyComboAction("Down"))

##########################################################################
# Expected output when Themes menu is in focus.
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar Audio Menu'
#      VISIBLE:  'Audio Menu', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Audio menu'
sequence.append(WaitForFocus("Audio", acc_role=pyatspi.ROLE_MENU))

########################################################################
# [[[Bug 483208: Exception raised when performing where am I]]]
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech:
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

# Leave menus.
sequence.append(KeyComboAction("Escape"))

sequence.append(PauseAction(5000))

sequence.start()
