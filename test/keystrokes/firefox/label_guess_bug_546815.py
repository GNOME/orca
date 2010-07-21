# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of label guess functionality, primarily by line."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "bug-546815.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

sequence.append(WaitForFocus("",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file",
    ["BRAILLE LINE:  'Separator'",
     "     VISIBLE:  'Separator', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

########################################################################
# Press Insert+Tab to move from form field to form field.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Enter your Name:  $l text field using default type=text'",
     "     VISIBLE:  ' $l text field using default typ', cursor=1",
     "SPEECH OUTPUT: 'Enter your Name: text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '1. Enter your Address:  $l text field using SIZE and MAXLENGTH'",
     "     VISIBLE:  ' $l text field using SIZE and MA', cursor=1",
     "SPEECH OUTPUT: '1. Enter your Address: text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field",
    ["BRAILLE LINE:  '2. Enter your City:  $l 3. Enter your State:  $l 4. Enter your Country: US $l Image text field using value'",
     "     VISIBLE:  ' $l 3. Enter your State:  $l 4. ', cursor=1",
     "SPEECH OUTPUT: '2. Enter your City: text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '2. Enter your City:  $l 3. Enter your State:  $l 4. Enter your Country: US $l Image text field using value'",
     "     VISIBLE:  ' $l 4. Enter your Country: US $l', cursor=1",
     "SPEECH OUTPUT: '3. Enter your State: text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '2. Enter your City:  $l 3. Enter your State:  $l 4. Enter your Country: US $l text field using value'",
     "     VISIBLE:  'US $l text field using value', cursor=1",
     "SPEECH OUTPUT: '4. Enter your Country: text'",
     "SPEECH OUTPUT: 'US' voice=uppercase"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '5. Enter your Zip:  $l'",
     "     VISIBLE:  '5. Enter your Zip:  $l', cursor=20",
     "SPEECH OUTPUT: '5. Enter your Zip: text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field",
    ["BRAILLE LINE:  '6. What happens when a fixed-width font(the default) is used for a one-byte text input area, let's try it.. Enter one character:  $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: '6. What happens when a fixed-width font(the default) is used for a one-byte text input area, let's try it.. Enter one character: text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '< > CheckBox bird'",
     "     VISIBLE:  '< > CheckBox bird', cursor=1",
     "SPEECH OUTPUT: 'bird check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '< > CheckBox fish'",
     "     VISIBLE:  '< > CheckBox fish', cursor=1",
     "SPEECH OUTPUT: 'fish check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '< > CheckBox wild animal'",
     "     VISIBLE:  '< > CheckBox wild animal', cursor=1",
     "SPEECH OUTPUT: 'wild animal check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '&=y RadioButton cabernet sauvignon'",
     "     VISIBLE:  '&=y RadioButton cabernet sauvign', cursor=1",
     "SPEECH OUTPUT: 'cabernet sauvignon selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '& y RadioButton merlot'",
     "     VISIBLE:  '& y RadioButton merlot', cursor=1",
     "SPEECH OUTPUT: 'merlot not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '& y RadioButton nebbiolo'",
     "     VISIBLE:  '& y RadioButton nebbiolo', cursor=1",
     "SPEECH OUTPUT: 'nebbiolo not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '& y RadioButton pinot noir'",
     "     VISIBLE:  '& y RadioButton pinot noir', cursor=1",
     "SPEECH OUTPUT: 'pinot noir not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  '& y RadioButton don't drink wine'",
     "     VISIBLE:  '& y RadioButton don't drink wine', cursor=1",
     "SPEECH OUTPUT: 'don't drink wine not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Next form field", 
    ["BRAILLE LINE:  'Wrapping to top.'",
     "     VISIBLE:  'Wrapping to top.', cursor=0",
     "BRAILLE LINE:  'Enter your Name:  $l text field using default type=text'",
     "     VISIBLE:  ' $l text field using default typ', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to top.'",
     "SPEECH OUTPUT: 'Enter your Name: text'"]))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
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
