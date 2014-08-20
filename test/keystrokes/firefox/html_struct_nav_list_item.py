#!/usr/bin/python

"""Test of structural navigation amongst list items."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("l"))
sequence.append(utils.AssertPresentationAction(
    "1. l to first list",
    ["BRAILLE LINE:  'List with 4 items'",
     "     VISIBLE:  'List with 4 items', cursor=0",
     "BRAILLE LINE:  '1.remember what the heck we are doing each day'",
     "     VISIBLE:  '1.remember what the heck we are ', cursor=1",
     "SPEECH OUTPUT: 'List with 4 items' voice=system",
     "SPEECH OUTPUT: '1.remember what the heck we are doing each day'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("l"))
sequence.append(utils.AssertPresentationAction(
    "2. l to second list",
    ["BRAILLE LINE:  'List with 6 items'",
     "     VISIBLE:  'List with 6 items', cursor=0",
     "BRAILLE LINE:  'VI.And use roman numerals,'",
     "     VISIBLE:  'VI.And use roman numerals,', cursor=1",
     "SPEECH OUTPUT: 'List with 6 items' voice=system",
     "SPEECH OUTPUT: 'VI.And use roman numerals,'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("l"))
sequence.append(utils.AssertPresentationAction(
    "3. l to third list",
    ["BRAILLE LINE:  'List with 1 item'",
     "     VISIBLE:  'List with 1 item', cursor=0",
     "BRAILLE LINE:  '•listing item'",
     "     VISIBLE:  '•listing item', cursor=1",
     "SPEECH OUTPUT: 'List with 1 item' voice=system",
     "SPEECH OUTPUT: '•listing item'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "4. i in third list",
    ["BRAILLE LINE:  '◦first sublevel'",
     "     VISIBLE:  '◦first sublevel', cursor=1",
     "SPEECH OUTPUT: '◦first sublevel'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "5. i in third list",
    ["BRAILLE LINE:  '▪look for the bullet on'",
     "     VISIBLE:  '▪look for the bullet on', cursor=1",
     "SPEECH OUTPUT: '▪look for the bullet on'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "6. i in third list",
    ["BRAILLE LINE:  '▪each sublevel'",
     "     VISIBLE:  '▪each sublevel', cursor=1",
     "SPEECH OUTPUT: '▪each sublevel'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "7. i in third list",
    ["BRAILLE LINE:  '▪they should all be different, except here.'",
     "     VISIBLE:  '▪they should all be different, e', cursor=1",
     "SPEECH OUTPUT: '▪they should all be different, except here.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "8. i in third list",
    ["BRAILLE LINE:  '▪second sublevel'",
     "     VISIBLE:  '▪second sublevel', cursor=1",
     "SPEECH OUTPUT: '▪second sublevel'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "9. i in third list",
    ["BRAILLE LINE:  '◦if your TYPE is circle'",
     "     VISIBLE:  '◦if your TYPE is circle', cursor=1",
     "SPEECH OUTPUT: '◦if your TYPE is circle'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "10. i in third list",
    ["BRAILLE LINE:  '•or even a disc'",
     "     VISIBLE:  '•or even a disc', cursor=1",
     "SPEECH OUTPUT: '•or even a disc'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "11. i in third list",
    ["BRAILLE LINE:  '◦was a composer who was not square'",
     "     VISIBLE:  '◦was a composer who was not squa', cursor=1",
     "SPEECH OUTPUT: '◦was a composer who was not square'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "12. i in third list",
    ["BRAILLE LINE:  '•would have liked the Who'",
     "     VISIBLE:  '•would have liked the Who', cursor=1",
     "SPEECH OUTPUT: '•would have liked the Who'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "13. i in third list",
    ["BRAILLE LINE:  '◦feeling listless'",
     "     VISIBLE:  '◦feeling listless', cursor=1",
     "SPEECH OUTPUT: '◦feeling listless"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "14. i in third list",
    ["BRAILLE LINE:  '▪blah, blah, blah'",
     "     VISIBLE:  '▪blah, blah, blah', cursor=1",
     "SPEECH OUTPUT: '▪blah, blah, blah'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "15. i in third list",
    ["BRAILLE LINE:  '•whine, whine, whine'",
     "     VISIBLE:  '•whine, whine, whine', cursor=1",
     "SPEECH OUTPUT: '•whine, whine, whine'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "16. i should wrap to top",
    ["BRAILLE LINE:  'Wrapping to top.'",
     "     VISIBLE:  'Wrapping to top.', cursor=0",
     "BRAILLE LINE:  '1.remember what the heck we are doing each day'",
     "     VISIBLE:  '1.remember what the heck we are ', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to top.' voice=system",
     "SPEECH OUTPUT: '1.remember what the heck we are doing each day'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
