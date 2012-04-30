#!/usr/bin/python

"""Plays Insert+q and then Alt+q to quit Orca."""

from macaroon.playback import *

sequence = MacroSequence()


sequence.append(KeyPressAction       (    0, 106, "Insert")) # Press Insert
sequence.append(KeyPressAction       (  168,  24, "q")) # Press q
sequence.append(KeyReleaseAction     (  151,  24, "q")) # Release q
sequence.append(KeyReleaseAction     (   48, 106, "Insert")) # Release Insert

sequence.append(WaitForFocus("Cancel", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("<Alt>q"))

sequence.start()
