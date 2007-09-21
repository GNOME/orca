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
# Tab to the first tab container.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Tab 2", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Tab 3", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Another Tab", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Sub TabContainer", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("SubTab 2", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(KeyComboAction("Left"))
sequence.append(WaitForFocus("SubTab 1", acc_role=pyatspi.ROLE_PAGE_TAB))

########################################################################
# Tab to the second tab container.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Tab 1", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Tab 2", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(KeyComboAction("Right"))

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
