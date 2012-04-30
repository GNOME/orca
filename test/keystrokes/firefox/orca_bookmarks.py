#!/usr/bin/python

"""Test of Orca bookmarks
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the frame.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the simpleform.html page.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction(utils.htmlURLPrefix + "simpleform.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Tab to the first entry.  The following will be presented.
#
# BRAILLE LINE:  'Type something here:   $l'
#      VISIBLE:  'Type something here:   $l', cursor=23
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Type something here: text '
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

########################################################################
# Set a bookmark at the entry.  The following will be presented.
#
# SPEECH OUTPUT: 'entered bookmark'
# SPEECH OUTPUT: 'Type something here: text '
#
sequence.append(KeyPressAction (0, None, "Alt_L"))
sequence.append(KeyPressAction (0, None, "Insert"))
sequence.append(TypeAction ("1"))
sequence.append(KeyReleaseAction(150, None, "Insert"))
sequence.append(KeyReleaseAction(150, None, "Alt_L"))

########################################################################
# Tab to the first checkbox.  Irrelevant output ignored.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PASSWORD_TEXT))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Red", acc_role=pyatspi.ROLE_CHECK_BOX))

########################################################################
# Set a bookmark at the checkbox.  The following will be presented.
#
# SPEECH OUTPUT: 'entered bookmark'
# SPEECH OUTPUT: 'Red check box not checked'
#
sequence.append(KeyPressAction (0, None, "Alt_L"))
sequence.append(KeyPressAction (0, None, "Insert"))
sequence.append(TypeAction ("2"))
sequence.append(KeyReleaseAction(150, None, "Insert"))
sequence.append(KeyReleaseAction(150, None, "Alt_L"))

########################################################################
# Go to bookmark number 1.  The following will be presented.
#
# BRAILLE LINE:  'Type something here:   $l'
#      VISIBLE:  'Type something here:   $l', cursor=23
# SPEECH OUTPUT: 'Type something here: text '
#
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("1"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
#sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

########################################################################
# Go to bookmark number 2.  The following will be presented.
# Note: some unicode characters have been removed from Braille output.
#
# BRAILLE LINE:  'Check one or more:   < > CheckBox Red < > CheckBox Blue < > CheckBox Green'
#      VISIBLE:  '? < > CheckBox Red < > CheckBox ', cursor=1
# SPEECH OUTPUT: 'Red check box not checked'
#
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("2"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
#sequence.append(WaitForFocus("Red", acc_role=pyatspi.ROLE_CHECK_BOX))

########################################################################
# Go to the next bookmark.  The following will be presented.
#
# BRAILLE LINE:  'Type something here:   $l'
#      VISIBLE:  'Type something here:   $l', cursor=23
# SPEECH OUTPUT: 'Type something here: text '
#
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("B"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
#sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

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
