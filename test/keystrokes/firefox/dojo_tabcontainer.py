#!/usr/bin/python

"""Test of Dojo tab container presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "TabContainer Demo" frame.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the dojo tab container demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction(utils.DojoURLPrefix + "layout/test_TabContainer.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("TabContainer Demo", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Give the widget a moment to construct itself
#
sequence.append(PauseAction(3000))

########################################################################
# Tab to 'Tab 2'.  The following will be presented.
#
# BRAILLE LINE:  'Tab 1 Tab 2 Tab 3 Another Tab Sub TabContainer'
#      VISIBLE:  'Tab 2 Tab 3 Another Tab Sub TabC', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Tab 2 page'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Tab 2", acc_role=pyatspi.ROLE_PAGE_TAB))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'Tab 1 Tab 2 Tab 3 Another Tab Sub TabContainer'
#      VISIBLE:  'Tab 2 Tab 3 Another Tab Sub TabC', cursor=1
# SPEECH OUTPUT: 'section'
# SPEECH OUTPUT: 'Tab 2 page'
# SPEECH OUTPUT: 'item 1 of 1'
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Use arrows to move between tabs: 'Tab 3'.  The following will be presented.
#
# BRAILLE LINE:  'Tab 1 Tab 2 Tab 3 Another Tab Sub TabContainer'
#      VISIBLE:  'Tab 3 Another Tab Sub TabContain', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Tab 3 page'
#
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Tab 3", acc_role=pyatspi.ROLE_PAGE_TAB))

########################################################################
# Use arrows to move between tabs: 'Another Tab'.  The following will be presented.
#
# BRAILLE LINE:  'Tab 1 Tab 2 Tab 3 Another Tab Sub TabContainer'
#      VISIBLE:  'Another Tab Sub TabContainer', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Another Tab page'
#
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Another Tab", acc_role=pyatspi.ROLE_PAGE_TAB))

########################################################################
# Use arrows to move between tabs: 'Sub TabContainer'.  The following will be presented.
#
# BRAILLE LINE:  'Tab 1 Tab 2 Tab 3 Another Tab Sub TabContainer'
#      VISIBLE:  'Sub TabContainer', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Sub TabContainer page'
#
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Sub TabContainer", acc_role=pyatspi.ROLE_PAGE_TAB))

########################################################################
# Tab to 'SubTab2'.  The following will be presented.
#
# BRAILLE LINE:  'SubTab 1 SubTab 2'
#      VISIBLE:  'SubTab 1 SubTab 2', cursor=10
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'SubTab 2 page'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("SubTab 2", acc_role=pyatspi.ROLE_PAGE_TAB))

########################################################################
# Use arrows to move between tabs: 'SubTab1'.  The following will be presented
#
# BRAILLE LINE:  'SubTab 1 SubTab 2'
#      VISIBLE:  'SubTab 1 SubTab 2', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'SubTab 1 page'
#
sequence.append(KeyComboAction("Left"))
sequence.append(WaitForFocus("SubTab 1", acc_role=pyatspi.ROLE_PAGE_TAB))

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
