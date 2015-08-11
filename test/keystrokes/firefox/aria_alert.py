#!/usr/bin/python

"""Test of ARIA alert presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "1. Press button",
    ["KNOWN ISSUE: Because the link has focus, we double-present it.",
     "BRAILLE LINE:  'alert'",
     "     VISIBLE:  'alert', cursor=1",
     "BRAILLE LINE:  'close'",
     "     VISIBLE:  'close', cursor=1",
     "BRAILLE LINE:  'close'",
     "     VISIBLE:  'close', cursor=1",
     "SPEECH OUTPUT: 'This popup is created as a div in the HTML content, rather than being created in the DOM at the time of use. The display style is changed from \"none\" to \"block\" to hide and show it. close'",
     "SPEECH OUTPUT: 'close link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "2. Up Arrow",
    ["BRAILLE LINE:  'show it.'",
     "     VISIBLE:  'show it.', cursor=1",
     "SPEECH OUTPUT: 'show it. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "3. Up Arrow",
    ["BRAILLE LINE:  'from \"none\" to \"block\" to hide and'",
     "     VISIBLE:  'from \"none\" to \"block\" to hide a', cursor=1",
     "SPEECH OUTPUT: 'from \"none\" to \"block\" to hide and '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Up Arrow",
    ["BRAILLE LINE:  'use. The display style is changed'",
     "     VISIBLE:  'use. The display style is change', cursor=1",
     "SPEECH OUTPUT: 'use. The display style is changed '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "5. Up Arrow",
    ["BRAILLE LINE:  'created in the DOM at the time of'",
     "     VISIBLE:  'created in the DOM at the time o', cursor=1",
     "SPEECH OUTPUT: 'created in the DOM at the time of '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Up Arrow",
    ["BRAILLE LINE:  'HTML content, rather than being'",
     "     VISIBLE:  'HTML content, rather than being', cursor=1",
     "SPEECH OUTPUT: 'HTML content, rather than being '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Up Arrow",
    ["BRAILLE LINE:  'This popup is created as a div in the'",
     "     VISIBLE:  'This popup is created as a div i', cursor=1",
     "SPEECH OUTPUT: 'This popup is created as a div in the '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Up Arrow",
    ["KNOWN ISSUE: You should not be able to arrow out of this alert.",
     "BRAILLE LINE:  'Show (via display style) and put focus inside alert (on link) push button'",
     "     VISIBLE:  'Show (via display style) and put', cursor=1",
     "SPEECH OUTPUT: 'Show (via display style) and put focus inside alert (on link) push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Down Arrow",
    ["BRAILLE LINE:  'This popup is created as a div in the'",
     "     VISIBLE:  'This popup is created as a div i', cursor=1",
     "SPEECH OUTPUT: 'This popup is created as a div in the '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Down Arrow",
    ["BRAILLE LINE:  'HTML content, rather than being'",
     "     VISIBLE:  'HTML content, rather than being', cursor=1",
     "SPEECH OUTPUT: 'HTML content, rather than being '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Down Arrow",
    ["BRAILLE LINE:  'created in the DOM at the time of'",
     "     VISIBLE:  'created in the DOM at the time o', cursor=1",
     "SPEECH OUTPUT: 'created in the DOM at the time of '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Down Arrow",
    ["BRAILLE LINE:  'use. The display style is changed'",
     "     VISIBLE:  'use. The display style is change', cursor=1",
     "SPEECH OUTPUT: 'use. The display style is changed '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. Down Arrow",
    ["BRAILLE LINE:  'from \"none\" to \"block\" to hide and'",
     "     VISIBLE:  'from \"none\" to \"block\" to hide a', cursor=1",
     "SPEECH OUTPUT: 'from \"none\" to \"block\" to hide and '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "14. Down Arrow",
    ["BRAILLE LINE:  'show it.'",
     "     VISIBLE:  'show it.', cursor=1",
     "SPEECH OUTPUT: 'show it. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "15. Down Arrow",
    ["BRAILLE LINE:  'close'",
     "     VISIBLE:  'close', cursor=1",
     "SPEECH OUTPUT: 'close link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "17. Down Arrow",
    ["BRAILLE LINE:  'Some text after the alert to help with selection in order to view alert source'",
     "     VISIBLE:  'Some text after the alert to hel', cursor=1",
     "SPEECH OUTPUT: 'Some text after the alert to help with selection in order to view alert source'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "18. Return on close link",
    ["KNOWN ISSUE: We should present something here.",
     ""]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
