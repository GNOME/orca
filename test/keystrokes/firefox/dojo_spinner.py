#!/usr/bin/python

"""Test of Dojo spinner presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "Dojo Spinner Widget Test" frame.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the dojo spinner demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction(utils.DojoURLPrefix + "form/test_Spinner.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Dojo Spinner Widget Test", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Give the widget a moment to construct itself
#
sequence.append(PauseAction(3000))

########################################################################
# Tab to the first spinner.  The following will be presented.  Note: ^ is an
# ascii substitute for the unicode up arrow to force the script to be syntactically
# correct. 
#
# BRAILLE LINE:  'Spinbox #1:  900 $l ^ Section'
#      VISIBLE:  'Spinbox #1:  900 $l ^ Section', cursor=17
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Spinbox #1:  900 spin button'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Spinbox #1:", acc_role=pyatspi.ROLE_SPIN_BUTTON))

########################################################################
# Use down arrow to decrement spinner value.  The following will be presented.
#
# BRAILLE LINE:  'Spinbox #1:  899 $l ^ Section'
#      VISIBLE:  'Spinbox #1:  899 $l ^ Section', cursor=17
# SPEECH OUTPUT: '899'
#
sequence.append(KeyComboAction("Down"))

########################################################################
# Use down arrow to decrement spinner value.  The following will be presented.
#
# BRAILLE LINE:  'Spinbox #1:  898 $l ^ Section'
#      VISIBLE:  'Spinbox #1:  898 $l ^ Section', cursor=17
# SPEECH OUTPUT: '898'
#
sequence.append(KeyComboAction("Down"))

########################################################################
# Use down arrow to decrement spinner value.  The following will be presented.
#
# BRAILLE LINE:  'Spinbox #1:  897 $l ^ Section'
#      VISIBLE:  'Spinbox #1:  897 $l ^ Section', cursor=17
# SPEECH OUTPUT: '897'
#
sequence.append(KeyComboAction("Down"))

########################################################################
# Use down arrow to decrement spinner value.  The following will be presented.
#
# BRAILLE LINE:  'Spinbox #1:  896 $l ^ Section'
#      VISIBLE:  'Spinbox #1:  896 $l ^ Section', cursor=17
# SPEECH OUTPUT: '896'
#
sequence.append(KeyComboAction("Down"))

########################################################################
# Use down arrow to decrement spinner value.  The following will be presented.
#
# BRAILLE LINE:  'Spinbox #1:  895 $l ^ Section'
#      VISIBLE:  'Spinbox #1:  895 $l ^ Section', cursor=17
# SPEECH OUTPUT: '895'
#
sequence.append(KeyComboAction("Down"))

########################################################################
# Use up arrow to increment spinner value.  The following will be presented.
#
# BRAILLE LINE:  'Spinbox #1:  896 $l ^ Section'
#      VISIBLE:  'Spinbox #1:  896 $l ^ Section', cursor=17
# SPEECH OUTPUT: '896'
#
sequence.append(KeyComboAction("Up"))

########################################################################
# Use up arrow to increment spinner value.  The following will be presented.
#
# BRAILLE LINE:  'Spinbox #1:  897 $l ^ Section'
#      VISIBLE:  'Spinbox #1:  897 $l ^ Section', cursor=17
# SPEECH OUTPUT: '897'
#
sequence.append(KeyComboAction("Up"))

########################################################################
# Use up arrow to increment spinner value.  The following will be presented.
#
# BRAILLE LINE:  'Spinbox #1:  898 $l ^ Section'
#      VISIBLE:  'Spinbox #1:  898 $l ^ Section', cursor=17
# SPEECH OUTPUT: '898'
#
sequence.append(KeyComboAction("Up"))

########################################################################
# Use up arrow to increment spinner value.  The following will be presented.
#
# BRAILLE LINE:  'Spinbox #1:  899 $l ^ Section'
#      VISIBLE:  'Spinbox #1:  899 $l ^ Section', cursor=17
# SPEECH OUTPUT: '899'
#
sequence.append(KeyComboAction("Up"))

########################################################################
# Use up arrow to increment spinner value.  The following will be presented.
#
# BRAILLE LINE:  'Spinbox #1:  900 $l ^ Section'
#      VISIBLE:  'Spinbox #1:  900 $l ^ Section', cursor=17
# SPEECH OUTPUT: '900'
#
sequence.append(KeyComboAction("Up"))

########################################################################
# Use up arrow to increment spinner value.  The following will be presented.
#
# BRAILLE LINE:  'Spinbox #1:  901 $l ^ Section'
#      VISIBLE:  'Spinbox #1:  901 $l ^ Section', cursor=17
# SPEECH OUTPUT: '901'
#
sequence.append(KeyComboAction("Up"))

########################################################################
# Use up arrow to increment spinner value.  The following will be presented.
#
# BRAILLE LINE:  'Spinbox #1:  902 $l ^ Section'
#      VISIBLE:  'Spinbox #1:  902 $l ^ Section', cursor=17
# SPEECH OUTPUT: '902'
#
sequence.append(KeyComboAction("Up"))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'Spinbox #1:  902 $l ^ Section'
#      VISIBLE:  'Spinbox #1:  902 $l ^ Section', cursor=17
# SPEECH OUTPUT: 'Spinbox #1: '
# SPEECH OUTPUT: 'spin button'
# SPEECH OUTPUT: '902'
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

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
