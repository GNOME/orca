# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of presentation of Codetalk's list using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://codetalks.org/source/enhanced-html-forms/list.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

sequence.append(PauseAction(5000))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file",
    ["BRAILLE LINE:  'Here is a static list of div elements with role 'listitem', and they sit inside a div with role 'list'. The divs contain text: dog, cat, sparrow, wolf! and begin here:'",
     "     VISIBLE:  'Here is a static list of div ele', cursor=1",
     "SPEECH OUTPUT: 'Here is a static list of div elements with role 'listitem', and they sit inside a div with role 'list'. The divs contain text: dog, cat, sparrow, wolf! and begin here: ",
     "'"]))

########################################################################
# Down Arrow.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Down Arrow", 
    ["BRAILLE LINE:  'dog'",
     "     VISIBLE:  'dog', cursor=1",
     "SPEECH OUTPUT: 'dog list item'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down Arrow", 
    ["BRAILLE LINE:  'cat'",
     "     VISIBLE:  'cat', cursor=1",
     "SPEECH OUTPUT: 'cat list item'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Down Arrow", 
    ["BRAILLE LINE:  'sparrow'",
     "     VISIBLE:  'sparrow', cursor=1",
     "SPEECH OUTPUT: 'sparrow list item'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Down Arrow", 
    ["BRAILLE LINE:  'wolf!'",
     "     VISIBLE:  'wolf!', cursor=1",
     "SPEECH OUTPUT: 'wolf! list item'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Down Arrow", 
    ["BRAILLE LINE:  '\$Revision: [0-9]* \$'",
     "     VISIBLE:  '\$Revision: [0-9]* \$', cursor=1",
     "SPEECH OUTPUT: '\$Revision: [0-9]* dollar'"]))

########################################################################
# Up Arrow.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "1. Up Arrow", 
    ["BRAILLE LINE:  'wolf!'",
     "     VISIBLE:  'wolf!', cursor=1",
     "SPEECH OUTPUT: 'wolf! list item'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "2. Up Arrow", 
    ["BRAILLE LINE:  'sparrow'",
     "     VISIBLE:  'sparrow', cursor=1",
     "SPEECH OUTPUT: 'sparrow list item'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "3. Up Arrow", 
    ["BRAILLE LINE:  'cat'",
     "     VISIBLE:  'cat', cursor=1",
     "SPEECH OUTPUT: 'cat list item'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Up Arrow", 
    ["BRAILLE LINE:  'dog'",
     "     VISIBLE:  'dog', cursor=1",
     "SPEECH OUTPUT: 'dog list item'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "5. Up Arrow", 
    ["BRAILLE LINE:  'Here is a static list of div elements with role 'listitem', and they sit inside a div with role 'list'. The divs contain text: dog, cat, sparrow, wolf! and begin here:'",
     "     VISIBLE:  'Here is a static list of div ele', cursor=1",
     "SPEECH OUTPUT: 'Here is a static list of div elements with role 'listitem', and they sit inside a div with role 'list'. The divs contain text: dog, cat, sparrow, wolf! and begin here: ",
     "'"]))

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
