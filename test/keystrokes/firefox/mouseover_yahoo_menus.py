# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of Yahoo's menus accessed via mouseover
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "inline: Tab Panel Example 1" frame.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the UIUC Tab Panel demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://developer.yahoo.com/yui/examples/menu/leftnavfrommarkupwithanim_source.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

sequence.append(PauseAction(5000))

########################################################################
# Navigate to the Communication menu (which is actually a link).
#
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Navigate to Communications",
    ["BRAILLE LINE:  'Communication'",
     "     VISIBLE:  'Communication', cursor=1",
     "SPEECH OUTPUT: 'Communication link'"]))

########################################################################
# Route the mouse pointer to Communication.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Divide"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Route the pointer to Communications",
    ["BUG? - This should also be brailled.",
     "SPEECH OUTPUT: 'New item has been added section'"]))

########################################################################
# Move focus into the new child.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Multiply"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Move focus inside Communications menu",
    ["BRAILLE LINE:  'Communication 360°'",
     "     VISIBLE:  'Communication 360°', cursor=15",
     "SPEECH OUTPUT: '360° link'"]))

########################################################################
# Navigate amongst the menu items.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to menu item",
    ["BRAILLE LINE:  'Alerts'",
     "     VISIBLE:  'Alerts', cursor=1",
     "SPEECH OUTPUT: 'Alerts link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Tab to menu item",
    ["BRAILLE LINE:  'Avatars'",
     "     VISIBLE:  'Avatars', cursor=1",
     "SPEECH OUTPUT: 'Avatars link'"]))

########################################################################
# Restore the mouse pointer to the previous location to close the
# Communications menu and land back on the Communications link.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Multiply"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Close the Communications menu",
    ["BRAILLE LINE:  'Communication 360°'",
     "     VISIBLE:  'Communication 360°', cursor=1",
     "SPEECH OUTPUT: 'Communication link'"]))

########################################################################
# Close the demo
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
