# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of find output of Firefox on the Orca wiki."""

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
# Get into the Find toolbar and type Orca.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>F"))
sequence.append(utils.AssertPresentationAction(
    "Get into the Find Toolbar", 
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Orca - GNOME Live! - " + utils.firefoxFrameNames + " Frame ScrollPane ToolBar Find:  \$l'",
     "     VISIBLE:  'Find:  $l', cursor=7",
     "BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Orca - GNOME Live! - " + utils.firefoxFrameNames + " Frame ScrollPane ToolBar Find:  \$l'",
     "     VISIBLE:  'Find:  $l', cursor=7",
     "SPEECH OUTPUT: 'Find: text'"]))

# We won't use an assert here because different builds of Firefox give
# different results.
#
sequence.append(TypeAction("orca"))

########################################################################
# Press Return to move from result to result.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "1. Return",
    ["SPEECH OUTPUT: 'Welcome to Orca! heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "2. Return",
    ["SPEECH OUTPUT: '1. Welcome to Orca! link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "3. Return",
    ["SPEECH OUTPUT: 'Orca is a free, open source, flexible, extensible, and powerful'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "4. Return",
    ["SPEECH OUTPUT: 'magnification, Orca helps provide access to applications and'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "5. Return",
    ["SPEECH OUTPUT: 'development of Orca has been led by the Accessibility Program link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "6. Return",
    ["SPEECH OUTPUT: 'Please join and participate on the Orca mailing list link  \( archives link \): it's a helpful, kind, and productive'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "7. Return",
    ["SPEECH OUTPUT: 'Darragh Ó Héiligh link  has created several audio guides for Orca. This is a fantastic contribution'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "8. Return",
    ["SPEECH OUTPUT: '• Review of Fedora 7 and the Orca screen reader for the Gnome graphical desktop link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "9. Return",
    ["SPEECH OUTPUT: '(• |)Guide to installing the latest versions of Firefox and Orca link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "10. Return",
    ["SPEECH OUTPUT: 'As of GNOME 2.16, Orca is a part of the GNOME platform. As a result, Orca is already provided by'"]))

########################################################################
# Press Escape to exit the Find toolbar and return to the page content.
#
# Depending on the version of Firefox, we sometimes behave as if the page
# has just finished loading. I'm not sure what triggers that, and it does
# not always occur. It also seems to be fixed in the latest Firefox trunk.
# Therefore, we'll accept either situation for the purpose of reproducible
# results and not use an assertion here.
# 
sequence.append(KeyComboAction("Escape"))

########################################################################
# Press Down Arrow to read the next line (verifying that the caret 
# position was correctly updated when the Find toolbar was closed).
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Down",
    ["BRAILLE LINE:  'default on a number of operating system distributions, including Open Solaris and Ubuntu.'",
     "     VISIBLE:  'default on a number of operating', cursor=1",
     "SPEECH OUTPUT: 'default on a number of operating system distributions, including Open Solaris link  and Ubuntu link .'"]))

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
