#!/usr/bin/python

"""Test of Mozilla ARIA slider presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "Graphical ARIA Slider" frame.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the Mozilla ARIA slider demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://www.mozilla.org/access/dhtml/pretty-slider.htm"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Graphical ARIA Slider", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Tab to the slider.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("My slider", acc_role=pyatspi.ROLE_SLIDER))


sequence.append(KeyComboAction("Right"))
sequence.append(KeyComboAction("Right"))
sequence.append(KeyComboAction("Right"))
sequence.append(KeyComboAction("Right"))
sequence.append(KeyComboAction("Left"))
sequence.append(KeyComboAction("Left"))
sequence.append(KeyComboAction("Left"))
sequence.append(KeyComboAction("Left"))
sequence.append(KeyComboAction("End"))
sequence.append(KeyComboAction("Home"))

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
