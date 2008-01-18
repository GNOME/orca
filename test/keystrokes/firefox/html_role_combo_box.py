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
# Press Tab once to get to the Severity combo box.  This combo box
# has a proper label (the Severity link that precedes it).
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to Severity combo box", 
    ["BRAILLE LINE:  'Severity Link : Severity normal Combo'",
     "     VISIBLE:  'normal Combo', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Severity normal combo box'"]))

########################################################################
# Press Tab twice to get to the Priority combo box.  This combo box
# lacks a proper label. Label guess should guess "Priority" from the
# link that precedes it.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to Priority Link", 
    ["BRAILLE LINE:  'Priority Link : Normal Combo'",
     "     VISIBLE:  'Priority Link : Normal Combo', cursor=0",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Priority link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to Priority combo box", 
    ["BRAILLE LINE:  'Priority Link : Normal Combo'",
     "     VISIBLE:  'Priority Link : Normal Combo', cursor=17",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Priority: Normal combo box'"]))

########################################################################
# Press Tab once to get to the Resolution combo box.  This combo box
# lacks a proper label. Label guess should guess "Resolution" from the
# text above it. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to Resolution combo box", 
    ["BRAILLE LINE:  'FIXED Combo'",
     "     VISIBLE:  'FIXED Combo', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Resolution: FIXED combo box'"]))

########################################################################
# Press Down Arrow to change the selection to WONTFIX.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Change selection Down: WONTFIX",
    ["BRAILLE LINE:  'WONTFIX Combo'",
     "     VISIBLE:  'WONTFIX Combo', cursor=0",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'WONTFIX'"]))

########################################################################
# Press Down Arrow to change the selection to NOTABUG
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Change selection Down: NOTABUG", 
    ["BRAILLE LINE:  'NOTABUG Combo'",
     "     VISIBLE:  'NOTABUG Combo', cursor=0",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'NOTABUG'"]))

########################################################################
# Press Up Arrow to change the selection back to WONTFIX.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Change selection Up: WONTFIX",
    ["BRAILLE LINE:  'WONTFIX Combo'",
     "     VISIBLE:  'WONTFIX Combo', cursor=0",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'WONTFIX'"]))

########################################################################
# Press Up Arrow to change the selection back to FIXED.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Change selection Up: FIXED", 
    ["BRAILLE LINE:  'FIXED Combo'",
     "     VISIBLE:  'FIXED Combo', cursor=0",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'FIXED'"]))

########################################################################
# Press Alt Down Arrow to expand the combo box.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>Down"))
sequence.append(utils.AssertPresentationAction(
    "Alt Down to Expand",
    ["BRAILLE LINE:  'FIXED Combo'",
     "     VISIBLE:  'FIXED Combo', cursor=1",
     "BRAILLE LINE:  'FIXED'",
     "     VISIBLE:  'FIXED', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'FIXED combo box'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'FIXED'"]))

########################################################################
# Press Down Arrow to change the selection back to WONTFIX.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Change selection Down: WONTFIX",
    ["BRAILLE LINE:  'WONTFIX'",
     "     VISIBLE:  'WONTFIX', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'WONTFIX'"]))

########################################################################
# Press Return to collapse the combo box with WONTFIX selected.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "Return to collapse combo box",
    ["BUG? - It would be nice to handle this better", 
     "BRAILLE LINE:  'WONTFIX Combo'",
     "     VISIBLE:  'WONTFIX Combo', cursor=1",
     "SPEECH OUTPUT: 'Minefield application Combo Box Regression Test - Minefield frame Combo Box Regression Test panel'",
     "SPEECH OUTPUT: 'Resolution: WONTFIX combo box'"]))

########################################################################
# Press Tab once to get to the Version combo box.  This combo box
# lacks a proper label. Label guess should guess "Version" from the
# text in the table cell on the left.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab",
    ["BRAILLE LINE:  'Version 2.16 Combo'",
     "     VISIBLE:  'Version 2.16 Combo', cursor=9",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Version 2.16 combo box'"]))

########################################################################
# Press Left Arrow once to move off of this combo box and onto the
# 'n' at the end of "Version".
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left out of combo box", 
    ["BRAILLE LINE:  'Version 2.16 Combo'",
     "     VISIBLE:  'Version 2.16 Combo', cursor=0",
     "SPEECH OUTPUT: 'Version 2.16 combo box'"]))

########################################################################
# Press Down Arrow once to move to the next line which contains
# the text "Component" in a table cell.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down to Component",
    ["BRAILLE LINE:  'Component'",
     "     VISIBLE:  'Component', cursor=1",
     "SPEECH OUTPUT: 'Component'"]))

########################################################################
# Press Down Arrow again to move to the next line which contains
# a combo box.
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
# Press Down Arrow to change the selection to Braille.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Change selection Down: Braille", 
    ["BRAILLE LINE:  'Braille'",
     "     VISIBLE:  'Braille', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Braille'"]))

########################################################################
# Press Return to collapse the combo box with Braille selected.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "Return to collapse combo box",
    ["BRAILLE LINE:  'Braille Combo'",
     "     VISIBLE:  'Braille Combo', cursor=1",
     "SPEECH OUTPUT: 'Minefield application Combo Box Regression Test - Minefield frame Combo Box Regression Test panel'",
     "SPEECH OUTPUT: 'Component Braille combo box'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BUG? - We're not handling combo boxes in HTML very well in where am I", 
     "BRAILLE LINE:  'Braille Combo'",
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

sequence.start()
