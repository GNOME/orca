# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of line navigation output of Firefox. 
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the local "simple form" test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "steaks.html"))
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
    ["BRAILLE LINE:  'Holiday Gift Giving'",
     "     VISIBLE:  'Holiday Gift Giving', cursor=0",
     "SPEECH OUTPUT: 'Holiday Gift Giving'"]))

########################################################################
# Down Arrow.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Line Down",
    ["BRAILLE LINE:  'Shop Early - Deliver Later'",
     "     VISIBLE:  'Shop Early - Deliver Later', cursor=1",
     "SPEECH OUTPUT: 'Shop Early - Deliver Later",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'The Ideal Gift Collection Link'",
     "     VISIBLE:  'The Ideal Gift Collection Link', cursor=1",
     "SPEECH OUTPUT: 'The Ideal Gift Collection link ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  '  2 (5 oz.) Filet Mignons'",
     "     VISIBLE:  '  2 (5 oz.) Filet Mignons', cursor=1",
     "SPEECH OUTPUT: '  2 (5 oz.) Filet Mignons",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  '  2 (5 oz.) Top Sirloins'",
     "     VISIBLE:  '  2 (5 oz.) Top Sirloins', cursor=2",
     "SPEECH OUTPUT: '  2 (5 oz.) Top Sirloins",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down",
    ["BRAILLE LINE:  '  4 (4 oz.) Foobar Steaks Burgers'",
     "     VISIBLE:  '  4 (4 oz.) Foobar Steaks Burger', cursor=2",
     "SPEECH OUTPUT: '  4 (4 oz.) Foobar Steaks Burgers",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["BRAILLE LINE:  '  6 (5.75 oz.) Stuffed Baked Potatoes'",
     "     VISIBLE:  '  6 (5.75 oz.) Stuffed Baked Pot', cursor=2",
     "SPEECH OUTPUT: '  6 (5.75 oz.) Stuffed Baked Potatoes",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Down",
    ["BRAILLE LINE:  '  2 (4.5 oz.) Stuffed Sole with Scallops and Crab'",
     "     VISIBLE:  '  2 (4.5 oz.) Stuffed Sole with ', cursor=2",
     "SPEECH OUTPUT: '  2 (4.5 oz.) Stuffed Sole with Scallops and Crab",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Down",
    ["BRAILLE LINE:  '  1 (6 in.) Chocolate Lover's Cake'",
     "     VISIBLE:  '  1 (6 in.) Chocolate Lover's Ca', cursor=2",
     "SPEECH OUTPUT: '  1 (6 in.) Chocolate Lover's Cake",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Down",
    ["BRAILLE LINE:  'Regular $133.00, Now $59.99'",
     "     VISIBLE:  'Regular $133.00, Now $59.99', cursor=2",
     "SPEECH OUTPUT: 'Regular $133.00, Now $59.99",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Down",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Down",
    [""]))

########################################################################
# Up Arrow.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "1. Line Up",
    ["BRAILLE LINE:  'Regular $133.00, Now $59.99'",
     "     VISIBLE:  'Regular $133.00, Now $59.99', cursor=1",
     "SPEECH OUTPUT: 'Regular $133.00, Now $59.99",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Up",
    ["BRAILLE LINE:  '  1 (6 in.) Chocolate Lover's Cake'",
     "     VISIBLE:  '  1 (6 in.) Chocolate Lover's Ca', cursor=1",
     "SPEECH OUTPUT: '  1 (6 in.) Chocolate Lover's Cake",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Up",
    ["BRAILLE LINE:  '  2 (4.5 oz.) Stuffed Sole with Scallops and Crab'",
     "     VISIBLE:  '  2 (4.5 oz.) Stuffed Sole with ', cursor=1",
     "SPEECH OUTPUT: '  2 (4.5 oz.) Stuffed Sole with Scallops and Crab",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Up",
    ["BRAILLE LINE:  '  6 (5.75 oz.) Stuffed Baked Potatoes'",
     "     VISIBLE:  '  6 (5.75 oz.) Stuffed Baked Pot', cursor=1",
     "SPEECH OUTPUT: '  6 (5.75 oz.) Stuffed Baked Potatoes",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Up",
    ["BRAILLE LINE:  '  4 (4 oz.) Foobar Steaks Burgers'",
     "     VISIBLE:  '  4 (4 oz.) Foobar Steaks Burger', cursor=1",
     "SPEECH OUTPUT: '  4 (4 oz.) Foobar Steaks Burgers",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Up",
    ["BRAILLE LINE:  '  2 (5 oz.) Top Sirloins'",
     "     VISIBLE:  '  2 (5 oz.) Top Sirloins', cursor=1",
     "SPEECH OUTPUT: '  2 (5 oz.) Top Sirloins",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Up",
    ["BRAILLE LINE:  '  2 (5 oz.) Filet Mignons'",
     "     VISIBLE:  '  2 (5 oz.) Filet Mignons', cursor=1",
     "SPEECH OUTPUT: '  2 (5 oz.) Filet Mignons",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Up",
    ["BRAILLE LINE:  'The Ideal Gift Collection Link'",
     "     VISIBLE:  'The Ideal Gift Collection Link', cursor=1",
     "SPEECH OUTPUT: 'The Ideal Gift Collection link ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Up",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Up",
    ["BRAILLE LINE:  'Shop Early - Deliver Later'",
     "     VISIBLE:  'Shop Early - Deliver Later', cursor=1",
     "SPEECH OUTPUT: 'Shop Early - Deliver Later",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Up",
    ["BRAILLE LINE:  'Holiday Gift Giving'",
     "     VISIBLE:  'Holiday Gift Giving', cursor=1",
     "SPEECH OUTPUT: 'Holiday Gift Giving'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Up",
    [""]))

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

sequence.append(utils.AssertionSummaryAction())

sequence.start()
