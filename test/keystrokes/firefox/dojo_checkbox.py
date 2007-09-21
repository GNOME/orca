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
# Tab to the first checkbox and uncheck it.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("cb0: Vanilla (non-dojo) checkbox (for comparison purposes)", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(TypeAction(" "))

########################################################################
# Tab to the second checkbox and uncheck it.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("cb1: normal checkbox, with value=foo", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(TypeAction("  "))

########################################################################
# Tab to the second checkbox and uncheck it.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("cb2: normal checkbox, initially turned on.", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("cb5: Vanilla (non-dojo) checkbox (for comparison purposes)", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("cb6: instantiated from script", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("cb7: normal checkbox.", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("disable", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("enable", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus('set value to "fish"', acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("talk", acc_role=pyatspi.ROLE_RADIO_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("top 40", acc_role=pyatspi.ROLE_RADIO_BUTTON))
sequence.append(TypeAction(" "))

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
