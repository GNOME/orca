#!/usr/bin/python

"""Test of menus in Java's SwingSet2."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

##########################################################################
# We wait for the demo to come up and for focus to be on the toggle button
#
#sequence.append(WaitForWindowActivate("SwingSet2",None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))

# Wait for entire window to get populated.
sequence.append(PauseAction(5000))

# Hack to deal with a timing issue which seems to interfere with our
# setting the locusOfFocus reliably.
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))

##########################################################################
# Open File menu
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("File", acc_role=pyatspi.ROLE_MENU))
sequence.append(utils.AssertPresentationAction(
    "1. Open File menu",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane File Menu'",
     "     VISIBLE:  'File Menu', cursor=1",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane File Menu'",
     "     VISIBLE:  'File Menu', cursor=1",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane PopupMenu About'",
     "     VISIBLE:  'About', cursor=1",
     "SPEECH OUTPUT: 'Swing demo menu bar menu bar File menu'",
     "SPEECH OUTPUT: 'About'"]))

########################################################################
# Basic Where Am I
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "2. Basic Where Am I",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane PopupMenu About'",
     "     VISIBLE:  'About', cursor=1",
     "SPEECH OUTPUT: 'SwingSet2 application SwingSet2 frame About 1 of 5.'",
     "SPEECH OUTPUT: 'B'",
     "SPEECH OUTPUT: 'Find out about the SwingSet2 application'"]))

##########################################################################
# Move to Look & Feel menu
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Look & Feel", acc_role=pyatspi.ROLE_MENU))
sequence.append(utils.AssertPresentationAction(
    "3. Move to Look & Feel menu",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Look & Feel Menu'",
     "     VISIBLE:  'Look & Feel Menu', cursor=1",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Look & Feel Menu'",
     "     VISIBLE:  'Look & Feel Menu', cursor=1",
     "SPEECH OUTPUT: 'Swing demo menu bar menu bar Look & Feel menu'"]))

########################################################################
# Basic Where Am I
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "4. Basic Where Am I",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Look & Feel Menu'",
     "     VISIBLE:  'Look & Feel Menu', cursor=1",
     "SPEECH OUTPUT: 'SwingSet2 application SwingSet2 frame Swing demo menu bar menu bar Look & Feel menu 2 of 5.'",
     "SPEECH OUTPUT: 'L'",
     "SPEECH OUTPUT: 'Menu that allows Look & Feel switching'"]))

##########################################################################
# Move to Themes menu
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Themes", acc_role=pyatspi.ROLE_MENU))
sequence.append(utils.AssertPresentationAction(
    "5. Move to Themes menu",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Look & Feel Menu'",
     "     VISIBLE:  'Look & Feel Menu', cursor=1",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Themes Menu'",
     "     VISIBLE:  'Themes Menu', cursor=1",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Themes Menu'",
     "     VISIBLE:  'Themes Menu', cursor=1",
     "SPEECH OUTPUT: 'Themes menu'"]))

########################################################################
# Basic Where Am I
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "6. Basic Where Am I",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Themes Menu'",
     "     VISIBLE:  'Themes Menu', cursor=1",
     "SPEECH OUTPUT: 'SwingSet2 application SwingSet2 frame Swing demo menu bar menu bar Themes menu 3 of 5.'",
     "SPEECH OUTPUT: 'T'",
     "SPEECH OUTPUT: 'Menu to switch Metal color themes'"]))

##########################################################################
# Move to Audio menu
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Audio", acc_role=pyatspi.ROLE_MENU))
sequence.append(utils.AssertPresentationAction(
    "7. Move to Audio menu",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar Audio Menu'",
     "     VISIBLE:  'Audio Menu', cursor=1",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar Audio Menu'",
     "     VISIBLE:  'Audio Menu', cursor=1",
     "SPEECH OUTPUT: 'Audio menu'"]))

########################################################################
# Basic Where Am I
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "8. Basic Where Am I",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar Audio Menu'",
     "     VISIBLE:  'Audio Menu', cursor=1",
     "SPEECH OUTPUT: 'SwingSet2 application SwingSet2 frame Swing demo menu bar menu bar Themes menu Audio menu 1 of 9.'",
     "SPEECH OUTPUT: 'A'",
     "SPEECH OUTPUT: 'Menu to switch the amount of auditory feedback available within the Java look and feel'"]))

# Leave menus.
sequence.append(KeyComboAction("Escape"))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
