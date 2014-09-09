#!/usr/bin/python

"""Test of sayAll."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "1. KP_Add to do a SayAll",
    ["SPEECH OUTPUT: 'This looks like A to Z, but it's really Z to A.'",
     "SPEECH OUTPUT: 'Test:'",
     "SPEECH OUTPUT: 'z image map link rect'",
     "SPEECH OUTPUT: 'y image map link rect'",
     "SPEECH OUTPUT: 'x image map link rect'",
     "SPEECH OUTPUT: 'w image map link rect'",
     "SPEECH OUTPUT: 'v image map link rect'",
     "SPEECH OUTPUT: 'u image map link rect'",
     "SPEECH OUTPUT: 't image map link rect'",
     "SPEECH OUTPUT: 's image map link rect'",
     "SPEECH OUTPUT: 'r image map link rect'",
     "SPEECH OUTPUT: 'q image map link rect'",
     "SPEECH OUTPUT: 'p image map link rect'",
     "SPEECH OUTPUT: 'o image map link rect'",
     "SPEECH OUTPUT: 'n image map link rect'",
     "SPEECH OUTPUT: 'm image map link rect'",
     "SPEECH OUTPUT: 'l image map link rect'",
     "SPEECH OUTPUT: 'k image map link rect'",
     "SPEECH OUTPUT: 'j image map link rect'",
     "SPEECH OUTPUT: 'i image map link rect'",
     "SPEECH OUTPUT: 'h image map link rect'",
     "SPEECH OUTPUT: 'g image map link rect'",
     "SPEECH OUTPUT: 'f image map link rect'",
     "SPEECH OUTPUT: 'e image map link rect'",
     "SPEECH OUTPUT: 'd image map link rect'",
     "SPEECH OUTPUT: 'c image map link rect'",
     "SPEECH OUTPUT: 'b image map link rect'",
     "SPEECH OUTPUT: 'a image map link rect'",
     "SPEECH OUTPUT: 'Here is some text.'",
     "SPEECH OUTPUT: 'Safeway had some interesting (and problematic) image maps. I didn't steal the images, but if you tab and look at the status bar, you should be able to see the URI for each region. We should also be speaking and brailling it correctly now -- at least as best as we can given what they gave us.'",
     "SPEECH OUTPUT: 'wk09_frozenmovie image link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'image'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
