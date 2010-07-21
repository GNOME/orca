# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of navigation by same-page links on the Orca wiki."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the local "wiki" test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "orca-wiki.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

sequence.append(WaitForFocus("Orca - GNOME Live!",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

sequence.append(PauseAction(6000))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file", 
    ["BRAILLE LINE:  'Home News Projects Art Support Development Community'",
     "     VISIBLE:  'Home News Projects Art Support D', cursor=1",
     "SPEECH OUTPUT: 'Home link News link Projects link Art link Support link Development link Community link'"]))

########################################################################
# Tab to the About link. Depending on timing, we get extra garbage here.
# This assertion isn't even necessary as we actually care about what
# comes after we press Return.
#
for i in range(24):
    sequence.append(KeyComboAction("Tab", 1000))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(5000))

sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("About", acc_role=pyatspi.ROLE_LINK))
sequence.append(PauseAction(2000))

########################################################################
# Press Return to active the link
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "Return",
    ["BRAILLE LINE:  'About h1'",
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
    ["BRAILLE LINE:  'Orca is a free, open source, flexible, extensible, and powerful'",
     "     VISIBLE:  'Orca is a free, open source, fle', cursor=1",
     "SPEECH OUTPUT: 'Orca is a free, open source, flexible, extensible, and powerful'"]))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
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
