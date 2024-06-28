#!/usr/bin/python

"""Test of line navigation output of Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("e"))
sequence.append(utils.AssertPresentationAction(
    "1. E for next entry",
    ["BRAILLE LINE:  'Search  $l'",
     "     VISIBLE:  'Search  $l', cursor=7",
     "SPEECH OUTPUT: 'Search entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'After the iframe'",
     "     VISIBLE:  'After the iframe', cursor=1",
     "SPEECH OUTPUT: 'After the iframe'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down from the last line",
    [""]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("g"))
sequence.append(utils.AssertPresentationAction(
    "4. G for next image",
    ["BRAILLE LINE:  'Wrapping to top.'",
     "     VISIBLE:  'Wrapping to top.', cursor=0",
     "BRAILLE LINE:  'image'",
     "     VISIBLE:  'image', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to top.' voice=system",
     "SPEECH OUTPUT: 'image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'After the iframe'",
     "     VISIBLE:  'After the iframe', cursor=1",
     "SPEECH OUTPUT: 'After the iframe'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Up",
    ["BRAILLE LINE:  'Go to Blogger.com Search  $l Search this blog +1 push button 9 More Next Blog»Create Blog Sign In'",
     "     VISIBLE:  'Go to Blogger.com Search  $l Sea', cursor=1",
     "SPEECH OUTPUT: 'Go to Blogger.com link.'",
     "SPEECH OUTPUT: 'Search entry.'",
     "SPEECH OUTPUT: 'Search this blog link.'",
     "SPEECH OUTPUT: 'clickable'",
     "SPEECH OUTPUT: '+1 push button'",
     "SPEECH OUTPUT: '9'",
     "SPEECH OUTPUT: 'More'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'Next Blog»'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'Create Blog'",
     "SPEECH OUTPUT: 'link.'",
     "SPEECH OUTPUT: 'Sign In'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["BRAILLE LINE:  'After the iframe'",
     "     VISIBLE:  'After the iframe', cursor=1",
     "SPEECH OUTPUT: 'After the iframe'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
