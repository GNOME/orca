#!/usr/bin/python

"""Test of menu radio button output using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Open the "View" menu then the Page Style menu. Focus should be on the
# "No Style" radio menu item.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>v"))
sequence.append(utils.AssertPresentationAction(
    "View menu",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ToolBar View Menu'",
     "     VISIBLE:  'View Menu', cursor=1",
     "BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ToolBar Application MenuBar Toolbars Menu'",
     "     VISIBLE:  'Toolbars Menu', cursor=1",
     "SPEECH OUTPUT: 'View menu'",
     "SPEECH OUTPUT: 'Toolbars menu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("y"))
sequence.append(utils.AssertPresentationAction(
    "y for Page Style menu",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ToolBar Application MenuBar Page Style Menu'",
     "     VISIBLE:  'Page Style Menu', cursor=1",
     "BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ToolBar Application MenuBar View Menu & y No Style RadioItem'",
     "     VISIBLE:  '& y No Style RadioItem', cursor=1",
     "SPEECH OUTPUT: 'Page Style menu'",
     "SPEECH OUTPUT: 'No Style not selected radio menu item'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ToolBar Application MenuBar View Menu & y No Style RadioItem'",
     "     VISIBLE:  '& y No Style RadioItem', cursor=1",
     "SPEECH OUTPUT: 'tool bar View menu Page Style menu No Style radio menu item not selected item 1 of 2'"]))

########################################################################
# Down Arrow to the "Basic Page Style" radio menu item.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Down Arrow in menu",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ToolBar Application MenuBar View Menu &=y Basic Page Style RadioItem'",
     "     VISIBLE:  '&=y Basic Page Style RadioItem', cursor=1",
     "SPEECH OUTPUT: 'Basic Page Style selected radio menu item'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ToolBar Application MenuBar View Menu &=y Basic Page Style RadioItem'",
     "     VISIBLE:  '&=y Basic Page Style RadioItem', cursor=1",
     "SPEECH OUTPUT: 'tool bar View menu Page Style menu Basic Page Style radio menu item selected item 2 of 2'"]))

########################################################################
# Dismiss the "Page Style" menu by pressing Escape.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("Page Style", acc_role=pyatspi.ROLE_MENU))

########################################################################
# Dismiss the menu by pressing Escape and wait for the location bar
# to regain focus.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
