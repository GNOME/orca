# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of Dojo combo box presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "Dojo Spinner Widget Test" frame.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the dojo spinner demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction(utils.DojoNightlyURLPrefix + "form/_autoComplete.html?testWidget=dijit.form.ComboBox"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("dijit.form.ComboBox Unit Test", 
                              acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Extra loading time.
#
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

########################################################################
# Tab to the first combo box
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to the first combo box", 
    ["BRAILLE LINE:  '▼ US State test 1 (200% Courier font): California (CA) $l'",
     "     VISIBLE:  '▼ US State test 1 (200% Courier ', cursor=0",
     "SPEECH OUTPUT: 'US State test 1 (200% Courier font): combo box US State test 1 (200% Courier font): text California (CA) selected'"]))

########################################################################
# Replace all the text (already selected) with a 'C'.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("C"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "Replace existing text with a 'C'", 
    ["BUG? - At this point, the entry expands into a combo box with three items showing. We speak them all. We should instead indicate that this object is expanded, similar to what we do with autocompletes.",
     "BRAILLE LINE:  '▼ US State test 1 (200% Courier font): C $l'",
     "     VISIBLE:  '▼ US State test 1 (200% Courier ', cursor=0",
     "BRAILLE LINE:  '▼ US State test 1 (200% Courier font): C $l'",
     "     VISIBLE:  '▼ US State test 1 (200% Courier ', cursor=0",
     "BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: 'California (CA)Colorado (CO)Connecticut (CT)'"]))

########################################################################
# Down Arrow amongst the newly-displayed items. One should not be able
# to arrow out of the combo box.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Down Arrow", 
    ["BUG? - What's with all the braille updating?!?",
     "BRAILLE LINE:  '▼ US State test 1 (200% Courier font): C $l'",
     "     VISIBLE:  '▼ US State test 1 (200% Courier ', cursor=0",
     "BRAILLE LINE:  '▼ US State test 1 (200% Courier font): California (CA) $l'",
     "     VISIBLE:  '▼ US State test 1 (200% Courier ', cursor=0",
     "BRAILLE LINE:  '▼ US State test 1 (200% Courier font): California (CA) $l'",
     "     VISIBLE:  '▼ US State test 1 (200% Courier ', cursor=0",
     "BRAILLE LINE:  '▼ US State test 1 (200% Courier font): California (CA) $l'",
     "     VISIBLE:  '▼ US State test 1 (200% Courier ', cursor=0",
     "BRAILLE LINE:  '▼ US State test 1 (200% Courier font): California (CA) $l'",
     "     VISIBLE:  '▼ US State test 1 (200% Courier ', cursor=0",
     "BRAILLE LINE:  'California (CA)'",
     "     VISIBLE:  'California (CA)', cursor=1",
     "SPEECH OUTPUT: 'California (CA)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down Arrow", 
    ["BRAILLE LINE:  'Colorado (CO)'",
     "     VISIBLE:  'Colorado (CO)', cursor=1",
     "SPEECH OUTPUT: 'Colorado (CO)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Down Arrow", 
    ["BRAILLE LINE:  'Connecticut (CT)'",
     "     VISIBLE:  'Connecticut (CT)', cursor=1",
     "SPEECH OUTPUT: 'Connecticut (CT)'"]))

# Note that not saying anything here is correct because we're already at
# the end of the expanded combo box thus pressing Down doesn't move us.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Down Arrow", 
    ["BRAILLE LINE:  'California (CA)'",
     "     VISIBLE:  'California (CA)', cursor=1",
     "SPEECH OUTPUT: 'California (CA)'"]))

########################################################################
# Up Arrow amongst the newly-displayed items. One should not be able
# to arrow out of the combo box.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "1. Up Arrow", 
    ["BRAILLE LINE:  'Connecticut (CT)'",
     "     VISIBLE:  'Connecticut (CT)', cursor=1",
     "SPEECH OUTPUT: 'Connecticut (CT)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "2. Up Arrow", 
    ["BRAILLE LINE:  'Colorado (CO)'",
     "     VISIBLE:  'Colorado (CO)', cursor=1",
     "SPEECH OUTPUT: 'Colorado (CO)'"]))

# Note that not saying anything here is correct because we're already at
# the top of the expanded combo box thus pressing Up doesn't move us.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "3. Up Arrow", 
    ["BRAILLE LINE:  'California (CA)'",
     "     VISIBLE:  'California (CA)', cursor=1",
     "SPEECH OUTPUT: 'California (CA)'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I - Combo box expanded", 
    ["BRAILLE LINE:  'California (CA)'",
     "     VISIBLE:  'California (CA)', cursor=1",
     "SPEECH OUTPUT: 'list item California (CA) 1 of 3'"]))

########################################################################
# Escape to collapse the combo box.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Escape"))
sequence.append(utils.AssertPresentationAction(
    "Escape", 
    ["BRAILLE LINE:  '▼ US State test 1 (200% Courier font): C $l'",
     "     VISIBLE:  '▼ US State test 1 (200% Courier ', cursor=0",
     "SPEECH OUTPUT: 'US State test 1 (200% Courier font): combo box US State test 1 (200% Courier font): text C'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I - Combo box collapsed back into an entry", 
    ["BRAILLE LINE:  '▼ US State test 1 (200% Courier font): C $l'",
     "     VISIBLE:  '▼ US State test 1 (200% Courier ', cursor=0",
     "SPEECH OUTPUT: 'US State test 1 (200% Courier font): text C'"]))

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
