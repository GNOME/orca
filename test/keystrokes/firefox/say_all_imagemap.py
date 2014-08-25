#!/usr/bin/python

"""Test of sayAll."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "1. KP_Add to do a SayAll",
    ["KNOWN ISSUE: Due to a test-timing, flakiness issue we do not always speak the urls for the last imagemap links",
     "SPEECH OUTPUT: 'This looks like A to Z, but it's really Z to A.'",
     "SPEECH OUTPUT: 'Test:'",
     "SPEECH OUTPUT: 'z link z image map link'",
     "SPEECH OUTPUT: 'y link y image map link'",
     "SPEECH OUTPUT: 'x link x image map link'",
     "SPEECH OUTPUT: 'w link w image map link'",
     "SPEECH OUTPUT: 'v link v image map link'",
     "SPEECH OUTPUT: 'u link u image map link'",
     "SPEECH OUTPUT: 't link t image map link'",
     "SPEECH OUTPUT: 's link s image map link'",
     "SPEECH OUTPUT: 'r link r image map link'",
     "SPEECH OUTPUT: 'q link q image map link'",
     "SPEECH OUTPUT: 'p link p image map link'",
     "SPEECH OUTPUT: 'o link o image map link'",
     "SPEECH OUTPUT: 'n link n image map link'",
     "SPEECH OUTPUT: 'm link m image map link'",
     "SPEECH OUTPUT: 'l link l image map link'",
     "SPEECH OUTPUT: 'k link k image map link'",
     "SPEECH OUTPUT: 'j link j image map link'",
     "SPEECH OUTPUT: 'i link i image map link'",
     "SPEECH OUTPUT: 'h link h image map link'",
     "SPEECH OUTPUT: 'g link g image map link'",
     "SPEECH OUTPUT: 'f link f image map link'",
     "SPEECH OUTPUT: 'e link e image map link'",
     "SPEECH OUTPUT: 'd link d image map link'",
     "SPEECH OUTPUT: 'c link c image map link'",
     "SPEECH OUTPUT: 'b link b image map link'",
     "SPEECH OUTPUT: 'a link a image map link'",
     "SPEECH OUTPUT: 'Here is some text.'",
     "SPEECH OUTPUT: 'Safeway had some interesting (and problematic) image maps. I didn't steal the images, but if you tab and look at the status bar, you should be able to see the URI for each region. We should also be speaking and brailling it correctly now -- at least as best as we can given what they gave us.'",
     "SPEECH OUTPUT: 'blank'",
     "SPEECH OUTPUT: 'wk09_frozenmovie link image'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'blank'",
     "SPEECH OUTPUT: 'blank'",
     "SPEECH OUTPUT: 'shop.safeway.com link shop.safeway.com image map link'",
     "SPEECH OUTPUT: 'Rancher's Reserve link Rancher's Reserve image map link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'blank'",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
