#!/usr/bin/python

"""Test of debug commands.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))

########################################################################
# Once gtk-demo is running, run through some debugging commands.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("<Control><Alt>Home"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Report script information",
    ["BRAILLE LINE:  'SCRIPT INFO: Script name='gtk-demo [(]module=orca.scripts.toolkits.GAIL[)]' Application name='gtk-demo' Toolkit name='GAIL' Version='[0-9]+[.][0-9]+[.][0-9]+''",
     "     VISIBLE:  'SCRIPT INFO: Script name='gtk-de', cursor=0",
     "SPEECH OUTPUT: 'SCRIPT INFO: Script name='gtk-demo [(]module=orca.scripts.toolkits.GAIL[)]' Application name='gtk-demo' Toolkit name='GAIL' Version='[0-9]+[.][0-9]+[.][0-9]+'' voice=system"]))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
