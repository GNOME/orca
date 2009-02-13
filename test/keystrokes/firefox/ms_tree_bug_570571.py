# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of Orca's interaction with the Microsoft ARIA tree example. In
It's current format, it's rather wacky. See bug 570571."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "TreeViewFrame" frame.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the editor test demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://samples.msdn.microsoft.com/ietestcenter/Aria/samples/tree/ariatree.htm"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("TreeViewFrame", 
                              acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Tab to the first tree item and expand it.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to Colors", 
    ["BRAILLE LINE:  '+Colors ListItem'",
     "     VISIBLE:  '+Colors ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: '+Colors collapsed'",
     "SPEECH OUTPUT: 'tree level 1'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "basic whereAmI", 
    ["BUG? - There are visually two items here, but we say this is 1 of 1",
     "BRAILLE LINE:  '+Colors ListItem'",
     "     VISIBLE:  '+Colors ListItem', cursor=1",
     "SPEECH OUTPUT: 'list item'",
     "SPEECH OUTPUT: '+Colors'",
     "SPEECH OUTPUT: 'item 1 of 1'",
     "SPEECH OUTPUT: 'collapsed'",
     "SPEECH OUTPUT: 'tree level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Expand Colors", 
    ["BRAILLE LINE:  '+Colors ListItem'",
     "     VISIBLE:  '+Colors ListItem', cursor=1",
     "BRAILLE LINE:  '-Colors ListItem'",
     "     VISIBLE:  '-Colors ListItem', cursor=1",
     "BRAILLE LINE:  '-Colors ListItem'",
     "     VISIBLE:  '-Colors ListItem', cursor=1",
     "SPEECH OUTPUT: 'expanded'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "basic whereAmI", 
    ["BRAILLE LINE:  '-Colors ListItem'",
     "     VISIBLE:  '-Colors ListItem', cursor=1",
     "SPEECH OUTPUT: 'list item'",
     "SPEECH OUTPUT: '-Colors'",
     "SPEECH OUTPUT: 'item 1 of 2'",
     "SPEECH OUTPUT: 'expanded'",
     "SPEECH OUTPUT: 'tree level 1'"]))

########################################################################
# Down Arrow. Independent of Orca, the first item claims focus as one
# would expect. However the second item then claims focus. Who knows
# why. But we present both (as expected).
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Down Arrow", 
    ["BRAILLE LINE:  'Red ListItem'",
     "     VISIBLE:  'Red ListItem', cursor=1",
     "BRAILLE LINE:  'Blue ListItem'",
     "     VISIBLE:  'Blue ListItem', cursor=1",
     "SPEECH OUTPUT: 'main colors panel'",
     "SPEECH OUTPUT: 'Red'",
     "SPEECH OUTPUT: 'tree level 2'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Blue'"]))

########################################################################
# Up Arrow to the first tree item and collaspe it.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Up Arrow to Colors", 
    ["BRAILLE LINE:  'Red ListItem'",
     "     VISIBLE:  'Red ListItem', cursor=1",
     "BRAILLE LINE:  '-Colors ListItem'",
     "     VISIBLE:  '-Colors ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Red'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: '-Colors expanded'",
     "SPEECH OUTPUT: 'tree level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Collapse Colors", 
    ["BRAILLE LINE:  '-Colors ListItem'",
     "     VISIBLE:  '-Colors ListItem', cursor=1",
     "BRAILLE LINE:  '+Colors ListItem'",
     "     VISIBLE:  '+Colors ListItem', cursor=1",
     "BRAILLE LINE:  '+Colors ListItem'",
     "     VISIBLE:  '+Colors ListItem', cursor=1",
     "SPEECH OUTPUT: 'collapsed'"]))

########################################################################
# Tab to the second tree item and expand it.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to Animals", 
    ["BRAILLE LINE:  '+Animals ListItem'",
     "     VISIBLE:  '+Animals ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: '+Animals collapsed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Expand Animals", 
    ["BRAILLE LINE:  '+Animals ListItem'",
     "     VISIBLE:  '+Animals ListItem', cursor=1",
     "BRAILLE LINE:  '-Animals ListItem'",
     "     VISIBLE:  '-Animals ListItem', cursor=1",
     "BRAILLE LINE:  '-Animals ListItem'",
     "     VISIBLE:  '-Animals ListItem', cursor=1",
     "SPEECH OUTPUT: 'expanded'"]))

########################################################################
# Down Arrow. Independent of Orca, the first item claims focus as one
# would expect. However the second item then claims focus. Who knows
# why. But we present both (as expected).
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Down Arrow",
    ["BRAILLE LINE:  'Dog ListItem'",
     "     VISIBLE:  'Dog ListItem', cursor=1",
     "BRAILLE LINE:  'Cat ListItem'",
     "     VISIBLE:  'Cat ListItem', cursor=1",
     "SPEECH OUTPUT: 'animals panel'",
     "SPEECH OUTPUT: 'Dog'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Cat'"]))

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
