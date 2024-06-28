#!/usr/bin/python

"""Test of structural navigation by heading."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'Index Vakbarát Hírportál h1'",
     "     VISIBLE:  'Index Vakbarát Hírportál h1', cursor=1",
     "SPEECH OUTPUT: 'Index Vakbarát Hírportál heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "2. h",
    ["BRAILLE LINE:  'Legfrissebb hírek h2'",
     "     VISIBLE:  'Legfrissebb hírek h2', cursor=1",
     "SPEECH OUTPUT: 'Legfrissebb hírek heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "3. h",
    ["BRAILLE LINE:  'Izrael bejelentette az ",
     "egyoldalú tûzszünetet h3'",
     "     VISIBLE:  'Izrael bejelentette az ",
     "egyoldal', cursor=1",
     "BRAILLE LINE:  'Izrael bejelentette az  h3'",
     "     VISIBLE:  'Izrael bejelentette az  h3', cursor=1",
     "SPEECH OUTPUT: 'Izrael bejelentette az ",
     "egyoldalú tûzszünetet'",
     "SPEECH OUTPUT: 'link heading level 3.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "4. h",
    ["BRAILLE LINE:  'Videók a Hudsonba zuhanó repülõrõl h3'",
     "     VISIBLE:  'Videók a Hudsonba zuhanó repülõr', cursor=1",
     "SPEECH OUTPUT: 'Videók a Hudsonba zuhanó repülõrõl'",
     "SPEECH OUTPUT: 'link heading level 3.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "5. h",
    ["BRAILLE LINE:  'Újabb pénzügyi guru tûnt el, pénzzel együtt h3'",
     "     VISIBLE:  'Újabb pénzügyi guru tûnt el, pén', cursor=1",
     "SPEECH OUTPUT: 'Újabb pénzügyi guru tûnt el, pénzzel együtt'",
     "SPEECH OUTPUT: 'link heading level 3.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Down",
    ["BRAILLE LINE:  'A 75 éves Arthur Nadeltõl több százmillió dollár követelnének az ügyfelei, de még a férfit sem találják.'",
     "     VISIBLE:  'A 75 éves Arthur Nadeltõl több s', cursor=1",
     "SPEECH OUTPUT: 'A 75 éves Arthur Nadeltõl több százmillió dollár követelnének az ügyfelei, de még a férfit sem találják.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Down",
    ["BRAILLE LINE:  '1150 embert utcára tesz a pécsi Elcoteq h3'",
     "     VISIBLE:  '1150 embert utcára tesz a pécsi ', cursor=1",
     "SPEECH OUTPUT: '1150 embert utcára tesz a pécsi Elcoteq'",
     "SPEECH OUTPUT: 'link heading level 3.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "8. h",
    ["BRAILLE LINE:  'Hamarosan újraindul a gázszállítás h3'",
     "     VISIBLE:  'Hamarosan újraindul a gázszállít', cursor=1",
     "SPEECH OUTPUT: 'Hamarosan újraindul a gázszállítás'",
     "SPEECH OUTPUT: 'link heading level 3.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Down",
    ["BRAILLE LINE:  'Megállapodott Putyin és Tyimosenko az orosz-ukrán szerzõdésrõl. Amint lepapírozzák, jön a gáz.'",
     "     VISIBLE:  'Megállapodott Putyin és Tyimosen', cursor=1",
     "SPEECH OUTPUT: 'Megállapodott Putyin és Tyimosenko az orosz-ukrán szerzõdésrõl. Amint lepapírozzák, jön a gáz.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>h"))
sequence.append(utils.AssertPresentationAction(
    "10. Shift+h",
    ["BRAILLE LINE:  'Hamarosan újraindul a gázszállítás h3'",
     "     VISIBLE:  'Hamarosan újraindul a gázszállít', cursor=1",
     "SPEECH OUTPUT: 'Hamarosan újraindul a gázszállítás'",
     "SPEECH OUTPUT: 'link heading level 3.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
