#!/usr/bin/python

"""Test of UIUC tab panel presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Give focus to a widget in the first Tab",
    ["BRAILLE LINE:  '&=y Thick and cheesy radio button Thick and cheesy'",
     "     VISIBLE:  '&=y Thick and cheesy radio butto', cursor=1",
     "BRAILLE LINE:  '&=y Thick and cheesy radio button Thick and cheesy'",
     "     VISIBLE:  '&=y Thick and cheesy radio butto', cursor=1",
     "SPEECH OUTPUT: 'Thick and cheesy selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Ctrl Page Down to second tab",
    ["KNOWN ISSUE: Missing a space",
     "BRAILLE LINE:  'Crust VeggiesCarnivore Delivery'",
     "     VISIBLE:  'Crust VeggiesCarnivore Delivery', cursor=7",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "BRAILLE LINE:  'Veggies page tab'",
     "     VISIBLE:  'Veggies page tab', cursor=1",
     "SPEECH OUTPUT: 'Veggies page tab'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Right arrow to third tab",
    ["BRAILLE LINE:  'Carnivore page tab'",
     "     VISIBLE:  'Carnivore page tab', cursor=1",
     "BRAILLE LINE:  'Carnivore page tab'",
     "     VISIBLE:  'Carnivore page tab', cursor=1",
     "SPEECH OUTPUT: 'Carnivore page tab'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "4. basic whereAmI",
    ["BRAILLE LINE:  'Carnivore page tab'",
     "     VISIBLE:  'Carnivore page tab', cursor=1",
     "SPEECH OUTPUT: 'page tab list'",
     "SPEECH OUTPUT: 'Carnivore'",
     "SPEECH OUTPUT: 'page tab 3 of 4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "5. Right arrow to fourth tab",
    ["BRAILLE LINE:  'Delivery page tab'",
     "     VISIBLE:  'Delivery page tab', cursor=1",
     "BRAILLE LINE:  'Delivery page tab'",
     "     VISIBLE:  'Delivery page tab', cursor=1",
     "SPEECH OUTPUT: 'Delivery page tab'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "6. Left arrow back to third tab",
    ["BRAILLE LINE:  'Carnivore page tab'",
     "     VISIBLE:  'Carnivore page tab', cursor=1",
     "BRAILLE LINE:  'Carnivore page tab'",
     "     VISIBLE:  'Carnivore page tab', cursor=1",
     "SPEECH OUTPUT: 'Carnivore page tab'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "7. Press Tab to move into the third page",
    ["BRAILLE LINE:  '< > Pepperoni Pepperoni check box'",
     "     VISIBLE:  '< > Pepperoni Pepperoni check bo', cursor=1",
     "BRAILLE LINE:  'Browse mode'",
     "     VISIBLE:  'Browse mode', cursor=0",
     "BRAILLE LINE:  '< > Pepperoni Pepperoni check box Pepperoni'",
     "     VISIBLE:  '< > Pepperoni Pepperoni check bo', cursor=1",
     "SPEECH OUTPUT: 'Pepperoni check box not checked'",
     "SPEECH OUTPUT: 'Browse mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "8. Toggle the focused checkbox",
    ["BRAILLE LINE:  '<x> Pepperoni Pepperoni check box Pepperoni'",
     "     VISIBLE:  '<x> Pepperoni Pepperoni check bo', cursor=1",
     "SPEECH OUTPUT: 'checked'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
