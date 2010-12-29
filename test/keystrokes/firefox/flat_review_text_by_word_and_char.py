# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of flat review by word and char in a simple text document."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the local blockquote test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "blockquotes.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Blockquote Regression Test",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

sequence.append(PauseAction(3000))

########################################################################
# Read the current word with KP_5 and the next word with KP_6.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5", 1000))
sequence.append(utils.AssertPresentationAction(
    "flat review current word", 
    ["BRAILLE LINE:  'On weaponry: $l'",
     "     VISIBLE:  'On weaponry: $l', cursor=1",
     "SPEECH OUTPUT: 'On'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6", 1000))
sequence.append(utils.AssertPresentationAction(
    "flat review current word", 
    ["BRAILLE LINE:  'On weaponry: $l'",
     "     VISIBLE:  'On weaponry: $l', cursor=4",
     "SPEECH OUTPUT: 'weaponry:'"]))

########################################################################
# Spell the current word with KP_5 2x.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "spell current word", 
    ["BRAILLE LINE:  'On weaponry: $l'",
     "     VISIBLE:  'On weaponry: $l', cursor=4",
     "BRAILLE LINE:  'On weaponry: $l'",
     "     VISIBLE:  'On weaponry: $l', cursor=4",
     "SPEECH OUTPUT: 'weaponry:'",
     "SPEECH OUTPUT: 'w'",
     "SPEECH OUTPUT: 'e'",
     "SPEECH OUTPUT: 'a'",
     "SPEECH OUTPUT: 'p'",
     "SPEECH OUTPUT: 'o'",
     "SPEECH OUTPUT: 'n'",
     "SPEECH OUTPUT: 'r'",
     "SPEECH OUTPUT: 'y'",
     "SPEECH OUTPUT: ':'"]))

########################################################################
# Spell the current word phonetically with KP_5 3x.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(KeyComboAction("KP_5"))
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "spell current word phonetically", 
    ["BRAILLE LINE:  'On weaponry: $l'",
     "     VISIBLE:  'On weaponry: $l', cursor=4",
     "BRAILLE LINE:  'On weaponry: $l'",
     "     VISIBLE:  'On weaponry: $l', cursor=4",
     "BRAILLE LINE:  'On weaponry: $l'",
     "     VISIBLE:  'On weaponry: $l', cursor=4",
     "SPEECH OUTPUT: 'weaponry:'",
     "SPEECH OUTPUT: 'w'",
     "SPEECH OUTPUT: 'e'",
     "SPEECH OUTPUT: 'a'",
     "SPEECH OUTPUT: 'p'",
     "SPEECH OUTPUT: 'o'",
     "SPEECH OUTPUT: 'n'",
     "SPEECH OUTPUT: 'r'",
     "SPEECH OUTPUT: 'y'",
     "SPEECH OUTPUT: ':'",
     "SPEECH OUTPUT: 'whiskey'",
     "SPEECH OUTPUT: 'echo'",
     "SPEECH OUTPUT: 'alpha'",
     "SPEECH OUTPUT: 'papa'",
     "SPEECH OUTPUT: 'oscar'",
     "SPEECH OUTPUT: 'november'",
     "SPEECH OUTPUT: 'romeo'",
     "SPEECH OUTPUT: 'yankee'",
     "SPEECH OUTPUT: ':'"]))

########################################################################
# Read forward word by word with KP_6.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "flat review next word", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=1",
     "SPEECH OUTPUT: 'NOBODY' voice=uppercase"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "flat review next word", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=8",
     "SPEECH OUTPUT: 'expects'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "flat review next word", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=16",
     "SPEECH OUTPUT: 'the'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "flat review next word", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=20",
     "SPEECH OUTPUT: 'Spanish'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "flat review next word", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=28",
     "SPEECH OUTPUT: 'Inquisition!'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "flat review next word", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and  $l'",
     "     VISIBLE:  'sition! Our chief weapon is surp', cursor=9",
     "SPEECH OUTPUT: 'Our'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "flat review next word", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and  $l'",
     "     VISIBLE:  'sition! Our chief weapon is surp', cursor=13",
     "SPEECH OUTPUT: 'chief'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "flat review next word", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and  $l'",
     "     VISIBLE:  'sition! Our chief weapon is surp', cursor=19",
     "SPEECH OUTPUT: 'weapon'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "flat review next word", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and  $l'",
     "     VISIBLE:  'sition! Our chief weapon is surp', cursor=26",
     "SPEECH OUTPUT: 'is'"]))

