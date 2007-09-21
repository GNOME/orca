#!/usr/bin/python

"""Test of Mozilla ARIA menu presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "Accessible DHTML" frame.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the Mozilla ARIA spreadsheet demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://www.mozilla.org/access/dhtml/spreadsheet"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Accessible DHTML", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Move to the menu
#
sequence.append(KeyComboAction("<Control><Alt>m"))
sequence.append(WaitForFocus("Edit", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("View", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Basic Grey", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("The Blues", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Garden", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("In the Pink", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Rose", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Left"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Hide", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Show", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("one", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("two", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Escape"))

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
