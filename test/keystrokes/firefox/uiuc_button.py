#!/usr/bin/python

"""Test of UIUC button presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "text/html: Button Example 1" frame.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the UIUC button demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://test.cita.uiuc.edu/aria/button/html.php?title=Button%20Example%201&ginc=includes/button1.inc&gcss=css/button1.css&gjs=../js/globals.js,../js/enable_app.js,js/button1.js"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("text/html: Button Example 1", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Tab to the first button.  The following will be presented.
#
#  BRAILLE LINE:  ' Reduce Text 1 Button'
#       VISIBLE:  ' Reduce Text 1 Button', cursor=1
# SPEECH OUTPUT: 'Button example 1 panel'
# SPEECH OUTPUT: ' Reduce Text 1 button'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus(" Reduce Text 1", acc_role=pyatspi.ROLE_PUSH_BUTTON))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
# BRAILLE LINE:  ' Reduce Text 1 Button'
#      VISIBLE:  ' Reduce Text 1 Button', cursor=1
# SPEECH OUTPUT: 'Reduce Text 1'
# SPEECH OUTPUT: 'button'
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Now push the first button.  The following will be presented.
#
# [[[Bug?: No output when button is pressed.]]]
#
sequence.append(TypeAction(" "))

########################################################################
# Tab to the second button.
#
# BRAILLE LINE:  ' Enlarge Text 1 Button'
#      VISIBLE:  ' Enlarge Text 1 Button', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ' Enlarge Text 1 button'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus(" Enlarge Text 1", acc_role=pyatspi.ROLE_PUSH_BUTTON))

########################################################################
# Now push the second button.  The following will be presented.
#
sequence.append(TypeAction(" "))

########################################################################
# Tab to the third button.
#
#  BRAILLE LINE:  ' Italicize Text 1 Button'
#       VISIBLE:  ' Italicize Text 1 Button', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ' Italicize Text 1 button'
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus(" Italicize Text 1", acc_role=pyatspi.ROLE_PUSH_BUTTON))

########################################################################
# Now push the third button.  The following will be presented.
#
sequence.append(TypeAction(" "))

########################################################################
# Tab to the fourth button.  The following will be presented.
#
#  BRAILLE LINE:  ' Bold Text 1 Button'
#       VISIBLE:  ' Bold Text 1 Button', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ' Bold Text 1 button'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus(" Bold Text 1", acc_role=pyatspi.ROLE_PUSH_BUTTON))

########################################################################
# Now push the fourth button.  The following will be presented.
#
sequence.append(TypeAction           ("  "))

########################################################################
# Now push the fourth button again.  The following will be presented.
#
sequence.append(TypeAction           ("  "))

########################################################################
# Close the demo
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_name="Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
