#!/usr/bin/python

import gi
gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk
from gi.repository import Gtk
from macaroon.playback import *
import utils

clipboard = Gtk.Clipboard.get(Gdk.Atom.intern("CLIPBOARD", False))
clipboard.set_text("Hello world", -1)

sequence = MacroSequence()
sequence.append(KeyComboAction("Return"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control><Shift>v"))
sequence.append(utils.AssertPresentationAction(
    "1. Paste",
    ["BRAILLE LINE:  '$ Hello world'",
     "     VISIBLE:  '$ Hello world', cursor=14",
     "BRAILLE LINE:  'Pasted contents from clipboard.'",
     "     VISIBLE:  'Pasted contents from clipboard.', cursor=0",
     "BRAILLE LINE:  '$ Hello world'",
     "     VISIBLE:  '$ Hello world', cursor=14",
     "SPEECH OUTPUT: 'Pasted contents from clipboard.' voice=system"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
