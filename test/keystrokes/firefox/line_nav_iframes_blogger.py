#!/usr/bin/python

"""Test of line navigation output of Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("e"))
sequence.append(utils.AssertPresentationAction(
    "1. E for next entry",
    ["BRAILLE LINE:  'Search  $l'",
     "     VISIBLE:  'Search  $l', cursor=0",
     "SPEECH OUTPUT: 'Search entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["KNOWN ISSUE: We're stuck on this line",
     "BRAILLE LINE:  'Go to Blogger.com Search  $l Search this blog & y Click here to publicly +1 this. toggle button 15 More Next Blog»Create Blog Sign In internal frame'",
     "     VISIBLE:  'Go to Blogger.com Search  $l Sea', cursor=1",
     "SPEECH OUTPUT: 'Go to Blogger.com link.'",
     "SPEECH OUTPUT: 'Search entry'",
     "SPEECH OUTPUT: 'Search this blog link.'",
     "SPEECH OUTPUT: 'clickable'",
     "SPEECH OUTPUT: 'Click here to publicly +1 this. toggle button not pressed'",
     "SPEECH OUTPUT: '15'",
     "SPEECH OUTPUT: 'More link.'",
     "SPEECH OUTPUT: 'Next Blog» link.'",
     "SPEECH OUTPUT: 'Create Blog link.'",
     "SPEECH OUTPUT: 'Sign In link.'",
     "SPEECH OUTPUT: 'internal frame'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["KNOWN ISSUE: We're stuck on this line",
     "BRAILLE LINE:  'Go to Blogger.com Search  $l Search this blog & y Click here to publicly +1 this. toggle button 15 More Next Blog»Create Blog Sign In internal frame'",
     "     VISIBLE:  'Go to Blogger.com Search  $l Sea', cursor=1",
     "SPEECH OUTPUT: 'Go to Blogger.com link.'",
     "SPEECH OUTPUT: 'Search entry'",
     "SPEECH OUTPUT: 'Search this blog link.'",
     "SPEECH OUTPUT: 'clickable'",
     "SPEECH OUTPUT: 'Click here to publicly +1 this. toggle button not pressed'",
     "SPEECH OUTPUT: '15'",
     "SPEECH OUTPUT: 'More link.'",
     "SPEECH OUTPUT: 'Next Blog» link.'",
     "SPEECH OUTPUT: 'Create Blog link.'",
     "SPEECH OUTPUT: 'Sign In link.'",
     "SPEECH OUTPUT: 'internal frame'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
