#!/usr/bin/python

"""Test of page tab output using Firefox.
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
# In the Page Setup dialog, shift+tab once to move to the page tabs.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(utils.AssertPresentationAction(
    "Shift+Tab to page tabs",
    ["BRAILLE LINE:  'Minefield Application Page Setup Dialog Format & Options Page'",
     "     VISIBLE:  'Format & Options Page', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Format & Options page'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  'Minefield Application Page Setup Dialog Format & Options Page'",
     "     VISIBLE:  'Format & Options Page', cursor=1",
     "SPEECH OUTPUT: 'tab list'",
     "SPEECH OUTPUT: 'Format & Options page'",
     "SPEECH OUTPUT: 'item 1 of 2'",
     "SPEECH OUTPUT: ''"]))

########################################################################
# Right Arrow to move to the second page tab.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Right Arrow to second page tab",
    ["BRAILLE LINE:  'Minefield Application Page Setup Dialog Margins & Header/Footer Page'",
     "     VISIBLE:  'Margins & Header/Footer Page', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Margins & Header/Footer page'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  'Minefield Application Page Setup Dialog Margins & Header/Footer Page'",
     "     VISIBLE:  'Margins & Header/Footer Page', cursor=1",
     "SPEECH OUTPUT: 'tab list'",
     "SPEECH OUTPUT: 'Margins & Header/Footer page'",
     "SPEECH OUTPUT: 'item 2 of 2'",
     "SPEECH OUTPUT: ''"]))

########################################################################
# Left Arrow to move to the first page tab.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left Arrow to first page tab",
    ["BRAILLE LINE:  'Minefield Application Page Setup Dialog Format & Options Page'",
     "     VISIBLE:  'Format & Options Page', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Format & Options page'"]))

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
