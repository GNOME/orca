# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of HTML list output of Firefox, in particular basic navigation
and where am I.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the local lists test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "lists.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Lists Test Page",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file", 
    ["BRAILLE LINE:  'Welcome to a List of Lists h1'",
     "     VISIBLE:  'Welcome to a List of Lists h1', cursor=1",
     "SPEECH OUTPUT: 'Welcome to a List of Lists heading  '",
     "SPEECH OUTPUT: 'level 1'"]))

########################################################################
# Press Down Arrow to move through the lists.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Lists are not only fun to make, they are fun to use. They help us:'",
     "     VISIBLE:  'Lists are not only fun to make, ', cursor=1",
     "SPEECH OUTPUT: 'Lists are not only fun to make, they are fun to use. They help us:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BUG? - For some reason in the harness, list numbers are all '0'. They are correct in actual use. I'm only marking this issue once.",
     "BRAILLE LINE:  '0. remember what the heck we are doing each day'",
     "     VISIBLE:  '0. remember what the heck we are', cursor=1",
     "SPEECH OUTPUT: '0. remember what the heck we are doing each day'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '0. arrange long and arbitrary lines of text into ordered lists that are pleasing to the eye and suggest some sense of priority, even if it is artificial'",
     "     VISIBLE:  '0. arrange long and arbitrary li', cursor=1",
     "SPEECH OUTPUT: '0. arrange long and arbitrary lines of text into ordered lists that are pleasing to the eye and suggest some sense of priority, even if it is artificial'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'sense of priority, even if it is artificial'",
     "     VISIBLE:  'sense of priority, even if it is', cursor=1",
     "SPEECH OUTPUT: 'sense of priority, even if it is artificial'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '0. look really cool when we carry them around on yellow Post-Itstm.'",
     "     VISIBLE:  '0. look really cool when we carr', cursor=1",
     "SPEECH OUTPUT: '0. look really cool when we carry them around on yellow Post-Itstm.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '0. and that other thing I keep forgetting.'",
     "     VISIBLE:  '0. and that other thing I keep f', cursor=1",
     "SPEECH OUTPUT: '0. and that other thing I keep forgetting.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Your ordered lists can start at a strange number, like:'",
     "     VISIBLE:  'Your ordered lists can start at ', cursor=1",
     "SPEECH OUTPUT: 'Your ordered lists can start at a strange number, like:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '0. And use roman numerals,'",
     "     VISIBLE:  '0. And use roman numerals,', cursor=1",
     "SPEECH OUTPUT: '0. And use roman numerals,'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '0. You might try using letters as well,'",
     "     VISIBLE:  '0. You might try using letters a', cursor=1",
     "SPEECH OUTPUT: '0. You might try using letters as well,'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '0. Maybe you prefer Big Letters,'",
     "     VISIBLE:  '0. Maybe you prefer Big Letters,', cursor=1",
     "SPEECH OUTPUT: '0. Maybe you prefer Big Letters,'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '0. or small roman numerals'",
     "     VISIBLE:  '0. or small roman numerals', cursor=1",
     "SPEECH OUTPUT: '0. or small roman numerals'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '• But discs belong to unordered lists'",
     "     VISIBLE:  '• But discs belong to unordere', cursor=1",
     "SPEECH OUTPUT: '• But discs belong to unordered lists'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '0. Though you can set the value in a list item!'",
     "     VISIBLE:  '0. Though you can set the value ', cursor=1",
     "SPEECH OUTPUT: '0. Though you can set the value in a list item!'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Unordered list:'",
     "     VISIBLE:  'Unordered list:', cursor=1",
     "SPEECH OUTPUT: 'Unordered list:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  '0. Though you can set the value in a list item!'",
     "     VISIBLE:  '0. Though you can set the value ', cursor=1",
     "SPEECH OUTPUT: '0. Though you can set the value in a list item!'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  '• But discs belong to unordered lists'",
     "     VISIBLE:  '• But discs belong to unordere', cursor=1",
     "SPEECH OUTPUT: '• But discs belong to unordered lists'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  '• But discs belong to unordered lists'",
     "     VISIBLE:  '• But discs belong to unordere', cursor=1",
     "SPEECH OUTPUT: 'list item'",
     "SPEECH OUTPUT: '• But discs belong to unordered lists'",
     "SPEECH OUTPUT: 'item 5 of 6'"]))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
#
sequence.append(KeyComboAction("<Control>l", 1000))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
