#!/usr/bin/python

"""Test of menu radio button output using Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Alt>v"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("y"))
sequence.append(utils.AssertPresentationAction(
    "1. y for the Page Style menu",
    ["BRAILLE LINE:  'Firefox application Firefox Nightly frame Menu Bar tool bar Application menu bar View menu & y No Style radio menu item'",
     "     VISIBLE:  '& y No Style radio menu item', cursor=1",
     "SPEECH OUTPUT: 'Page Style menu'",
     "SPEECH OUTPUT: 'No Style not selected radio menu item'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "2. Basic Where Am I",
    ["BRAILLE LINE:  'Firefox application Firefox Nightly frame Menu Bar tool bar Application menu bar View menu & y No Style radio menu item'",
     "     VISIBLE:  '& y No Style radio menu item', cursor=1",
     "SPEECH OUTPUT: 'View menu'",
     "SPEECH OUTPUT: 'Page Style menu'",
     "SPEECH OUTPUT: 'Menu Bar tool bar No Style radio menu item not selected 1 of 2.'",
     "SPEECH OUTPUT: 'N'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Down Arrow in menu",
    ["BRAILLE LINE:  'Firefox application Firefox Nightly frame Menu Bar tool bar Application menu bar View menu &=y Basic Page Style radio menu item'",
     "     VISIBLE:  '&=y Basic Page Style radio menu ', cursor=1",
     "SPEECH OUTPUT: 'Basic Page Style selected radio menu item'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "4. Basic Where Am I",
    ["BRAILLE LINE:  'Firefox application Firefox Nightly frame Menu Bar tool bar Application menu bar View menu &=y Basic Page Style radio menu item'",
     "     VISIBLE:  '&=y Basic Page Style radio menu ', cursor=1",
     "SPEECH OUTPUT: 'View menu'",
     "SPEECH OUTPUT: 'Page Style menu'",
     "SPEECH OUTPUT: 'Menu Bar tool bar Basic Page Style radio menu item selected 2 of 2.'",
     "SPEECH OUTPUT: 'B'"]))

sequence.append(KeyComboAction("Escape"))
sequence.append(KeyComboAction("Escape"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
