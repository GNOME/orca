#!/usr/bin/python

"""Test of sayAll."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "1. KP_Add to do a SayAll",
    ["KNOWN ISSUE: Say All is not living up to its name.",
     "SPEECH OUTPUT: 'Home'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'News'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'Projects'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'Art'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'Support'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'Development'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'Community'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'live.gnome.org '",
     "SPEECH OUTPUT: 'heading level 1'",
     "SPEECH OUTPUT: 'entry Search'",
     "SPEECH OUTPUT: 'Titles push button grayed Text push button grayed'",
     "SPEECH OUTPUT: 'Home'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'RecentChanges'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'FindPage'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'HelpContents'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'Orca'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
