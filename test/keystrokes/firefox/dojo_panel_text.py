#!/usr/bin/python

"""Test of presentation of Dojo's panel text using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the Test Dialog demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction(utils.DojoNightlyURLPrefix + "test_Dialog.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

sequence.append(PauseAction(5000))

########################################################################
# Tab to the third button "Show TabContainer Dialog" and press it.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(WaitForFocus("First tab"))
sequence.append(utils.AssertPresentationAction(
    "Space to press the Show TabContainer Dialog", 
    ["BRAILLE LINE:  'First tab Page Image Second tab Page Image'",
     "     VISIBLE:  'First tab Page Image Second tab ', cursor=1",
     "SPEECH OUTPUT: 'TabContainer Dialog dialog First tab page'"]))

########################################################################
# Right Arrow to the Second tab page
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Right Arrow to the Second tab page", 
    ["BRAILLE LINE:  'First tab Page Image Second tab Page Image'",
     "     VISIBLE:  'Second tab Page Image', cursor=1",
     "SPEECH OUTPUT: 'Second tab page'"]))

########################################################################
# Tab to the panel.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab into the panel", 
    ["BUG? - Speech isn't getting the first line",
     "BRAILLE LINE:  'This is the second tab.'",
     "     VISIBLE:  'This is the second tab.', cursor=1",
     "SPEECH OUTPUT: 'panel'"]))

########################################################################
# Down Arrow from the page tab to the panel text.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Down Arrow", 
    ["BUG? - We're quiet here."]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down Arrow", 
    ["BRAILLE LINE:  'Make it overflow. ipsum dolor sit amet, consectetuer adipiscing elit.'",
     "     VISIBLE:  'Make it overflow. ipsum dolor si', cursor=1",
     "SPEECH OUTPUT: 'Make it overflow. ipsum dolor sit amet link , consectetuer adipiscing elit.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Down Arrow", 
    ["BRAILLE LINE:  'Aenean semper sagittis velit. Cras in mi. Duis porta mauris ut'",
     "     VISIBLE:  'Aenean semper sagittis velit. Cr', cursor=1",
     "SPEECH OUTPUT: 'Aenean semper sagittis velit. Cras in mi. Duis porta mauris ut'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Down Arrow", 
    ["BRAILLE LINE:  'ligula. Proin porta rutrum lacus. Etiam consequat scelerisque'",
     "     VISIBLE:  'ligula. Proin porta rutrum lacus', cursor=1",
     "SPEECH OUTPUT: 'ligula. Proin porta rutrum lacus. Etiam consequat scelerisque'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Down Arrow", 
    ["BRAILLE LINE:  'quam. Nulla facilisi. Maecenas luctus venenatis nulla. In sit amet'",
     "     VISIBLE:  'quam. Nulla facilisi. Maecenas l', cursor=1",
     "SPEECH OUTPUT: 'quam. Nulla facilisi. Maecenas luctus venenatis nulla. In sit amet'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Down Arrow", 
    ["BRAILLE LINE:  'dui non mi semper iaculis. Sed molestie tortor at ipsum. Morbi'",
     "     VISIBLE:  'dui non mi semper iaculis. Sed m', cursor=1",
     "SPEECH OUTPUT: 'dui non mi semper iaculis. Sed molestie tortor at ipsum. Morbi'"]))

########################################################################
# Up Arrow through the panel text back to the page tab.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "1. Up Arrow", 
    ["BRAILLE LINE:  'quam. Nulla facilisi. Maecenas luctus venenatis nulla. In sit amet'",
     "     VISIBLE:  'quam. Nulla facilisi. Maecenas l', cursor=1",
     "SPEECH OUTPUT: 'quam. Nulla facilisi. Maecenas luctus venenatis nulla. In sit amet'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "2. Up Arrow", 
    ["BRAILLE LINE:  'ligula. Proin porta rutrum lacus. Etiam consequat scelerisque'",
     "     VISIBLE:  'ligula. Proin porta rutrum lacus', cursor=1",
     "SPEECH OUTPUT: 'ligula. Proin porta rutrum lacus. Etiam consequat scelerisque'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "3. Up Arrow", 
    ["BRAILLE LINE:  'Aenean semper sagittis velit. Cras in mi. Duis porta mauris ut'",
     "     VISIBLE:  'Aenean semper sagittis velit. Cr', cursor=1",
     "SPEECH OUTPUT: 'Aenean semper sagittis velit. Cras in mi. Duis porta mauris ut'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Up Arrow", 
    ["BRAILLE LINE:  'Make it overflow. ipsum dolor sit amet, consectetuer adipiscing elit.'",
     "     VISIBLE:  'Make it overflow. ipsum dolor si', cursor=1",
     "SPEECH OUTPUT: 'Make it overflow. ipsum dolor sit amet link , consectetuer adipiscing elit.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "5. Up Arrow", 
    ["BRAILLE LINE:  'This is the second tab.'",
     "     VISIBLE:  'This is the second tab.', cursor=1",
     "SPEECH OUTPUT: 'This is the second tab.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Up Arrow", 
    ["BRAILLE LINE:  'First tab Page Image Second tab Page Image'",
     "     VISIBLE:  'First tab Page Image Second tab ', cursor=1",
     "SPEECH OUTPUT: 'First tab page Second tab page'"]))

########################################################################
# Escape to dismiss the dialog.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Escape"))
sequence.append(utils.AssertPresentationAction(
    "Escape to dismiss the dialog", 
    ["BRAILLE LINE:  'Show TabContainer Dialog Button'",
     "     VISIBLE:  'Show TabContainer Dialog Button', cursor=1",
     "SPEECH OUTPUT: 'Show TabContainer Dialog button'"]))

########################################################################
# Close the demo
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
