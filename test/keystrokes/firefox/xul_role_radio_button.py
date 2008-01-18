#!/usr/bin/python

"""Test of radio button output using Firefox.
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

########################################################################
# Tab twice to get to the Portrait radio button.
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab",
    ["BRAILLE LINE:  'Page Setup Dialog Paper size:  Combo'",
     "     VISIBLE:  ' Combo', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Paper size: combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab",
    ["BRAILLE LINE:  'Page Setup Dialog &=y Orientation: Portrait RadioButton'",
     "     VISIBLE:  '&=y Orientation: Portrait RadioB', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Orientation:'",
     "SPEECH OUTPUT: 'Portrait selected radio button'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  'Page Setup Dialog &=y Orientation: Portrait RadioButton'",
     "     VISIBLE:  '&=y Orientation: Portrait RadioB', cursor=1",
     "SPEECH OUTPUT: 'Orientation:'",
     "SPEECH OUTPUT: 'Orientation: Portrait radio button'",
     "SPEECH OUTPUT: 'selected'",
     "SPEECH OUTPUT: 'item 1 of 4'",
     "SPEECH OUTPUT: 'Alt o'"]))

########################################################################
# Right Arrow to the "Reverse portrait" radio button. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Right Arrow to radio button",
    ["BRAILLE LINE:  'Page Setup Dialog & y Reverse portrait RadioButton'",
     "     VISIBLE:  '& y Reverse portrait RadioButton', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Reverse portrait not selected radio button'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  'Page Setup Dialog &=y Reverse portrait RadioButton'",
     "     VISIBLE:  '&=y Reverse portrait RadioButton', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Reverse portrait radio button'",
     "SPEECH OUTPUT: 'selected'",
     "SPEECH OUTPUT: 'item 2 of 4'",
     "SPEECH OUTPUT: ''"]))

########################################################################
# Dismiss the dialog by pressing Escape and wait for the location bar
# to regain focus.
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
