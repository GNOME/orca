#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Give focus to a widget in the first Tab",
    ["BRAILLE LINE:  '&=y Thick and cheesy radio button'",
     "     VISIBLE:  '&=y Thick and cheesy radio butto', cursor=1",
     "BRAILLE LINE:  'Browse mode'",
     "     VISIBLE:  'Browse mode', cursor=0",
     "SPEECH OUTPUT: 'List with 4 items.'",
     "SPEECH OUTPUT: 'Thick and cheesy.'",
     "SPEECH OUTPUT: 'selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Ctrl Page Down to second tab",
    ["BRAILLE LINE:  '&=y Thick and cheesy radio button'",
     "     VISIBLE:  '&=y Thick and cheesy radio butto', cursor=1",
     "BRAILLE LINE:  'Veggies page tab'",
     "     VISIBLE:  'Veggies page tab', cursor=1",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "SPEECH OUTPUT: 'Veggies page tab.'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Right arrow to third tab",
    ["BRAILLE LINE:  'Veggies page tab'",
     "     VISIBLE:  'Veggies page tab', cursor=1",
     "BRAILLE LINE:  'Carnivore page tab'",
     "     VISIBLE:  'Carnivore page tab', cursor=1",
     "SPEECH OUTPUT: 'Carnivore page tab.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "4. basic whereAmI",
    ["BRAILLE LINE:  'Carnivore page tab'",
     "     VISIBLE:  'Carnivore page tab', cursor=1",
     "SPEECH OUTPUT: 'page tab list.'",
     "SPEECH OUTPUT: 'Carnivore page tab.'",
     "SPEECH OUTPUT: '3 of 4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "5. Right arrow to fourth tab",
    ["BRAILLE LINE:  'Delivery page tab'",
     "     VISIBLE:  'Delivery page tab', cursor=1",
     "SPEECH OUTPUT: 'Delivery page tab.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "6. Left arrow back to third tab",
    ["BRAILLE LINE:  'Carnivore page tab'",
     "     VISIBLE:  'Carnivore page tab', cursor=1",
     "SPEECH OUTPUT: 'Carnivore page tab.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "7. Press Tab to move into the third page",
    ["BRAILLE LINE:  '< > Pepperoni check box'",
     "     VISIBLE:  '< > Pepperoni check box', cursor=1",
     "BRAILLE LINE:  'Browse mode'",
     "     VISIBLE:  'Browse mode', cursor=0",
     "SPEECH OUTPUT: 'List with 4 items'",
     "SPEECH OUTPUT: 'Pepperoni check box not checked.'",
     "SPEECH OUTPUT: 'Browse mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "8. Toggle the focused checkbox",
    ["BRAILLE LINE:  '< > Pepperoni check box'",
     "     VISIBLE:  '< > Pepperoni check box', cursor=1",
     "BRAILLE LINE:  '<x> Pepperoni check box'",
     "     VISIBLE:  '<x> Pepperoni check box', cursor=1",
     "SPEECH OUTPUT: 'checked'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
