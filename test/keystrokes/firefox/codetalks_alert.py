#!/usr/bin/python

"""Test of Codetalks alert test presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "text/html: Button Example 1" frame.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the Codetalks alert demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://codetalks.org/source/widgets/alert/alert.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Accessible DHTML Alerts", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# A little extra time for slow loading.
#
sequence.append(PauseAction(3000))

########################################################################
# Tab to the "Show (via display style) and put focus insert alert (on
# link)" button. Then press that button
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Create and Focus", acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Create - no Focus", acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Show (via visibility style) and Focus", acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Show (via visibility style) - no Focus", acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Show (via display style) and Focus", acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Show (via display style) - no Focus", acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Show (via display style) and put focus inside alert (on link)", acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "Press button", 
    ["KNOWN ISSUE - A focus event went missing: https://bugzilla.mozilla.org/show_bug.cgi?id=579964",
     "BRAILLE LINE:  'close'",
     "     VISIBLE:  'close', cursor=1",
     "SPEECH OUTPUT: 'close link'",
     "SPEECH OUTPUT: 'This popup is created as a div in the HTML content, rather than being created in the DOM at the time of use. The display style is changed from \"none\" to \"block\" to hide and show it. close'"]))

########################################################################
# Up Arrow from the link at the bottom to review the text.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "1. Up Arrow", 
    ["KNOWN ISSUE - A focus event went missing: https://bugzilla.mozilla.org/show_bug.cgi?id=579964",
     "BRAILLE LINE:  '\"none\" to \"block\" to hide and show it.'",
     "     VISIBLE:  '\"none\" to \"block\" to hide and sh', cursor=1",
     "SPEECH OUTPUT: '\"none\" to \"block\" to hide and show it. alert'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "2. Up Arrow", 
    ["KNOWN ISSUE - A focus event went missing: https://bugzilla.mozilla.org/show_bug.cgi?id=579964",
     "BRAILLE LINE:  'the time of use. The display style is changed from'",
     "     VISIBLE:  'the time of use. The display sty', cursor=1",
     "SPEECH OUTPUT: 'the time of use. The display style is changed from alert'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "3. Up Arrow", 
    ["KNOWN ISSUE - A focus event went missing: https://bugzilla.mozilla.org/show_bug.cgi?id=579964",
     "BRAILLE LINE:  'content, rather than being created in the DOM at'",
     "     VISIBLE:  'content, rather than being creat', cursor=1",
     "SPEECH OUTPUT: 'content, rather than being created in the DOM at alert'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Up Arrow", 
    ["KNOWN ISSUE - A focus event went missing: https://bugzilla.mozilla.org/show_bug.cgi?id=579964",
     "BRAILLE LINE:  'This popup is created as a div in the HTML'",
     "     VISIBLE:  'This popup is created as a div i', cursor=1",
     "SPEECH OUTPUT: 'This popup is created as a div in the HTML alert'"]))

########################################################################
# Down Arrow from the top to review the text.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Down Arrow", 
    ["KNOWN ISSUE - A focus event went missing: https://bugzilla.mozilla.org/show_bug.cgi?id=579964",
     "BRAILLE LINE:  'content, rather than being created in the DOM at'",
     "     VISIBLE:  'content, rather than being creat', cursor=1",
     "SPEECH OUTPUT: 'content, rather than being created in the DOM at alert'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down Arrow", 
    ["KNOWN ISSUE - A focus event went missing: https://bugzilla.mozilla.org/show_bug.cgi?id=579964",
     "BRAILLE LINE:  'the time of use. The display style is changed from'",
     "     VISIBLE:  'the time of use. The display sty', cursor=1",
     "SPEECH OUTPUT: 'the time of use. The display style is changed from alert'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Down Arrow", 
    ["KNOWN ISSUE - A focus event went missing: https://bugzilla.mozilla.org/show_bug.cgi?id=579964",
     "BRAILLE LINE:  '\"none\" to \"block\" to hide and show it.'",
     "     VISIBLE:  '\"none\" to \"block\" to hide and sh', cursor=1",
     "SPEECH OUTPUT: '\"none\" to \"block\" to hide and show it. alert'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Down Arrow", 
    ["KNOWN ISSUE - A focus event went missing: https://bugzilla.mozilla.org/show_bug.cgi?id=579964",
     "BRAILLE LINE:  'close'",
     "     VISIBLE:  'close', cursor=1",
     "SPEECH OUTPUT: 'close link'"]))

########################################################################
# Press Return on the 'close' link to dismiss the alert.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "Return on close link", 
    [""]))

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
