#!/usr/bin/python

"""Test of push button output using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Open the "File" menu and press U for the Page Setup dialog
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(utils.AssertPresentationAction(
    "File menu",
    ["BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar File Menu'",
     "     VISIBLE:  'File Menu', cursor=1",
     "BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar New Window(Control N)'",
     "     VISIBLE:  'New Window(Control N)', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'File menu'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'New Window Control N'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("u"))
sequence.append(utils.AssertPresentationAction(
    "u for Page Setup",
    ["BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar AutoComplete Location  $l'",
     "     VISIBLE:  'Location  $l', cursor=10",
     "BRAILLE LINE:  'Page Setup Dialog Format for:  Combo'",
     "     VISIBLE:  ' Combo', cursor=1",
     "SPEECH OUTPUT: 'Location autocomplete'",
     "SPEECH OUTPUT: 'Location text '",
     "SPEECH OUTPUT: 'Format for: combo box'"]))

sequence.append(WaitForWindowActivate("Page Setup",None))

########################################################################
# Shift+tab again to move to the Apply push button. 
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(utils.AssertPresentationAction(
    "Shift Tab to the Apply button",
    ["BRAILLE LINE:  'Page Setup Dialog Apply Button'",
     "     VISIBLE:  'Page Setup Dialog Apply Button', cursor=19",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Apply button'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  'Page Setup Dialog Apply Button'",
     "     VISIBLE:  'Page Setup Dialog Apply Button', cursor=19",
     "SPEECH OUTPUT: 'Apply'",
     "SPEECH OUTPUT: 'button'",
     "SPEECH OUTPUT: 'Alt a'"]))

########################################################################
# Shift+tab again to move to the Cancel push button. 
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(utils.AssertPresentationAction(
    "Shift Tab to the Cancel button",
    ["BRAILLE LINE:  'Page Setup Dialog Cancel Button'",
     "     VISIBLE:  'Page Setup Dialog Cancel Button', cursor=19",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Cancel button'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  'Page Setup Dialog Cancel Button'",
     "     VISIBLE:  'Page Setup Dialog Cancel Button', cursor=19",
     "SPEECH OUTPUT: 'Cancel'",
     "SPEECH OUTPUT: 'button'",
     "SPEECH OUTPUT: 'Alt c'"]))

########################################################################
# Dismiss the dialog by pressing Space on the Cancel button and wait 
# for the location bar to regain focus.
#
sequence.append(TypeAction(" "))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
