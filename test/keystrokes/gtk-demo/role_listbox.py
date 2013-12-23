#!/usr/bin/python

"""Test of listbox output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("List Box"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Return"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "Where Am I",
    ["KNOWN ISSUE: The order of presentation can vary. Seems to be a timing issue.",
     "BRAILLE LINE:  'gtk-demo application List Box frame list box 2",
     "Reshares 4",
     "Favorites 23:00:00 - 26 Mar 2013 Resent by @GTKtoolkit 26 Mar 13 GTK+ 3.8.0 (STABLE) released: wayland, Multi-application Broadway, improved CSS support and more ... http://ur1.ca/d6yms  #gtk #gtk3 Details push button'",
     "     VISIBLE:  '2",
     "Reshares 4",
     "Favorites 23:00:00 ', cursor=1",
     "SPEECH OUTPUT: '2",
     "Reshares 4",
     "Favorites 23:00:00 - 26 Mar 2013 Resent by @GTKtoolkit 26 Mar 13 GTK+ 3.8.0 (STABLE) released: wayland, Multi-application Broadway, improved CSS support and more ... http://ur1.ca/d6yms  #gtk #gtk3'",
     "SPEECH OUTPUT: '1 of 8'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Next item",
    ["KNOWN ISSUE: The order of presentation can vary. Seems to be a timing issue.",
     "BRAILLE LINE:  'gtk-demo application List Box frame list box 0",
     "Favorites 0",
     "Reshares 20:20:00 - 11 Oct 2013 @GTKtoolkit 11 Oct 13 GLib 2.34.0 (STABLE) released: http://ur1.ca/aj4du  #glib Details push button'",
     "     VISIBLE:  'Resent by 0",
     "Favorites 0",
     "Reshares', cursor=1",
     "SPEECH OUTPUT: 'Resent by 0",
     "Favorites 0",
     "Reshares 20:20:00 - 11 Oct 2013 @GTKtoolkit 11 Oct 13 GLib 2.34.0 (STABLE) released: http://ur1.ca/aj4du  #glib Details push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "Where Am I",
    ["KNOWN ISSUE: The order of presentation can vary. Seems to be a timing issue.",
     "BRAILLE LINE:  'gtk-demo application List Box frame list box Resent by 0",
     "Favorites 0",
     "Reshares 20:20:00 - 11 Oct 2013 @GTKtoolkit 11 Oct 13 GLib 2.34.0 (STABLE) released: http://ur1.ca/aj4du  #glib Details push button'",
     "     VISIBLE:  'Resent by 0",
     "Favorites 0",
     "Reshares', cursor=1",
     "SPEECH OUTPUT: 'Resent by 0",
     "Favorites 0",
     "Reshares 20:20:00 - 11 Oct 2013 @GTKtoolkit 11 Oct 13 GLib 2.34.0 (STABLE) released: http://ur1.ca/aj4du  #glib'",
     "SPEECH OUTPUT: '2 of 8'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
