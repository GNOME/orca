# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of where Am I output in a dialog box using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield", None))

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
 
sequence.append(WaitForWindowActivate("Page Setup", None))

########################################################################
# Read the title bar with Orca+KP_ENTER
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Title Bar", 
    ["BRAILLE LINE:  'Minefield Application Page Setup Dialog ScrollPane Format Panel Orientation: Panel &=y Portrait RadioButton'",
     "     VISIBLE:  '&=y Portrait RadioButton', cursor=1",
     "SPEECH OUTPUT: 'Page Setup'"]))

########################################################################
# Obtain the default button with Orca+KP_ENTER double clicked.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Default button", 
    ["BRAILLE LINE:  'Minefield Application Page Setup Dialog ScrollPane Format Panel Orientation: Panel &=y Portrait RadioButton'",
     "     VISIBLE:  '&=y Portrait RadioButton', cursor=1",
     "BRAILLE LINE:  'Minefield Application Page Setup Dialog ScrollPane Format Panel Orientation: Panel &=y Portrait RadioButton'",
     "     VISIBLE:  '&=y Portrait RadioButton', cursor=1",
     "SPEECH OUTPUT: 'Page Setup'",
     "SPEECH OUTPUT: 'Default button is OK'"]))

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