########################################################################
# Read the current char with KP_2.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_2"))
sequence.append(utils.AssertPresentationAction(
    "flat review current char", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and  $l'",
     "     VISIBLE:  'sition! Our chief weapon is surp', cursor=26",
     "SPEECH OUTPUT: 'i'"]))

########################################################################
# Read forward char by char with KP_3.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_3"))
sequence.append(utils.AssertPresentationAction(
    "flat review next char", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and  $l'",
     "     VISIBLE:  'sition! Our chief weapon is surp', cursor=27",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_3"))
sequence.append(utils.AssertPresentationAction(
    "flat review next char", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and  $l'",
     "     VISIBLE:  'sition! Our chief weapon is surp', cursor=28",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_3"))
sequence.append(utils.AssertPresentationAction(
    "flat review next char", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and  $l'",
     "     VISIBLE:  'sition! Our chief weapon is surp', cursor=29",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_3"))
sequence.append(utils.AssertPresentationAction(
    "flat review next char", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and  $l'",
     "     VISIBLE:  'sition! Our chief weapon is surp', cursor=30",
     "SPEECH OUTPUT: 'u'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_3"))
sequence.append(utils.AssertPresentationAction(
    "flat review next char", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and  $l'",
     "     VISIBLE:  'sition! Our chief weapon is surp', cursor=31",
     "SPEECH OUTPUT: 'r'"]))

########################################################################
# Read backwards char by char with KP_1.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_1"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous char", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and  $l'",
     "     VISIBLE:  'sition! Our chief weapon is surp', cursor=30",
     "SPEECH OUTPUT: 'u'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_1"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous char", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and  $l'",
     "     VISIBLE:  'sition! Our chief weapon is surp', cursor=29",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_1"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous char", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and  $l'",
     "     VISIBLE:  'sition! Our chief weapon is surp', cursor=28",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_1"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous char", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and  $l'",
     "     VISIBLE:  'sition! Our chief weapon is surp', cursor=27",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_1"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous char", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and  $l'",
     "     VISIBLE:  'sition! Our chief weapon is surp', cursor=26",
     "SPEECH OUTPUT: 'i'"]))

########################################################################
# Read backwards word by word with KP_4.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_4"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous word", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and  $l'",
     "     VISIBLE:  'sition! Our chief weapon is surp', cursor=19",
     "SPEECH OUTPUT: 'weapon'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_4"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous word", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and  $l'",
     "     VISIBLE:  'sition! Our chief weapon is surp', cursor=13",
     "SPEECH OUTPUT: 'chief'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_4"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous word", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and  $l'",
     "     VISIBLE:  'sition! Our chief weapon is surp', cursor=9",
     "SPEECH OUTPUT: 'Our'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_4"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous word", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=28",
     "SPEECH OUTPUT: 'Inquisition!'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_4"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous word", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=20",
     "SPEECH OUTPUT: 'Spanish'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_4"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous word", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=16",
     "SPEECH OUTPUT: 'the'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_4"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous word", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=8",
     "SPEECH OUTPUT: 'expects'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_4"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous word", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and  $l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=1",
     "SPEECH OUTPUT: 'NOBODY'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_4"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous word", 
    ["BRAILLE LINE:  'On weaponry: $l'",
     "     VISIBLE:  'On weaponry: $l', cursor=4",
     "SPEECH OUTPUT: 'weaponry:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_4"))
sequence.append(utils.AssertPresentationAction(
    "flat review previous word", 
    ["BRAILLE LINE:  'On weaponry: $l'",
     "     VISIBLE:  'On weaponry: $l', cursor=1",
     "SPEECH OUTPUT: 'On'"]))

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
