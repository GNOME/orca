#!/usr/bin/python

"""Test of UIUC radio button presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "application/xhtml+xml: Radio Example 1" frame.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the UIUC button demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://test.cita.uiuc.edu/aria/radio/view_xhtml.php?title=Radio%20Example%201&ginc=includes/radio1_xhtml.inc&gcss=css/radio1_xhtml.css&gjs=../js/globals.js,../js/widgets_xhtml.js,js/radio1_xhtml.js"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("application/xhtml+xml: Radio Example 1", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Tab to the first radio button group (panel).
#
# BRAILLE LINE:  '& y Thai RadioButton'
#      VISIBLE:  '& y Thai RadioButton', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Lunch Options panel'
#
#sequence.append(KeyComboAction("Tab"))
#sequence.append(WaitForFocus("Lunch Options", acc_role=pyatspi.ROLE_PANEL))

########################################################################
# Move to the first radio button.
#
# BRAILLE LINE:  '& y Thai RadioButton'
#     VISIBLE:  '& y Thai RadioButton', cursor=1
# SPEECH OUTPUT: 'Lunch Options panel'
# SPEECH OUTPUT: 'Thai not selected radio button'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Thai", acc_role=pyatspi.ROLE_RADIO_BUTTON))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
# BRAILLE LINE:  '&=y Thai RadioButton'
#      VISIBLE:  '&=y Thai RadioButton', cursor=1
# SPEECH OUTPUT: 'Lunch Options'
# SPEECH OUTPUT: 'Thai radio button'
# SPEECH OUTPUT: 'selected'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Move to the second radio button.
#
# BRAILLE LINE:  '&=y Subway RadioButton'
#      VISIBLE:  '&=y Subway RadioButton', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Subway selected radio button'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Subway", acc_role=pyatspi.ROLE_RADIO_BUTTON))

########################################################################
# Move to the third radio button.
#
# BRAILLE LINE:  '&=y Jimmy Johns RadioButton'
#      VISIBLE:  '&=y Jimmy Johns RadioButton', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Jimmy Johns selected radio button'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Jimmy Johns", acc_role=pyatspi.ROLE_RADIO_BUTTON))

########################################################################
# Move to the fourth radio button.
#
# BRAILLE LINE:  '&=y Radio Maria RadioButton'
#      VISIBLE:  '&=y Radio Maria RadioButton', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Radio Maria selected radio button'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Radio Maria", acc_role=pyatspi.ROLE_RADIO_BUTTON))

########################################################################
# Move to the fifth radio button.
#
# BRAILLE LINE:  '&=y Rainbow Gardens RadioButton'
#      VISIBLE:  '&=y Rainbow Gardens RadioButton', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Rainbow Gardens selected radio button'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Rainbow Gardens", acc_role=pyatspi.ROLE_RADIO_BUTTON))

########################################################################
# Move to the second radio button group (panel).  Contrast to the first group
# where the "Water" radio button already has been selected.
#
# BRAILLE LINE:  '&=y Water RadioButton'
#      VISIBLE:  '&=y Water RadioButton', cursor=1
# SPEECH OUTPUT: 'Drink Options panel'
# SPEECH OUTPUT: 'Water selected radio button'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Water", acc_role=pyatspi.ROLE_RADIO_BUTTON))

########################################################################
# Move to the second radio button.
#
# BRAILLE LINE:  '&=y Tea RadioButton'
#      VISIBLE:  '&=y Tea RadioButton', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Tea selected radio button'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Tea", acc_role=pyatspi.ROLE_RADIO_BUTTON))

########################################################################
# Move back to the first radio button.
#
# BRAILLE LINE:  '&=y Water RadioButton'
#      VISIBLE:  '&=y Water RadioButton', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Water selected radio button'
#
sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("Water", acc_role=pyatspi.ROLE_RADIO_BUTTON))

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
