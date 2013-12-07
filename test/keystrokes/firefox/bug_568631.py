#!/usr/bin/python

"""Test of navigation by same-page links on the Orca wiki."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# Load the local "wiki" test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(TypeAction(utils.htmlURLPrefix + "orca-wiki.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Orca - GNOME Live!", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))
sequence.append(PauseAction(6000))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file", 
    ["BRAILLE LINE:  'Home list item'",
     "     VISIBLE:  'Home list item', cursor=0",
     "SPEECH OUTPUT: 'Home'"]))

########################################################################
# Tab to the About link. Depending on timing, we get extra garbage here.
# This assertion isn't even necessary as we actually care about what
# comes after we press Return.
#
for i in range(24):
    sequence.append(KeyComboAction("Tab", 1000))

sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("Tab"))

########################################################################
# Press Return to active the link
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "Return",
    ["KNOWN ISSUE: We are moving to this location but not presenting it.",
     "BRAILLE LINE:  'About h1'",
     "     VISIBLE:  'About h1', cursor=1",
     "SPEECH OUTPUT: 'About heading level 1'"]))

########################################################################
# Press Down Arrow to read the next line (verifying that the caret
# position was correctly updated).
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Orca is a free, open source, flexible, extensible, and'",
     "     VISIBLE:  'Orca is a free, open source, fle', cursor=1",
     "SPEECH OUTPUT: 'Orca is a free, open source, flexible, extensible, and '"]))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertionSummaryAction())
sequence.start()
