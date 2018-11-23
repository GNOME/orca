#!/usr/bin/python

"""Test of listbox output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("List Box"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "1. Where Am I",
    ["BRAILLE LINE:  'gtk3-demo application List Box frame GTKtoolkit 23 Nov 14 @breizhodrome yeah, that's for the OpenGL support that has been added recently list box GTKtoolkit 23 Nov 14 @breizhodrome yeah, that's for the OpenGL support that has been added recently Details push button Expand push button Reply push button Reshare push button Favorite push button & y More... toggle button reshareer push button GTK+ and friends push button '",
     "     VISIBLE:  'GTKtoolkit 23 Nov 14 @breizhodro', cursor=1",
     "SPEECH OUTPUT: 'GTKtoolkit 23 Nov 14 @breizhodrome yeah, that's for the OpenGL support that has been added recently.'",
     "SPEECH OUTPUT: '1 of 388.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Next item",
    ["BRAILLE LINE:  'gtk3-demo application List Box frame ebassi 15 Nov 14 RT @ebassi: embloggeration happened: http://t.co/9ukkNuSzuc \u2014 help out supporting GL on windows and macos in GTK+ 3.16. Resent by list box ebassi 15 Nov 14 RT @ebassi: embloggeration happened: http://t.co/9ukkNuSzuc \u2014 help out supporting GL on windows and macos in GTK+ 3.16. Resent by Details push button Expand push button Reply push button Reshare push button Favorite push button & y More... toggle button GTKtoolkit push button Emmanuele Bassi push button '",
     "     VISIBLE:  'ebassi 15 Nov 14 RT @ebassi: emb', cursor=1",
     "SPEECH OUTPUT: 'ebassi 15 Nov 14 RT @ebassi: embloggeration happened: http://t.co/9ukkNuSzuc \u2014 help out supporting GL on windows and macos in GTK+ 3.16. Resent by.'",
     "SPEECH OUTPUT: 'Expand push button'",
     "SPEECH OUTPUT: 'Reply push button'",
     "SPEECH OUTPUT: 'Reshare push button'",
     "SPEECH OUTPUT: 'Favorite push button'",
     "SPEECH OUTPUT: 'More... toggle button not pressed'",
     "SPEECH OUTPUT: 'GTKtoolkit push button'",
     "SPEECH OUTPUT: 'Emmanuele Bassi push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "3. Where Am I",
    ["BRAILLE LINE:  'gtk3-demo application List Box frame ebassi 15 Nov 14 RT @ebassi: embloggeration happened: http://t.co/9ukkNuSzuc \u2014 help out supporting GL on windows and macos in GTK+ 3.16. Resent by list box ebassi 15 Nov 14 RT @ebassi: embloggeration happened: http://t.co/9ukkNuSzuc \u2014 help out supporting GL on windows and macos in GTK+ 3.16. Resent by Details push button Expand push button Reply push button Reshare push button Favorite push button & y More... toggle button GTKtoolkit push button Emmanuele Bassi push button '",
     "     VISIBLE:  'ebassi 15 Nov 14 RT @ebassi: emb', cursor=1",
     "SPEECH OUTPUT: 'ebassi 15 Nov 14 RT @ebassi: embloggeration happened: http://t.co/9ukkNuSzuc \u2014 help out supporting GL on windows and macos in GTK+ 3.16. Resent by.'",
     "SPEECH OUTPUT: '2 of 388.'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
