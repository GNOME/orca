#!/usr/bin/python

"""Test of sayAll."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "1. KP_Add to do a SayAll",
    ["SPEECH OUTPUT: 'This looks like A to Z, but it's really Z to A.'",
     "SPEECH OUTPUT: 'Test:'",
     "SPEECH OUTPUT: 'z'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'y'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'x'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'w'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'v'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'u'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 't'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 's'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'r'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'q'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'p'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'o'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'n'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'm'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'l'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'k'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'j'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'i'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'h'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'g'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'f'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'e'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'd'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'c'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'b'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'a'",
     "SPEECH OUTPUT: 'image map link'",
     "SPEECH OUTPUT: 'Here is some text.'",
     "SPEECH OUTPUT: 'Safeway had some interesting (and problematic) image maps.'",
     "SPEECH OUTPUT: 'I didn't steal the images, but if you tab and look at the status bar, you should be able to see the URI for each region.'",
     "SPEECH OUTPUT: 'We should also be speaking and brailling it correctly now -- at least as best as we can given what they gave us.'",
     "SPEECH OUTPUT: 'wk09_frozenmovie'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
