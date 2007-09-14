#!/usr/bin/python

"""Test of Dojo slider presentation using Firefox.
"""

from macaroon.playback.keypress_mimic import *

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "Dojo Slider Widget Demo" frame.
#
sequence.append(WaitForWindowActivate("Minefield",None))
sequence.append(WaitForFocus("Dojo Slider Widget Demo", pyatspi.ROLE_DOCUMENT_FRAME))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_SLIDER))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("Disable previous slider", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_SLIDER))
sequence.append(KeyComboAction("Up"))

sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(KeyComboAction("Up"))

sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(KeyComboAction("Up"))

sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(KeyComboAction("Up"))

sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(KeyComboAction("Up"))

sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(KeyComboAction("Down"))

sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(KeyComboAction("Down"))

sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(KeyComboAction("Down"))

sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(KeyComboAction("Down"))

sequence.append(WaitAction("object:property-change:accessible-value",
                           None,
                           None,
                           pyatspi.ROLE_SLIDER,
                           5000))
sequence.append(KeyComboAction("Down"))

########################################################################
# Close the demo
#
sequence.append(KeyComboAction("<Control>w"))

# Just a little extra wait to let some events get through.
#
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_INVALID, timeout=3000))

sequence.start()
