#!/usr/bin/python

"""Test of UIUC tree presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "application/xhtml+xml: Tree Example 1" frame.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the UIUC button demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://test.cita.uiuc.edu/aria/tree/xhtml.php?title=Tree%20Example%201&ginc=includes/tree1a.inc&gcss=css/tree1a.css&gjs=../js/globals.js,../js/enable_app.js,js/tree1a.js"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("application/xhtml+xml: Tree Example 1", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Tab to the tree.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Fruits", acc_role=pyatspi.ROLE_LIST_ITEM))

########################################################################
# Navigate the tree
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Oranges", acc_role=pyatspi.ROLE_LIST_ITEM))

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Pineapples", acc_role=pyatspi.ROLE_LIST_ITEM))

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Apples", acc_role=pyatspi.ROLE_LIST_ITEM))

sequence.append(KeyComboAction("Right"))
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Macintosh", acc_role=pyatspi.ROLE_LIST_ITEM))

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Granny Smith", acc_role=pyatspi.ROLE_LIST_ITEM))

sequence.append(KeyComboAction("Right"))
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Washington State", acc_role=pyatspi.ROLE_LIST_ITEM))

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Michigan", acc_role=pyatspi.ROLE_LIST_ITEM))

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("New York", acc_role=pyatspi.ROLE_LIST_ITEM))

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Fuji", acc_role=pyatspi.ROLE_LIST_ITEM))

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Bananas", acc_role=pyatspi.ROLE_LIST_ITEM))

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Pears", acc_role=pyatspi.ROLE_LIST_ITEM))

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Vegetables", acc_role=pyatspi.ROLE_LIST_ITEM))

sequence.append(KeyComboAction("Left"))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
