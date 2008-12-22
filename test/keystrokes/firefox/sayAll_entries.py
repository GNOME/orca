# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of sayAll output in Firefox on a page with a bunch of entries
contained in a variety of hierarchies."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the local "simple form" test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "entries.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

sequence.append(WaitForFocus("",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file",
    ["BRAILLE LINE:  'Here are some entries h2'",
     "     VISIBLE:  'Here are some entries h2', cursor=1",
     "SPEECH OUTPUT: 'Here are some entries heading level 2'"]))

########################################################################
# SayAll to the End.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "KP_Add to do a SayAll",
    ["SPEECH OUTPUT: 'Here are some entries heading level 2'",
     "SPEECH OUTPUT: 'Type something link  rather amusing link  here: text'",
     "SPEECH OUTPUT: 'Amusing numbers fall between text  and text .'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'I'm a label'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'Am I a label as well?'",
     "SPEECH OUTPUT: 'What the heck should we do here? heading level 2'",
     "SPEECH OUTPUT: 'Looking at what follows visually, I'm not sure what I would type/i.e. what the labels are.'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'Too far away to be a label.'",
     "SPEECH OUTPUT: 'Distance doesn't count on the left'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'Sometimes labels can be below the fields due to <br /> heading level 2'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: '",
     "First Name'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: '",
     "M.I.'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: '",
     "Last Name'",
     "SPEECH OUTPUT: 'Other times it's due to layout tables heading level 2'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'First name'",
     "SPEECH OUTPUT: 'Middle",
     "initial'",
     "SPEECH OUTPUT: 'Last name link'",
     "SPEECH OUTPUT: 'Second verse same as the first (only now the labels are above the fields) heading level 2'",
     "SPEECH OUTPUT: 'First Name'",
     "SPEECH OUTPUT: 'Middle",
     "initial'",
     "SPEECH OUTPUT: 'Last name link'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'Decisions, decisions.... When in doubt, closest table cell text wins heading level 2'",
     "SPEECH OUTPUT: 'First name'",
     "SPEECH OUTPUT: 'Middle",
     "initial'",
     "SPEECH OUTPUT: 'Last name'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'Given name'",
     "SPEECH OUTPUT: 'initial'",
     "SPEECH OUTPUT: 'Surname'",
     "SPEECH OUTPUT: 'First name'",
     "SPEECH OUTPUT: 'Middle",
     "initial'",
     "SPEECH OUTPUT: 'Last name'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'Given name'",
     "SPEECH OUTPUT: 'initial'",
     "SPEECH OUTPUT: 'Surname'",
     "SPEECH OUTPUT: 'Decisions, decisions.... We should try to figure out if we're in a grid of fields. heading level 2'",
     "SPEECH OUTPUT: 'First name'",
     "SPEECH OUTPUT: 'Middle",
     "initial'",
     "SPEECH OUTPUT: 'Last name'",
     "SPEECH OUTPUT: 'patched image image'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'We mustn't forget images as labels -- even if that practice is lame heading level 2'",
     "SPEECH OUTPUT: 'bandaid graphic image'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'bandaid graphic redux image'",
     "SPEECH OUTPUT: 'Magic disappearing text trick: text tab to me and I disappear'",
     "SPEECH OUTPUT: 'Tell me a secret: password'",
     "SPEECH OUTPUT: 'Tell me a little more about yourself:",
     " text and plan to write my memoirs.'"]))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
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
