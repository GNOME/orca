#!/usr/bin/python

"""Test of HTML combo box output of Firefox, including label guess and
forcing a combo box that has been reached by caret browsing to expand
and gain focus.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the local combo box test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "combobox.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Combo Box Regression Test",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file", 
    ["BRAILLE LINE:  'Severity Link : Severity normal Combo'",
     "     VISIBLE:  'Severity Link : Severity normal ', cursor=1",
     "SPEECH OUTPUT: 'Severity link : Severity normal combo box'"]))

########################################################################
# Press Tab once to get to the Severity link. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to Severity combo box", 
    ["BRAILLE LINE:  'Severity Link : Severity normal Combo'",
     "     VISIBLE:  'Severity Link : Severity normal ', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Severity link'"]))

########################################################################
# Press Tab once to get to the Severity combo box.  This combo box
# has a proper label (the Severity link that precedes it).
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(utils.AssertPresentationAction(
    "Tab to Severity combo box", 
    ["BRAILLE LINE:  'Severity Link : Severity normal Combo'",
     "     VISIBLE:  'normal Combo', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Severity normal combo box'"]))

########################################################################
# Press Tab twice to get to the Priority combo box.  This combo box
# lacks a proper label. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to Priority Link", 
    ["BRAILLE LINE:  'Priority Link : Normal Combo'",
     "     VISIBLE:  'Priority Link : Normal Combo', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Priority link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(utils.AssertPresentationAction(
    "Tab to Priority combo box", 
    ["BRAILLE LINE:  'Priority Link : Normal Combo'",
     "     VISIBLE:  'Priority Link : Normal Combo', cursor=17",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Normal combo box'"]))

########################################################################
# Press Down Arrow to change the selection to Low.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Change selection Down: Low",
    ["BUG? - We're picking up the previous menu item in the braille context",
     "BRAILLE LINE:  'Normal Combo Low'",
     "     VISIBLE:  'Normal Combo Low', cursor=14",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Low'"]))

########################################################################
# Press Up Arrow to change the selection back to Normal.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Change selection Up: Normal",
    ["BUG? - We're picking up the previous menu item in the braille context",
     "BRAILLE LINE:  'High Combo Normal'",
     "     VISIBLE:  'High Combo Normal', cursor=12",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Normal'"]))

########################################################################
# Press Alt Down Arrow to expand the combo box.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>Down"))
sequence.append(utils.AssertPresentationAction(
    "Alt Down to Expand",
    ["BRAILLE LINE:  'Priority Link : Normal Combo'",
     "     VISIBLE:  'Priority Link : Normal Combo', cursor=17",
     "BRAILLE LINE:  'Normal'",
     "     VISIBLE:  'Normal', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Normal combo box'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Normal'"]))

########################################################################
# Press Down Arrow to change the selection back to Low.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Change selection Down: Low",
    ["BRAILLE LINE:  'Low'",
     "     VISIBLE:  'Low', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Low'"]))

########################################################################
# Press Return to collapse the combo box with Low selected.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "Return to collapse combo box",
    ["BRAILLE LINE:  'Priority Link : Low Combo'",
     "     VISIBLE:  'Priority Link : Low Combo', cursor=17",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Low combo box'"]))

########################################################################
# Press Tab once to get to the Resolution combo box.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(utils.AssertPresentationAction(
    "Tab",
    ["BRAILLE LINE:  'FIXED Combo'",
     "     VISIBLE:  'FIXED Combo', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Resolution: FIXED combo box'"]))

########################################################################
# Press Left Arrow once to move off of this combo box.
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left out of combo box", 
    ["BRAILLE LINE:  'FIXED Combo'",
     "     VISIBLE:  'FIXED Combo', cursor=0",
     "SPEECH OUTPUT: 'Resolution: FIXED combo box'"]))

########################################################################
# Press Down Arrow once to move to the next line.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Version 2.16 Combo'",
     "     VISIBLE:  'Version 2.16 Combo', cursor=1",
     "SPEECH OUTPUT: 'Version 2.16 combo box'"]))

########################################################################
# Press Down Arrow again to move to the next line which contains the
# word Component.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Component'",
     "     VISIBLE:  'Component', cursor=1",
     "SPEECH OUTPUT: 'Component'"]))

########################################################################
# Press Down Arrow again to move to the next line which contains a
# combo box.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Speech Combo'",
     "     VISIBLE:  'Speech Combo', cursor=0",
     "SPEECH OUTPUT: 'Speech combo box'"]))

########################################################################
# Press Alt Down Arrow once to grab focus on this technically unfocused
# combo box and force it to expand.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>Down"))
sequence.append(utils.AssertPresentationAction(
    "Alt Down to Expand", 
    ["BRAILLE LINE:  'Speech Combo'",
     "     VISIBLE:  'Speech Combo', cursor=1",
     "BRAILLE LINE:  'Speech'",
     "     VISIBLE:  'Speech', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Speech combo box'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Speech'"]))

########################################################################
# Press Down Arrow to change the selection.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Change selection Down", 
    ["BRAILLE LINE:  'Braille'",
     "     VISIBLE:  'Braille', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Braille'"]))

########################################################################
# Press Return to collapse the combo box.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "Return to collapse combo box",
    ["BRAILLE LINE:  'Braille Combo'",
     "     VISIBLE:  'Braille Combo', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Component Braille combo box'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  'Braille Combo'",
     "     VISIBLE:  'Braille Combo', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'combo box'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: ''"]))

########################################################################
# Press Shift Tab once to return to the Version combo box.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(utils.AssertPresentationAction(
    "Shift Tab to Version", 
    ["BRAILLE LINE:  'Version 2.16 Combo'",
     "     VISIBLE:  'Version 2.16 Combo', cursor=9",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Version 2.16 combo box'"]))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
