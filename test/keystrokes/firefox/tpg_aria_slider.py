# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of ARIA sliders using Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://www.paciellogroup.com/blog/misc/samples/aria/slider/"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("ARIA Slider Examples - TPG", 
                              acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Extra loading time.
#
sequence.append(PauseAction(5000))

########################################################################
# Tab to each slider and change its value.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to Volume Slider", 
    ["BRAILLE LINE:  'Volume 0 % Slider'",
     "     VISIBLE:  'Volume 0 % Slider', cursor=1",
     "SPEECH OUTPUT: 'Volume slider 0 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Volume 1. Right Arrow", 
    ["BUG? - Lots of unneeded braille updating here and in the assertions that follow for the Volume slider. Just marking it here.",
     "BRAILLE LINE:  'Volume 0 % Slider'",
     "     VISIBLE:  'Volume 0 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 0 % Slider'",
     "     VISIBLE:  'Volume 0 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 1 % Slider'",
     "     VISIBLE:  'Volume 1 % Slider', cursor=1",
     "SPEECH OUTPUT: '1 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Volume 2. Right Arrow", 
    ["BRAILLE LINE:  'Volume 1 % Slider'",
     "     VISIBLE:  'Volume 1 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 1 % Slider'",
     "     VISIBLE:  'Volume 1 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 2 % Slider'",
     "     VISIBLE:  'Volume 2 % Slider', cursor=1",
     "SPEECH OUTPUT: '2 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Volume 3. Right Arrow", 
    ["BRAILLE LINE:  'Volume 2 % Slider'",
     "     VISIBLE:  'Volume 2 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 2 % Slider'",
     "     VISIBLE:  'Volume 2 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 3 % Slider'",
     "     VISIBLE:  'Volume 3 % Slider', cursor=1",
     "SPEECH OUTPUT: '3 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Volume 1. Left Arrow", 
    ["BRAILLE LINE:  'Volume 3 % Slider'",
     "     VISIBLE:  'Volume 3 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 3 % Slider'",
     "     VISIBLE:  'Volume 3 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 2 % Slider'",
     "     VISIBLE:  'Volume 2 % Slider', cursor=1",
     "SPEECH OUTPUT: '2 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Volume 2. Left Arrow", 
    ["BRAILLE LINE:  'Volume 2 % Slider'",
     "     VISIBLE:  'Volume 2 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 2 % Slider'",
     "     VISIBLE:  'Volume 2 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 1 % Slider'",
     "     VISIBLE:  'Volume 1 % Slider', cursor=1",
     "SPEECH OUTPUT: '1 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Volume 3. Left Arrow", 
    ["BRAILLE LINE:  'Volume 1 % Slider'",
     "     VISIBLE:  'Volume 1 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 1 % Slider'",
     "     VISIBLE:  'Volume 1 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 0 % Slider'",
     "     VISIBLE:  'Volume 0 % Slider', cursor=1",
     "SPEECH OUTPUT: '0 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Volume 1. Up Arrow", 
    ["BRAILLE LINE:  'Volume 0 % Slider'",
     "     VISIBLE:  'Volume 0 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 0 % Slider'",
     "     VISIBLE:  'Volume 0 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 1 % Slider'",
     "     VISIBLE:  'Volume 1 % Slider', cursor=1",
     "SPEECH OUTPUT: '1 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Volume 2. Up Arrow", 
    ["BRAILLE LINE:  'Volume 1 % Slider'",
     "     VISIBLE:  'Volume 1 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 1 % Slider'",
     "     VISIBLE:  'Volume 1 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 2 % Slider'",
     "     VISIBLE:  'Volume 2 % Slider', cursor=1",
     "SPEECH OUTPUT: '2 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Volume 3. Up Arrow", 
    ["BRAILLE LINE:  'Volume 2 % Slider'",
     "     VISIBLE:  'Volume 2 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 2 % Slider'",
     "     VISIBLE:  'Volume 2 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 3 % Slider'",
     "     VISIBLE:  'Volume 3 % Slider', cursor=1",
     "SPEECH OUTPUT: '3 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Volume 1. Down Arrow", 
    ["BRAILLE LINE:  'Volume 3 % Slider'",
     "     VISIBLE:  'Volume 3 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 3 % Slider'",
     "     VISIBLE:  'Volume 3 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 2 % Slider'",
     "     VISIBLE:  'Volume 2 % Slider', cursor=1",
     "SPEECH OUTPUT: '2 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Volume 2. Down Arrow", 
    ["BRAILLE LINE:  'Volume 2 % Slider'",
     "     VISIBLE:  'Volume 2 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 2 % Slider'",
     "     VISIBLE:  'Volume 2 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 1 % Slider'",
     "     VISIBLE:  'Volume 1 % Slider', cursor=1",
     "SPEECH OUTPUT: '1 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Volume 3. Down Arrow", 
    ["BRAILLE LINE:  'Volume 1 % Slider'",
     "     VISIBLE:  'Volume 1 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 1 % Slider'",
     "     VISIBLE:  'Volume 1 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 0 % Slider'",
     "     VISIBLE:  'Volume 0 % Slider', cursor=1",
     "SPEECH OUTPUT: '0 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Up"))
sequence.append(utils.AssertPresentationAction(
    "Volume 1. Page Up", 
    ["BRAILLE LINE:  'Volume 0 % Slider'",
     "     VISIBLE:  'Volume 0 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 0 % Slider'",
     "     VISIBLE:  'Volume 0 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 25 % Slider'",
     "     VISIBLE:  'Volume 25 % Slider', cursor=1",
     "SPEECH OUTPUT: '25 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Up"))
sequence.append(utils.AssertPresentationAction(
    "Volume 2. Page Up", 
    ["BRAILLE LINE:  'Volume 25 % Slider'",
     "     VISIBLE:  'Volume 25 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 25 % Slider'",
     "     VISIBLE:  'Volume 25 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 50 % Slider'",
     "     VISIBLE:  'Volume 50 % Slider', cursor=1",
     "SPEECH OUTPUT: '50 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "Volume 1. Page Down", 
    ["BRAILLE LINE:  'Volume 50 % Slider'",
     "     VISIBLE:  'Volume 50 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 50 % Slider'",
     "     VISIBLE:  'Volume 50 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 25 % Slider'",
     "     VISIBLE:  'Volume 25 % Slider', cursor=1",
     "SPEECH OUTPUT: '25 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "Volume 2. Page Down", 
    ["BRAILLE LINE:  'Volume 25 % Slider'",
     "     VISIBLE:  'Volume 25 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 25 % Slider'",
     "     VISIBLE:  'Volume 25 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 0 % Slider'",
     "     VISIBLE:  'Volume 0 % Slider', cursor=1",
     "SPEECH OUTPUT: '0 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("End"))
sequence.append(utils.AssertPresentationAction(
    "Volume End", 
    ["BRAILLE LINE:  'Volume 0 % Slider'",
     "     VISIBLE:  'Volume 0 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 0 % Slider'",
     "     VISIBLE:  'Volume 0 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 100 % Slider'",
     "     VISIBLE:  'Volume 100 % Slider', cursor=1",
     "SPEECH OUTPUT: '100 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Home"))
sequence.append(utils.AssertPresentationAction(
    "Volume Home", 
    ["BRAILLE LINE:  'Volume 100 % Slider'",
     "     VISIBLE:  'Volume 100 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 100 % Slider'",
     "     VISIBLE:  'Volume 100 % Slider', cursor=1",
     "BRAILLE LINE:  'Volume 0 % Slider'",
     "     VISIBLE:  'Volume 0 % Slider', cursor=1",
     "SPEECH OUTPUT: '0 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to Food Quality Slider", 
    ["BRAILLE LINE:  'Food Quality terrible Slider'",
     "     VISIBLE:  'Food Quality terrible Slider', cursor=1",
     "SPEECH OUTPUT: 'Food Quality slider terrible'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Food Quality 1. Right Arrow", 
    ["BRAILLE LINE:  'Food Quality bad Slider'",
     "     VISIBLE:  'Food Quality bad Slider', cursor=1",
     "SPEECH OUTPUT: 'bad'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Food Quality 2. Right Arrow", 
    ["BRAILLE LINE:  'Food Quality decent Slider'",
     "     VISIBLE:  'Food Quality decent Slider', cursor=1",
     "SPEECH OUTPUT: 'decent'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Food Quality 3. Right Arrow", 
    ["BRAILLE LINE:  'Food Quality good Slider'",
     "     VISIBLE:  'Food Quality good Slider', cursor=1",
     "SPEECH OUTPUT: 'good'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Food Quality 1. Left Arrow", 
    ["BRAILLE LINE:  'Food Quality decent Slider'",
     "     VISIBLE:  'Food Quality decent Slider', cursor=1",
     "SPEECH OUTPUT: 'decent'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Food Quality 2. Left Arrow", 
    ["BRAILLE LINE:  'Food Quality bad Slider'",
     "     VISIBLE:  'Food Quality bad Slider', cursor=1",
     "SPEECH OUTPUT: 'bad'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Food Quality 3. Left Arrow", 
    ["BRAILLE LINE:  'Food Quality terrible Slider'",
     "     VISIBLE:  'Food Quality terrible Slider', cursor=1",
     "SPEECH OUTPUT: 'terrible'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Food Quality 1. Up Arrow", 
    ["BRAILLE LINE:  'Food Quality bad Slider'",
     "     VISIBLE:  'Food Quality bad Slider', cursor=1",
     "SPEECH OUTPUT: 'bad'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Food Quality 2. Up Arrow", 
    ["BRAILLE LINE:  'Food Quality decent Slider'",
     "     VISIBLE:  'Food Quality decent Slider', cursor=1",
     "SPEECH OUTPUT: 'decent'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Food Quality 3. Up Arrow", 
    ["BRAILLE LINE:  'Food Quality good Slider'",
     "     VISIBLE:  'Food Quality good Slider', cursor=1",
     "SPEECH OUTPUT: 'good'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Food Quality 1. Down Arrow", 
     ["BRAILLE LINE:  'Food Quality decent Slider'",
     "     VISIBLE:  'Food Quality decent Slider', cursor=1",
     "SPEECH OUTPUT: 'decent'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Food Quality 2. Down Arrow", 
    ["BRAILLE LINE:  'Food Quality bad Slider'",
     "     VISIBLE:  'Food Quality bad Slider', cursor=1",
     "SPEECH OUTPUT: 'bad'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Food Quality 3. Down Arrow", 
    ["BRAILLE LINE:  'Food Quality terrible Slider'",
     "     VISIBLE:  'Food Quality terrible Slider', cursor=1",
     "SPEECH OUTPUT: 'terrible'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Up"))
sequence.append(utils.AssertPresentationAction(
    "Food Quality 1. Page Up", 
     ["BRAILLE LINE:  'Food Quality bad Slider'",
     "     VISIBLE:  'Food Quality bad Slider', cursor=1",
     "SPEECH OUTPUT: 'bad'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Up"))
sequence.append(utils.AssertPresentationAction(
    "Food Quality 2. Page Up", 
    ["BRAILLE LINE:  'Food Quality decent Slider'",
     "     VISIBLE:  'Food Quality decent Slider', cursor=1",
     "SPEECH OUTPUT: 'decent'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "Food Quality 1. Page Down", 
    ["BRAILLE LINE:  'Food Quality bad Slider'",
     "     VISIBLE:  'Food Quality bad Slider', cursor=1",
     "SPEECH OUTPUT: 'bad'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "Food Quality 2. Page Down", 
    ["BRAILLE LINE:  'Food Quality terrible Slider'",
     "     VISIBLE:  'Food Quality terrible Slider', cursor=1",
     "SPEECH OUTPUT: 'terrible'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("End"))
sequence.append(utils.AssertPresentationAction(
    "Food Quality End", 
    ["BRAILLE LINE:  'Food Quality excellent Slider'",
     "     VISIBLE:  'Food Quality excellent Slider', cursor=1",
     "SPEECH OUTPUT: 'excellent'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Home"))
sequence.append(utils.AssertPresentationAction(
    "Food Quality Home", 
    ["BRAILLE LINE:  'Food Quality terrible Slider'",
     "     VISIBLE:  'Food Quality terrible Slider', cursor=1",
     "SPEECH OUTPUT: 'terrible'"]))

sequence.append(KeyComboAction("Tab"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to Filesize Slider", 
    ["BRAILLE LINE:  'Filesize 0 Slider'",
     "     VISIBLE:  'Filesize 0 Slider', cursor=1",
     "SPEECH OUTPUT: 'Filesize slider 0'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Filesize 1. Right Arrow", 
    ["BRAILLE LINE:  'Filesize 1 Slider'",
     "     VISIBLE:  'Filesize 1 Slider', cursor=1",
     "SPEECH OUTPUT: '1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Filesize 2. Right Arrow", 
    ["BRAILLE LINE:  'Filesize 2 Slider'",
     "     VISIBLE:  'Filesize 2 Slider', cursor=1",
     "SPEECH OUTPUT: '2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Filesize 3. Right Arrow", 
    ["BRAILLE LINE:  'Filesize 3 Slider'",
     "     VISIBLE:  'Filesize 3 Slider', cursor=1",
     "SPEECH OUTPUT: '3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Filesize 1. Left Arrow", 
    ["BRAILLE LINE:  'Filesize 2 Slider'",
     "     VISIBLE:  'Filesize 2 Slider', cursor=1",
     "SPEECH OUTPUT: '2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Filesize 2. Left Arrow", 
    ["BRAILLE LINE:  'Filesize 1 Slider'",
     "     VISIBLE:  'Filesize 1 Slider', cursor=1",
     "SPEECH OUTPUT: '1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Filesize 3. Left Arrow", 
    ["BRAILLE LINE:  'Filesize 0 Slider'",
     "     VISIBLE:  'Filesize 0 Slider', cursor=1",
     "SPEECH OUTPUT: '0'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Filesize 1. Up Arrow", 
    ["BRAILLE LINE:  'Filesize 1 Slider'",
     "     VISIBLE:  'Filesize 1 Slider', cursor=1",
     "SPEECH OUTPUT: '1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Filesize 2. Up Arrow", 
    ["BRAILLE LINE:  'Filesize 2 Slider'",
     "     VISIBLE:  'Filesize 2 Slider', cursor=1",
     "SPEECH OUTPUT: '2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Filesize 3. Up Arrow", 
    ["BRAILLE LINE:  'Filesize 3 Slider'",
     "     VISIBLE:  'Filesize 3 Slider', cursor=1",
     "SPEECH OUTPUT: '3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Filesize 1. Down Arrow", 
    ["BRAILLE LINE:  'Filesize 2 Slider'",
     "     VISIBLE:  'Filesize 2 Slider', cursor=1",
     "SPEECH OUTPUT: '2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Filesize 2. Down Arrow", 
    ["BRAILLE LINE:  'Filesize 1 Slider'",
     "     VISIBLE:  'Filesize 1 Slider', cursor=1",
     "SPEECH OUTPUT: '1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Filesize 3. Down Arrow", 
    ["BRAILLE LINE:  'Filesize 0 Slider'",
     "     VISIBLE:  'Filesize 0 Slider', cursor=1",
     "SPEECH OUTPUT: '0'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Up"))
sequence.append(utils.AssertPresentationAction(
    "Filesize 1. Page Up", 
    ["BRAILLE LINE:  'Filesize 250 Slider'",
     "     VISIBLE:  'Filesize 250 Slider', cursor=1",
     "SPEECH OUTPUT: '250'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Up"))
sequence.append(utils.AssertPresentationAction(
    "Filesize 2. Page Up", 
    ["BRAILLE LINE:  'Filesize 500 Slider'",
     "     VISIBLE:  'Filesize 500 Slider', cursor=1",
     "SPEECH OUTPUT: '500'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "Filesize 1. Page Down", 
    ["BRAILLE LINE:  'Filesize 250 Slider'",
     "     VISIBLE:  'Filesize 250 Slider', cursor=1",
     "SPEECH OUTPUT: '250'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "Filesize 2. Page Down", 
    ["BRAILLE LINE:  'Filesize 0 Slider'",
     "     VISIBLE:  'Filesize 0 Slider', cursor=1",
     "SPEECH OUTPUT: '0'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("End"))
sequence.append(utils.AssertPresentationAction(
    "Filesize End", 
     ["BRAILLE LINE:  'Filesize 1000 Slider'",
     "     VISIBLE:  'Filesize 1000 Slider', cursor=1",
     "SPEECH OUTPUT: '1000'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Home"))
sequence.append(utils.AssertPresentationAction(
    "Filesize Home", 
    ["BRAILLE LINE:  'Filesize 0 Slider'",
     "     VISIBLE:  'Filesize 0 Slider', cursor=1",
     "SPEECH OUTPUT: '0'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to Staff Slider", 
    ["BRAILLE LINE:  'The staff was helpful Strongly disagree Slider'",
     "     VISIBLE:  'The staff was helpful Strongly d', cursor=1",
     "SPEECH OUTPUT: 'The staff was helpful slider Strongly disagree'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Staff 1. Right Arrow", 
    ["BRAILLE LINE:  'The staff was helpful Disagree Slider'",
     "     VISIBLE:  'The staff was helpful Disagree S', cursor=1",
     "SPEECH OUTPUT: 'Disagree'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Staff 2. Right Arrow", 
    ["BRAILLE LINE:  'The staff was helpful Neutral Slider'",
     "     VISIBLE:  'The staff was helpful Neutral Sl', cursor=1",
     "SPEECH OUTPUT: 'Neutral'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Staff 3. Right Arrow", 
    ["BRAILLE LINE:  'The staff was helpful Agree Slider'",
     "     VISIBLE:  'The staff was helpful Agree Slid', cursor=1",
     "SPEECH OUTPUT: 'Agree'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Staff 1. Left Arrow", 
    ["BRAILLE LINE:  'The staff was helpful Neutral Slider'",
     "     VISIBLE:  'The staff was helpful Neutral Sl', cursor=1",
     "SPEECH OUTPUT: 'Neutral'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Staff 2. Left Arrow", 
    ["BRAILLE LINE:  'The staff was helpful Disagree Slider'",
     "     VISIBLE:  'The staff was helpful Disagree S', cursor=1",
     "SPEECH OUTPUT: 'Disagree'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Staff 3. Left Arrow", 
    ["BRAILLE LINE:  'The staff was helpful Strongly disagree Slider'",
     "     VISIBLE:  'The staff was helpful Strongly d', cursor=1",
     "SPEECH OUTPUT: 'Strongly disagree'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Staff 1. Up Arrow", 
    ["BRAILLE LINE:  'The staff was helpful Disagree Slider'",
     "     VISIBLE:  'The staff was helpful Disagree S', cursor=1",
     "SPEECH OUTPUT: 'Disagree'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Staff 2. Up Arrow", 
    ["BRAILLE LINE:  'The staff was helpful Neutral Slider'",
     "     VISIBLE:  'The staff was helpful Neutral Sl', cursor=1",
     "SPEECH OUTPUT: 'Neutral'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Staff 3. Up Arrow", 
    ["BRAILLE LINE:  'The staff was helpful Agree Slider'",
     "     VISIBLE:  'The staff was helpful Agree Slid', cursor=1",
     "SPEECH OUTPUT: 'Agree'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Staff 1. Down Arrow", 
    ["BRAILLE LINE:  'The staff was helpful Neutral Slider'",
     "     VISIBLE:  'The staff was helpful Neutral Sl', cursor=1",
     "SPEECH OUTPUT: 'Neutral'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Staff 2. Down Arrow", 
    ["BRAILLE LINE:  'The staff was helpful Disagree Slider'",
     "     VISIBLE:  'The staff was helpful Disagree S', cursor=1",
     "SPEECH OUTPUT: 'Disagree'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Staff 3. Down Arrow", 
    ["BRAILLE LINE:  'The staff was helpful Strongly disagree Slider'",
     "     VISIBLE:  'The staff was helpful Strongly d', cursor=1",
     "SPEECH OUTPUT: 'Strongly disagree'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Up"))
sequence.append(utils.AssertPresentationAction(
    "Staff 1. Page Up", 
    ["BRAILLE LINE:  'The staff was helpful Disagree Slider'",
     "     VISIBLE:  'The staff was helpful Disagree S', cursor=1",
     "SPEECH OUTPUT: 'Disagree'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Up"))
sequence.append(utils.AssertPresentationAction(
    "Staff 2. Page Up", 
    ["BRAILLE LINE:  'The staff was helpful Neutral Slider'",
     "     VISIBLE:  'The staff was helpful Neutral Sl', cursor=1",
     "SPEECH OUTPUT: 'Neutral'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "Staff 1. Page Down", 
    ["BRAILLE LINE:  'The staff was helpful Disagree Slider'",
     "     VISIBLE:  'The staff was helpful Disagree S', cursor=1",
     "SPEECH OUTPUT: 'Disagree'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "Staff 2. Page Down", 
    ["BRAILLE LINE:  'The staff was helpful Strongly disagree Slider'",
     "     VISIBLE:  'The staff was helpful Strongly d', cursor=1",
     "SPEECH OUTPUT: 'Strongly disagree'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("End"))
sequence.append(utils.AssertPresentationAction(
    "Staff End", 
    ["BRAILLE LINE:  'The staff was helpful Strongly agree Slider'",
     "     VISIBLE:  'The staff was helpful Strongly a', cursor=1",
     "SPEECH OUTPUT: 'Strongly agree'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Home"))
sequence.append(utils.AssertPresentationAction(
    "Staff Home", 
    ["BRAILLE LINE:  'The staff was helpful Strongly disagree Slider'",
     "     VISIBLE:  'The staff was helpful Strongly d', cursor=1",
     "SPEECH OUTPUT: 'Strongly disagree'"]))

sequence.append(KeyComboAction("Tab"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to Red Slider", 
    ["BRAILLE LINE:  'Red 0 % Slider'",
     "     VISIBLE:  'Red 0 % Slider', cursor=1",
     "SPEECH OUTPUT: 'Red slider 0 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Red 1. Right Arrow", 
    ["BUG? - Lots of unneeded braille updating here and in the assertions that follow for the Red slider. Just marking it here.",
     "BRAILLE LINE:  'Red 0 % Slider'",
     "     VISIBLE:  'Red 0 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 0 % Slider'",
     "     VISIBLE:  'Red 0 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 1 % Slider'",
     "     VISIBLE:  'Red 1 % Slider', cursor=1",
     "SPEECH OUTPUT: '1 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Red 2. Right Arrow", 
    ["BRAILLE LINE:  'Red 1 % Slider'",
     "     VISIBLE:  'Red 1 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 1 % Slider'",
     "     VISIBLE:  'Red 1 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 2 % Slider'",
     "     VISIBLE:  'Red 2 % Slider', cursor=1",
     "SPEECH OUTPUT: '2 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Red 3. Right Arrow", 
    ["BRAILLE LINE:  'Red 2 % Slider'",
     "     VISIBLE:  'Red 2 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 2 % Slider'",
     "     VISIBLE:  'Red 2 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 3 % Slider'",
     "     VISIBLE:  'Red 3 % Slider', cursor=1",
     "SPEECH OUTPUT: '3 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Red 1. Left Arrow", 
    ["BRAILLE LINE:  'Red 3 % Slider'",
     "     VISIBLE:  'Red 3 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 3 % Slider'",
     "     VISIBLE:  'Red 3 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 2 % Slider'",
     "     VISIBLE:  'Red 2 % Slider', cursor=1",
     "SPEECH OUTPUT: '2 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Red 2. Left Arrow", 
    ["BRAILLE LINE:  'Red 2 % Slider'",
     "     VISIBLE:  'Red 2 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 2 % Slider'",
     "     VISIBLE:  'Red 2 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 1 % Slider'",
     "     VISIBLE:  'Red 1 % Slider', cursor=1",
     "SPEECH OUTPUT: '1 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Red 3. Left Arrow", 
    ["BRAILLE LINE:  'Red 1 % Slider'",
     "     VISIBLE:  'Red 1 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 1 % Slider'",
     "     VISIBLE:  'Red 1 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 0 % Slider'",
     "     VISIBLE:  'Red 0 % Slider', cursor=1",
     "SPEECH OUTPUT: '0 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Red 1. Up Arrow", 
    ["BRAILLE LINE:  'Red 0 % Slider'",
     "     VISIBLE:  'Red 0 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 0 % Slider'",
     "     VISIBLE:  'Red 0 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 1 % Slider'",
     "     VISIBLE:  'Red 1 % Slider', cursor=1",
     "SPEECH OUTPUT: '1 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Red 2. Up Arrow", 
    ["BRAILLE LINE:  'Red 1 % Slider'",
     "     VISIBLE:  'Red 1 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 1 % Slider'",
     "     VISIBLE:  'Red 1 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 2 % Slider'",
     "     VISIBLE:  'Red 2 % Slider', cursor=1",
     "SPEECH OUTPUT: '2 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Red 3. Up Arrow", 
    ["BRAILLE LINE:  'Red 2 % Slider'",
     "     VISIBLE:  'Red 2 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 2 % Slider'",
     "     VISIBLE:  'Red 2 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 3 % Slider'",
     "     VISIBLE:  'Red 3 % Slider', cursor=1",
     "SPEECH OUTPUT: '3 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Red 1. Down Arrow", 
    ["BRAILLE LINE:  'Red 3 % Slider'",
     "     VISIBLE:  'Red 3 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 3 % Slider'",
     "     VISIBLE:  'Red 3 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 2 % Slider'",
     "     VISIBLE:  'Red 2 % Slider', cursor=1",
     "SPEECH OUTPUT: '2 %'"]))


sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Red 2. Down Arrow", 
    ["BRAILLE LINE:  'Red 2 % Slider'",
     "     VISIBLE:  'Red 2 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 2 % Slider'",
     "     VISIBLE:  'Red 2 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 1 % Slider'",
     "     VISIBLE:  'Red 1 % Slider', cursor=1",
     "SPEECH OUTPUT: '1 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Red 3. Down Arrow", 
    ["BRAILLE LINE:  'Red 1 % Slider'",
     "     VISIBLE:  'Red 1 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 1 % Slider'",
     "     VISIBLE:  'Red 1 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 0 % Slider'",
     "     VISIBLE:  'Red 0 % Slider', cursor=1",
     "SPEECH OUTPUT: '0 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Up"))
sequence.append(utils.AssertPresentationAction(
    "Red 1. Page Up", 
    ["BRAILLE LINE:  'Red 0 % Slider'",
     "     VISIBLE:  'Red 0 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 0 % Slider'",
     "     VISIBLE:  'Red 0 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 20 % Slider'",
     "     VISIBLE:  'Red 20 % Slider', cursor=1",
     "SPEECH OUTPUT: '20 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Up"))
sequence.append(utils.AssertPresentationAction(
    "Red 2. Page Up", 
    ["BRAILLE LINE:  'Red 20 % Slider'",
     "     VISIBLE:  'Red 20 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 20 % Slider'",
     "     VISIBLE:  'Red 20 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 40 % Slider'",
     "     VISIBLE:  'Red 40 % Slider', cursor=1",
     "SPEECH OUTPUT: '40 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "Red 1. Page Down", 
    ["BRAILLE LINE:  'Red 40 % Slider'",
     "     VISIBLE:  'Red 40 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 40 % Slider'",
     "     VISIBLE:  'Red 40 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 20 % Slider'",
     "     VISIBLE:  'Red 20 % Slider', cursor=1",
     "SPEECH OUTPUT: '20 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "Red 2. Page Down", 
    ["BRAILLE LINE:  'Red 20 % Slider'",
     "     VISIBLE:  'Red 20 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 20 % Slider'",
     "     VISIBLE:  'Red 20 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 0 % Slider'",
     "     VISIBLE:  'Red 0 % Slider', cursor=1",
     "SPEECH OUTPUT: '0 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("End"))
sequence.append(utils.AssertPresentationAction(
    "Red End", 
    ["BRAILLE LINE:  'Red 0 % Slider'",
     "     VISIBLE:  'Red 0 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 0 % Slider'",
     "     VISIBLE:  'Red 0 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 55 % Slider'",
     "     VISIBLE:  'Red 55 % Slider', cursor=1",
     "SPEECH OUTPUT: '55 %'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Home"))
sequence.append(utils.AssertPresentationAction(
    "Red Home", 
    ["BRAILLE LINE:  'Red 55 % Slider'",
     "     VISIBLE:  'Red 55 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 55 % Slider'",
     "     VISIBLE:  'Red 55 % Slider', cursor=1",
     "BRAILLE LINE:  'Red 0 % Slider'",
     "     VISIBLE:  'Red 0 % Slider', cursor=1",
     "SPEECH OUTPUT: '0 %'"]))

sequence.append(KeyComboAction("Tab"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to Green Slider", 
    ["BRAILLE LINE:  'Green 0 Slider'",
     "     VISIBLE:  'Green 0 Slider', cursor=1",
     "SPEECH OUTPUT: 'Green slider 0'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Green 1. Right Arrow", 
    ["BRAILLE LINE:  'Green 1 Slider'",
     "     VISIBLE:  'Green 1 Slider', cursor=1",
     "SPEECH OUTPUT: '1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Green 2. Right Arrow", 
    ["BRAILLE LINE:  'Green 2 Slider'",
     "     VISIBLE:  'Green 2 Slider', cursor=1",
     "SPEECH OUTPUT: '2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Green 3. Right Arrow", 
    ["BRAILLE LINE:  'Green 3 Slider'",
     "     VISIBLE:  'Green 3 Slider', cursor=1",
     "SPEECH OUTPUT: '3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Green 1. Left Arrow", 
    ["BRAILLE LINE:  'Green 2 Slider'",
     "     VISIBLE:  'Green 2 Slider', cursor=1",
     "SPEECH OUTPUT: '2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Green 2. Left Arrow", 
    ["BRAILLE LINE:  'Green 1 Slider'",
     "     VISIBLE:  'Green 1 Slider', cursor=1",
     "SPEECH OUTPUT: '1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Green 3. Left Arrow", 
    ["BRAILLE LINE:  'Green 0 Slider'",
     "     VISIBLE:  'Green 0 Slider', cursor=1",
     "SPEECH OUTPUT: '0'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Green 1. Up Arrow", 
    ["BRAILLE LINE:  'Green 1 Slider'",
     "     VISIBLE:  'Green 1 Slider', cursor=1",
     "SPEECH OUTPUT: '1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Green 2. Up Arrow", 
    ["BRAILLE LINE:  'Green 2 Slider'",
     "     VISIBLE:  'Green 2 Slider', cursor=1",
     "SPEECH OUTPUT: '2'"]))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Green 3. Up Arrow", 
    ["BRAILLE LINE:  'Green 3 Slider'",
     "     VISIBLE:  'Green 3 Slider', cursor=1",
     "SPEECH OUTPUT: '3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Green 1. Down Arrow", 
    ["BRAILLE LINE:  'Green 2 Slider'",
     "     VISIBLE:  'Green 2 Slider', cursor=1",
     "SPEECH OUTPUT: '2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Green 2. Down Arrow", 
    ["BRAILLE LINE:  'Green 1 Slider'",
     "     VISIBLE:  'Green 1 Slider', cursor=1",
     "SPEECH OUTPUT: '1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Green 3. Down Arrow", 
    ["BRAILLE LINE:  'Green 0 Slider'",
     "     VISIBLE:  'Green 0 Slider', cursor=1",
     "SPEECH OUTPUT: '0'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Up"))
sequence.append(utils.AssertPresentationAction(
    "Green 1. Page Up", 
    ["BRAILLE LINE:  'Green 64 Slider'",
     "     VISIBLE:  'Green 64 Slider', cursor=1",
     "SPEECH OUTPUT: '64'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Up"))
sequence.append(utils.AssertPresentationAction(
    "Green 2. Page Up", 
    ["BRAILLE LINE:  'Green 128 Slider'",
     "     VISIBLE:  'Green 128 Slider', cursor=1",
     "SPEECH OUTPUT: '128'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "Green 1. Page Down", 
    ["BRAILLE LINE:  'Green 64 Slider'",
     "     VISIBLE:  'Green 64 Slider', cursor=1",
     "SPEECH OUTPUT: '64'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "Green 2. Page Down", 
    ["BRAILLE LINE:  'Green 0 Slider'",
     "     VISIBLE:  'Green 0 Slider', cursor=1",
     "SPEECH OUTPUT: '0'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("End"))
sequence.append(utils.AssertPresentationAction(
    "Green End", 
    ["BRAILLE LINE:  'Green 255 Slider'",
     "     VISIBLE:  'Green 255 Slider', cursor=1",
     "SPEECH OUTPUT: '255'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Home"))
sequence.append(utils.AssertPresentationAction(
    "Green Home", 
    ["BRAILLE LINE:  'Green 0 Slider'",
     "     VISIBLE:  'Green 0 Slider', cursor=1",
     "SPEECH OUTPUT: '0'"]))

sequence.append(KeyComboAction("Tab"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to Blue Slider", 
    ["BRAILLE LINE:  'Blue 0 Slider'",
     "     VISIBLE:  'Blue 0 Slider', cursor=1",
     "SPEECH OUTPUT: 'Blue slider 0'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Blue 1. Right Arrow", 
    ["BRAILLE LINE:  'Blue 1 Slider'",
     "     VISIBLE:  'Blue 1 Slider', cursor=1",
     "SPEECH OUTPUT: '1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Blue 2. Right Arrow", 
    ["BRAILLE LINE:  'Blue 2 Slider'",
     "     VISIBLE:  'Blue 2 Slider', cursor=1",
     "SPEECH OUTPUT: '2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Blue 3. Right Arrow", 
    ["BRAILLE LINE:  'Blue 3 Slider'",
     "     VISIBLE:  'Blue 3 Slider', cursor=1",
     "SPEECH OUTPUT: '3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Blue 1. Left Arrow", 
    ["BRAILLE LINE:  'Blue 2 Slider'",
     "     VISIBLE:  'Blue 2 Slider', cursor=1",
     "SPEECH OUTPUT: '2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Blue 2. Left Arrow", 
    ["BRAILLE LINE:  'Blue 1 Slider'",
     "     VISIBLE:  'Blue 1 Slider', cursor=1",
     "SPEECH OUTPUT: '1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Blue 3. Left Arrow", 
    ["BRAILLE LINE:  'Blue 0 Slider'",
     "     VISIBLE:  'Blue 0 Slider', cursor=1",
     "SPEECH OUTPUT: '0'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Blue 1. Up Arrow", 
    ["BRAILLE LINE:  'Blue 1 Slider'",
     "     VISIBLE:  'Blue 1 Slider', cursor=1",
     "SPEECH OUTPUT: '1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Blue 2. Up Arrow", 
    ["BRAILLE LINE:  'Blue 2 Slider'",
     "     VISIBLE:  'Blue 2 Slider', cursor=1",
     "SPEECH OUTPUT: '2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Blue 3. Up Arrow", 
    ["BRAILLE LINE:  'Blue 3 Slider'",
     "     VISIBLE:  'Blue 3 Slider', cursor=1",
     "SPEECH OUTPUT: '3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Blue 1. Down Arrow", 
    ["BRAILLE LINE:  'Blue 2 Slider'",
     "     VISIBLE:  'Blue 2 Slider', cursor=1",
     "SPEECH OUTPUT: '2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Blue 2. Down Arrow", 
    ["BRAILLE LINE:  'Blue 1 Slider'",
     "     VISIBLE:  'Blue 1 Slider', cursor=1",
     "SPEECH OUTPUT: '1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Blue 3. Down Arrow", 
    ["BRAILLE LINE:  'Blue 0 Slider'",
     "     VISIBLE:  'Blue 0 Slider', cursor=1",
     "SPEECH OUTPUT: '0'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Up"))
sequence.append(utils.AssertPresentationAction(
    "Blue 1. Page Up", 
    ["BRAILLE LINE:  'Blue 64 Slider'",
     "     VISIBLE:  'Blue 64 Slider', cursor=1",
     "SPEECH OUTPUT: '64'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Up"))
sequence.append(utils.AssertPresentationAction(
    "Blue 2. Page Up", 
    ["BRAILLE LINE:  'Blue 128 Slider'",
     "     VISIBLE:  'Blue 128 Slider', cursor=1",
     "SPEECH OUTPUT: '128'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "Blue 1. Page Down", 
    ["BRAILLE LINE:  'Blue 64 Slider'",
     "     VISIBLE:  'Blue 64 Slider', cursor=1",
     "SPEECH OUTPUT: '64'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "Blue 2. Page Down", 
    ["BRAILLE LINE:  'Blue 0 Slider'",
     "     VISIBLE:  'Blue 0 Slider', cursor=1",
     "SPEECH OUTPUT: '0'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("End"))
sequence.append(utils.AssertPresentationAction(
    "Blue End", 
    ["BRAILLE LINE:  'Blue 255 Slider'",
     "     VISIBLE:  'Blue 255 Slider', cursor=1",
     "SPEECH OUTPUT: '255'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Home"))
sequence.append(utils.AssertPresentationAction(
    "Blue Home", 
    ["BRAILLE LINE:  'Blue 0 Slider'",
     "     VISIBLE:  'Blue 0 Slider', cursor=1",
     "SPEECH OUTPUT: '0'"]))

sequence.append(KeyComboAction("Tab"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to Vertical Slider", 
    ["BRAILLE LINE:  'Minimum Filesize 0 units Slider'",
     "     VISIBLE:  'Minimum Filesize 0 units Slider', cursor=1",
     "SPEECH OUTPUT: 'Minimum Filesize slider 0 units'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Vertical 1. Right Arrow", 
    ["BRAILLE LINE:  'Minimum Filesize 1 units Slider'",
     "     VISIBLE:  'Minimum Filesize 1 units Slider', cursor=1",
     "SPEECH OUTPUT: '1 units'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Vertical 2. Right Arrow", 
    ["BRAILLE LINE:  'Minimum Filesize 2 units Slider'",
     "     VISIBLE:  'Minimum Filesize 2 units Slider', cursor=1",
     "SPEECH OUTPUT: '2 units'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Vertical 3. Right Arrow", 
    ["BRAILLE LINE:  'Minimum Filesize 3 units Slider'",
     "     VISIBLE:  'Minimum Filesize 3 units Slider', cursor=1",
     "SPEECH OUTPUT: '3 units'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Vertical 1. Left Arrow", 
    ["BRAILLE LINE:  'Minimum Filesize 2 units Slider'",
     "     VISIBLE:  'Minimum Filesize 2 units Slider', cursor=1",
     "SPEECH OUTPUT: '2 units'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Vertical 2. Left Arrow", 
    ["BRAILLE LINE:  'Minimum Filesize 1 units Slider'",
     "     VISIBLE:  'Minimum Filesize 1 units Slider', cursor=1",
     "SPEECH OUTPUT: '1 units'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Vertical 3. Left Arrow", 
    ["BRAILLE LINE:  'Minimum Filesize 0 units Slider'",
     "     VISIBLE:  'Minimum Filesize 0 units Slider', cursor=1",
     "SPEECH OUTPUT: '0 units'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Vertical 1. Down Arrow", 
    ["BRAILLE LINE:  'Minimum Filesize 1 units Slider'",
     "     VISIBLE:  'Minimum Filesize 1 units Slider', cursor=1",
     "SPEECH OUTPUT: '1 units'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Vertical 2. Down Arrow", 
    ["BRAILLE LINE:  'Minimum Filesize 2 units Slider'",
     "     VISIBLE:  'Minimum Filesize 2 units Slider', cursor=1",
     "SPEECH OUTPUT: '2 units'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Vertical 3. Down Arrow", 
    ["BRAILLE LINE:  'Minimum Filesize 3 units Slider'",
     "     VISIBLE:  'Minimum Filesize 3 units Slider', cursor=1",
     "SPEECH OUTPUT: '3 units'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Vertical 1. Up Arrow", 
    ["BRAILLE LINE:  'Minimum Filesize 2 units Slider'",
     "     VISIBLE:  'Minimum Filesize 2 units Slider', cursor=1",
     "SPEECH OUTPUT: '2 units'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Vertical 2. Up Arrow", 
    ["BRAILLE LINE:  'Minimum Filesize 1 units Slider'",
     "     VISIBLE:  'Minimum Filesize 1 units Slider', cursor=1",
     "SPEECH OUTPUT: '1 units'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Vertical 3. Up Arrow", 
    ["BRAILLE LINE:  'Minimum Filesize 0 units Slider'",
     "     VISIBLE:  'Minimum Filesize 0 units Slider', cursor=1",
     "SPEECH OUTPUT: '0 units'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Up"))
sequence.append(utils.AssertPresentationAction(
    "Vertical 1. Page Up", 
    ["BRAILLE LINE:  'Minimum Filesize 64 units Slider'",
     "     VISIBLE:  'Minimum Filesize 64 units Slider', cursor=1",
     "SPEECH OUTPUT: '64 units'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Up"))
sequence.append(utils.AssertPresentationAction(
    "Vertical 2. Page Up", 
    ["BRAILLE LINE:  'Minimum Filesize 128 units Slider'",
     "     VISIBLE:  'Minimum Filesize 128 units Slide', cursor=1",
     "SPEECH OUTPUT: '128 units'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "Vertical 1. Page Down", 
    ["BRAILLE LINE:  'Minimum Filesize 64 units Slider'",
     "     VISIBLE:  'Minimum Filesize 64 units Slider', cursor=1",
     "SPEECH OUTPUT: '64 units'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "Vertical 2. Page Down", 
    ["BRAILLE LINE:  'Minimum Filesize 0 units Slider'",
     "     VISIBLE:  'Minimum Filesize 0 units Slider', cursor=1",
     "SPEECH OUTPUT: '0 units'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("End"))
sequence.append(utils.AssertPresentationAction(
    "Vertical End", 
    ["BRAILLE LINE:  'Minimum Filesize 255 units Slider'",
     "     VISIBLE:  'Minimum Filesize 255 units Slide', cursor=1",
     "SPEECH OUTPUT: '255 units'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Home"))
sequence.append(utils.AssertPresentationAction(
    "Vertical Home", 
    ["BUG? - This is the same as End.",
     "BRAILLE LINE:  'Minimum Filesize 255 units Slider'",
     "     VISIBLE:  'Minimum Filesize 255 units Slide', cursor=1",
     "SPEECH OUTPUT: 'Minimum Filesize slider 255 units'"]))

########################################################################
# Close the demo
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
