#!/usr/bin/python

"""Test of menu and menu item output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Application class"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Return"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>p"))
sequence.append(utils.AssertPresentationAction(
    "Initial menu and menu item",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame Preferences menu'",
     "     VISIBLE:  'Preferences menu', cursor=1",
     "BRAILLE LINE:  'gtk3-demo-application application Application Class frame < > Prefer Dark Theme check menu item'",
     "     VISIBLE:  '< > Prefer Dark Theme check menu', cursor=1",
     "SPEECH OUTPUT: 'Preferences menu'",
     "SPEECH OUTPUT: 'Prefer Dark Theme check menu item not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Next menu item",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame < > Hide Titlebar when maximized check menu item'",
     "     VISIBLE:  '< > Hide Titlebar when maximized', cursor=1",
     "SPEECH OUTPUT: 'Hide Titlebar when maximized check menu item not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Next menu item",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame Color menu'",
     "     VISIBLE:  'Color menu', cursor=1",
     "SPEECH OUTPUT: 'Color menu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "Where Am I",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame Color menu'",
     "     VISIBLE:  'Color menu', cursor=1",
     "SPEECH OUTPUT: 'Application Class'",
     "SPEECH OUTPUT: 'frame'",
     "SPEECH OUTPUT: 'Preferences'",
     "SPEECH OUTPUT: 'menu'",
     "SPEECH OUTPUT: 'Color'",
     "SPEECH OUTPUT: 'menu 3 of 5.'",
     "SPEECH OUTPUT: 'C'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Get into Color menu",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame Preferences menu & y Red radio menu item(Ctrl+R)'",
     "     VISIBLE:  '& y Red radio menu item(Ctrl+R)', cursor=1",
     "SPEECH OUTPUT: 'Red not selected radio menu item Ctrl+R'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "Where Am I",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame Preferences menu & y Red radio menu item(Ctrl+R)'",
     "     VISIBLE:  '& y Red radio menu item(Ctrl+R)', cursor=1",
     "SPEECH OUTPUT: 'Application Class'",
     "SPEECH OUTPUT: 'frame'",
     "SPEECH OUTPUT: 'Preferences'",
     "SPEECH OUTPUT: 'menu'",
     "SPEECH OUTPUT: 'Color'",
     "SPEECH OUTPUT: 'menu'",
     "SPEECH OUTPUT: 'Red'",
     "SPEECH OUTPUT: 'radio menu item not selected Ctrl+R 1 of 3.'",
     "SPEECH OUTPUT: 'R'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Get out of Color menu",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame Color menu'",
     "     VISIBLE:  'Color menu', cursor=1",
     "SPEECH OUTPUT: 'Color menu'"]))

sequence.append(KeyComboAction("Escape"))
sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
