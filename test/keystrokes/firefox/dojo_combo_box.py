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

########################################################################
# Tab to the first combo box
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to the first combo box", 
    ["BRAILLE LINE:  '  US State test 1 California $l'",
     "     VISIBLE:  '  US State test 1 California $l', cursor=0",
     "SPEECH OUTPUT: 'US State test 1 combo box US State test 1 text California selected'"]))

########################################################################
# Replace all the text (already selected) with a 'C'.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("C"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "Replace existing text with a 'C'", 
    ["BUG? - At this point, the entry expands into a combo box with three items showing. We speak them all. We should instead indicate that this object is expanded, similar to what we do with autocompletes.",
     "BRAILLE LINE:  '  US State test 1 California $l'",
     "     VISIBLE:  '  US State test 1 California $l', cursor=0",
     "BRAILLE LINE:  '  US State test 1 C $l'",
     "     VISIBLE:  '  US State test 1 C $l', cursor=0",
     "SPEECH OUTPUT: '• California• Colorado• Connecticut'"]))

########################################################################
# Down Arrow amongst the newly-displayed items. One should not be able
# to arrow out of the combo box.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Down Arrow", 
    ["BRAILLE LINE:  '  US State test 1 C $l'",
     "     VISIBLE:  '  US State test 1 C $l', cursor=0",
     "BRAILLE LINE:  '• California'",
     "     VISIBLE:  '• California', cursor=1",
     "SPEECH OUTPUT: '• California'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down Arrow", 
    ["BRAILLE LINE:  '• Colorado'",
     "     VISIBLE:  '• Colorado', cursor=1",
     "SPEECH OUTPUT: '• Colorado'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Down Arrow", 
    ["BRAILLE LINE:  '• Connecticut'",
     "     VISIBLE:  '• Connecticut', cursor=1",
     "SPEECH OUTPUT: '• Connecticut'"]))

# Note that not saying anything here is correct because we're already at
# the end of the expanded combo box thus pressing Down doesn't move us.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Down Arrow", 
    [""]))

########################################################################
# Up Arrow amongst the newly-displayed items. One should not be able
# to arrow out of the combo box.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "1. Up Arrow", 
    ["BRAILLE LINE:  '• Colorado'",
     "     VISIBLE:  '• Colorado', cursor=1",
     "SPEECH OUTPUT: '• Colorado'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "2. Up Arrow", 
    ["BRAILLE LINE:  '• California'",
     "     VISIBLE:  '• California', cursor=1",
     "SPEECH OUTPUT: '• California'"]))

# Note that not saying anything here is correct because we're already at
# the top of the expanded combo box thus pressing Up doesn't move us.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "3. Up Arrow", 
    [""]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I - Combo box expanded", 
    ["BRAILLE LINE:  '• California'",
     "     VISIBLE:  '• California', cursor=1",
     "SPEECH OUTPUT: 'list item • California item 1 of 3'"]))

########################################################################
# Escape to collapse the combo box.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Escape"))
sequence.append(utils.AssertPresentationAction(
    "Escape", 
    ["BRAILLE LINE:  '  US State test 1 California $l'",
     "     VISIBLE:  '  US State test 1 California $l', cursor=0",
     "SPEECH OUTPUT: 'US State test 1 combo box US State test 1 text California selected'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I - Combo box collapsed back into an entry", 
    ["BRAILLE LINE:  '  US State test 1 California $l'",
     "     VISIBLE:  '  US State test 1 California $l', cursor=0",
     "SPEECH OUTPUT: 'US State test 1 text alifornia selected'"]))

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
