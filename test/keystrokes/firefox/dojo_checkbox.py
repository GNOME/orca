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
sequence.append(TypeAction(utils.DojoURLPrefix + "form/test_CheckBox.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("CheckBox Widget Demo", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Give the widget a moment to construct itself
#
sequence.append(PauseAction(3000))

########################################################################
# Tab to the cb0 checkbox.  The following will be presented.
#
# BRAILLE LINE:  '< > CheckBox cb0: Vanilla (non-dojo) checkbox (for comparison purposes) '
#     VISIBLE:  '< > CheckBox cb0: Vanilla (non-d', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'cb0: Vanilla (non-dojo) checkbox (for comparison purposes) check box not checked'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("cb0: Vanilla (non-dojo) checkbox (for comparison purposes)", acc_role=pyatspi.ROLE_CHECK_BOX))

########################################################################
# Now, change its state.  The following should be presented in speech
# and braille:
#
# BRAILLE LINE:  '<x> CheckBox cb0: Vanilla (non-dojo) checkbox (for comparison purposes) '
#     VISIBLE:  '<x> CheckBox cb0: Vanilla (non-d', cursor=1
# SPEECH OUTPUT: 'checked'
#
sequence.append(TypeAction(" "))

########################################################################
# Tab to the cb1 checkbox.  The following will be presented.
#
# BRAILLE LINE:  '< > CheckBox cb1: normal checkbox, with value=foo '
#     VISIBLE:  '< > CheckBox cb1: normal checkbo', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'cb1: normal checkbox, with value=foo check box not checked'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("cb1: normal checkbox, with value=foo", acc_role=pyatspi.ROLE_CHECK_BOX))

########################################################################
# Now, change its state.  The following should be presented in speech
# and braille:
#
# BRAILLE LINE:  '<x> CheckBox cb1: normal checkbox, with value=foo '
#     VISIBLE:  '<x> CheckBox cb1: normal checkbo', cursor=1
# SPEECH OUTPUT: 'checked'
#
sequence.append(TypeAction("  "))

########################################################################
# Tab to the cb2 checkbox.  The following should be presented.
#
#BRAILLE LINE:  '<x> CheckBox cb2: normal checkbox, initially turned on. "onChange" handler updates: [true]'
#     VISIBLE:  '<x> CheckBox cb2: normal checkbo', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'cb2: normal checkbox, initially turned on. check box checked'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("cb2: normal checkbox, initially turned on.", acc_role=pyatspi.ROLE_CHECK_BOX))

########################################################################
# Tab to the cb5 checkbox.  Note: cb3 and cb4 are disabled.  The following should 
# be presented.
#
# BRAILLE LINE:  '< > CheckBox cb5: Vanilla (non-dojo) checkbox (for comparison purposes) '
#     VISIBLE:  '< > CheckBox cb5: Vanilla (non-d', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'cb5: Vanilla (non-dojo) checkbox (for comparison purposes) check box not checked'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("cb5: Vanilla (non-dojo) checkbox (for comparison purposes)", acc_role=pyatspi.ROLE_CHECK_BOX))

########################################################################
# Tab to the cb6 checkbox.  The following should be presented.
#
# BRAILLE LINE:  '<x> CheckBox cb6: instantiated from script '
#     VISIBLE:  '<x> CheckBox cb6: instantiated f', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'cb6: instantiated from script check box checked'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("cb6: instantiated from script", acc_role=pyatspi.ROLE_CHECK_BOX))

########################################################################
# Tab to the cb7 checkbox.  The following should be presented.
#
# BRAILLE LINE:  '< > CheckBox cb7: normal checkbox. disable Button enable Button set value to "fish" Button "onChange" handler updates: [false]'
#     VISIBLE:  '< > CheckBox cb7: normal checkbo', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'cb7: normal checkbox. check box not checked'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("cb7: normal checkbox.", acc_role=pyatspi.ROLE_CHECK_BOX))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
# BRAILLE LINE:  '< > CheckBox cb7: normal checkbox. disable Button enable Button set value to "fish" Button "onChange" handler updates: [false]'
#     VISIBLE:  '< > CheckBox cb7: normal checkbo', cursor=1
# SPEECH OUTPUT: 'cb7: normal checkbox. check box'
# SPEECH OUTPUT: 'not checked'
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
