#!/usr/bin/python

"""Test of Mozilla ARIA tabpanel presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "Tabbed UI" frame.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the Mozilla ARIA slider demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://www.mozilla.org/access/dhtml/tabpanel"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Tabbed UI", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Give the widget a moment to construct itself
#
sequence.append(PauseAction(1000))

########################################################################
# Tab to the tabpanel.
#
# BRAILLE LINE:  'Tab One Tab Two Tab Three Tab Four Tab Five'
#      VISIBLE:  'Tab One Tab Two Tab Three Tab Fo', cursor=1
# SPEECH OUTPUT: 'Tab One page Tab Two page Tab Three page Tab Four page Tab Five page'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Tab One", acc_role=pyatspi.ROLE_PAGE_TAB))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'Tab One Tab Two Tab Three Tab Four Tab Five'
#      VISIBLE:  'Tab One Tab Two Tab Three Tab Fo', cursor=1
# SPEECH OUTPUT: 'section'
# SPEECH OUTPUT: 'Tab One page'
# SPEECH OUTPUT: 'item 1 of 1'
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Move to tab 2.
#
# BRAILLE LINE:  'Tab One Tab Two Tab Three Tab Four Tab Five'
#      VISIBLE:  'Tab Two Tab Three Tab Four Tab F', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Tab Two page'
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Tab Two", acc_role=pyatspi.ROLE_PAGE_TAB))

########################################################################
# Move to tab 3
#
# BRAILLE LINE:  'Tab One Tab Two Tab Three Tab Four Tab Five'
#      VISIBLE:  'Tab Three Tab Four Tab Five', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Tab Three page'
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Tab Three", acc_role=pyatspi.ROLE_PAGE_TAB))

########################################################################
# Move to tab 3 contents
#
# BRAILLE LINE:  '&=y RadioButton Internal Portal Bookmark & y RadioButton External URL '
#      VISIBLE:  '&=y RadioButton Internal Portal ', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Internal Portal Bookmark'
# SPEECH OUTPUT: 'selected radio button'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Internal Portal Bookmark", acc_role=pyatspi.ROLE_RADIO_BUTTON))

########################################################################
# Move back to tab 3
#
# BRAILLE LINE:  'Tab One Tab Two Tab Three Tab Four Tab Five'
#      VISIBLE:  'Tab Three Tab Four Tab Five', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Tab Three page'
#
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(WaitForFocus("Tab Three", acc_role=pyatspi.ROLE_PAGE_TAB))

########################################################################
# Move to tab 4
#
# BRAILLE LINE:  'Tab One Tab Two Tab Three Tab Four Tab Five'
#      VISIBLE:  'Tab Four Tab Five', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Tab Four page'
#
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Tab Four", acc_role=pyatspi.ROLE_PAGE_TAB))

########################################################################
# Move to tab 5
#
# BRAILLE LINE:  'Tab One Tab Two Tab Three Tab Four Tab Five'
#      VISIBLE:  'Tab Five', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Tab Five page'
#
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Tab Five", acc_role=pyatspi.ROLE_PAGE_TAB))

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
