#!/usr/bin/python

"""Test of checkbox output using Firefox.
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
     "BRAILLE LINE:  'Minefield Application Page Setup Dialog'",
     "     VISIBLE:  'Page Setup Dialog', cursor=1",
     "BRAILLE LINE:  'Minefield Application Page Setup Dialog ScrollPane Format Panel Orientation: Panel &=y Portrait RadioButton'",
     "     VISIBLE:  '&=y Portrait RadioButton', cursor=1",
     "SPEECH OUTPUT: 'Location autocomplete'",
     "SPEECH OUTPUT: 'Location text '",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Page Setup %'",
     "SPEECH OUTPUT: 'Format panel Orientation: panel'",
     "SPEECH OUTPUT: 'Portrait selected radio button'"]))
 
sequence.append(WaitForWindowActivate("Page Setup",None))

########################################################################
# In the Page Setup dialog, tab to the first check box. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to checkbox",
    ["BRAILLE LINE:  'Minefield Application Page Setup Dialog ScrollPane Format Panel <x> Shrink To Fit Page Width CheckBox'",
     "     VISIBLE:  '<x> Shrink To Fit Page Width Che', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Shrink To Fit Page Width check box checked'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  'Minefield Application Page Setup Dialog ScrollPane Format Panel <x> Shrink To Fit Page Width CheckBox'",
     "     VISIBLE:  '<x> Shrink To Fit Page Width Che', cursor=1",
     "SPEECH OUTPUT: 'Shrink To Fit Page Width check box checked'",
     "SPEECH OUTPUT: ''"]))

########################################################################
# Toggle the state of the check box by pressing Space. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  'Minefield Application Page Setup Dialog ScrollPane Format Panel < > Shrink To Fit Page Width CheckBox'",
     "     VISIBLE:  '< > Shrink To Fit Page Width Che', cursor=1",
     "SPEECH OUTPUT: 'not checked'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  'Minefield Application Page Setup Dialog ScrollPane Format Panel < > Shrink To Fit Page Width CheckBox'",
     "     VISIBLE:  '< > Shrink To Fit Page Width Che', cursor=1",
     "SPEECH OUTPUT: 'Shrink To Fit Page Width check box not checked'",
     "SPEECH OUTPUT: ''"]))

########################################################################
# Toggle the state of the check box by pressing Space. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  'Minefield Application Page Setup Dialog ScrollPane Format Panel <x> Shrink To Fit Page Width CheckBox'",
     "     VISIBLE:  '<x> Shrink To Fit Page Width Che', cursor=1",
     "SPEECH OUTPUT: 'checked'"]))

########################################################################
# Dismiss the dialog by pressing Escape and wait for the location bar
# to regain focus.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
