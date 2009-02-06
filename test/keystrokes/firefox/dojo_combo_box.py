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
    ["BUG? - Too verbose",
     "BRAILLE LINE:  'US State test 1 California $l'",
     "     VISIBLE:  'US State test 1 California $l', cursor=0",
     "BRAILLE LINE:  '  US State test 1 California $l'",
     "     VISIBLE:  '  US State test 1 California $l', cursor=0",
     "BRAILLE LINE:  '  US State test 1 California $l'",
     "     VISIBLE:  '  US State test 1 California $l', cursor=0",
     "SPEECH OUTPUT: 'US State test 1 combo box'",
     "SPEECH OUTPUT: 'US State test 1 text California selected'"]))

########################################################################
# Replace all the text (already selected) with a 'C'.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("C"))
sequence.append(utils.AssertPresentationAction(
    "Replace existing text with a 'C'", 
    ["BUG? - Too verbose",
     "BRAILLE LINE:  'US State test 1 California $l'",
     "     VISIBLE:  'US State test 1 California $l', cursor=0",
     "BRAILLE LINE:  'US State test 1 C $l'",
     "     VISIBLE:  'US State test 1 C $l', cursor=0",
     "BRAILLE LINE:  'US State test 1 C $l'",
     "     VISIBLE:  'US State test 1 C $l', cursor=0",
     "SPEECH OUTPUT: '• California• Colorado• Connecticut'"]))

########################################################################
# Down Arrow amongst the newly-displayed items. One should not be able
# to arrow out of the combo box.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Down Arrow", 
    ["BRAILLE LINE:  'US State test 1 C $l'",
     "     VISIBLE:  'US State test 1 C $l', cursor=0",
     "BRAILLE LINE:  '• California ListItem'",
     "     VISIBLE:  '• California ListItem', cursor=1",
     "BRAILLE LINE:  '  US State test 1 California $l'",
     "     VISIBLE:  '  US State test 1 California $l', cursor=0",
     "BRAILLE LINE:  '  US State test 1 California $l'",
     "     VISIBLE:  '  US State test 1 California $l', cursor=0",
     "BRAILLE LINE:  'US State test 1 California $l'",
     "     VISIBLE:  'US State test 1 California $l', cursor=0",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: '• California'",
     "SPEECH OUTPUT: '  US State test 1 text California selected'",
     "SPEECH OUTPUT: 'California'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down Arrow", 
    ["BUG? - Too verbose",
    "BRAILLE LINE:  'US State test 1 California $l'",
     "     VISIBLE:  'US State test 1 California $l', cursor=0",
     "BRAILLE LINE:  'US State test 1 C $l'",
     "     VISIBLE:  'US State test 1 C $l', cursor=0",
     "BRAILLE LINE:  'US State test 1 Colorado $l'",
     "     VISIBLE:  'US State test 1 Colorado $l', cursor=0",
     "BRAILLE LINE:  '• Colorado ListItem'",
     "     VISIBLE:  '• Colorado ListItem', cursor=1",
     "BRAILLE LINE:  '  US State test 1 Colorado $l'",
     "     VISIBLE:  '  US State test 1 Colorado $l', cursor=0",
     "BRAILLE LINE:  '  US State test 1 Colorado $l'",
     "     VISIBLE:  '  US State test 1 Colorado $l', cursor=0",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: '• Colorado'",
     "SPEECH OUTPUT: '  US State test 1 text Colorado selected'",
     "SPEECH OUTPUT: 'Colorado'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Down Arrow", 
    ["BUG? - Too verbose",
    "BRAILLE LINE:  'US State test 1 Colorado $l'",
     "     VISIBLE:  'US State test 1 Colorado $l', cursor=0",
     "BRAILLE LINE:  'US State test 1 C $l'",
     "     VISIBLE:  'US State test 1 C $l', cursor=0",
     "BRAILLE LINE:  '  US State test 1 Connecticut $l'",
     "     VISIBLE:  '  US State test 1 Connecticut $l', cursor=30",
     "BRAILLE LINE:  '• Connecticut ListItem'",
     "     VISIBLE:  '• Connecticut ListItem', cursor=1",
     "BRAILLE LINE:  '  US State test 1 Connecticut $l'",
     "     VISIBLE:  '  US State test 1 Connecticut $l', cursor=0",
     "BRAILLE LINE:  '  US State test 1 Connecticut $l'",
     "     VISIBLE:  '  US State test 1 Connecticut $l', cursor=0",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: '• Connecticut'",
     "SPEECH OUTPUT: '  US State test 1 text Connecticut selected'",
     "SPEECH OUTPUT: 'Connecticut'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Down Arrow", 
    ["BUG? - Too verbose",
    "BRAILLE LINE:  'US State test 1 Connecticut $l'",
     "     VISIBLE:  'US State test 1 Connecticut $l', cursor=0",
     "BRAILLE LINE:  'US State test 1 C $l'",
     "     VISIBLE:  'US State test 1 C $l', cursor=0",
     "BRAILLE LINE:  'US State test 1 Connecticut $l'",
     "     VISIBLE:  'US State test 1 Connecticut $l', cursor=0",
     "BRAILLE LINE:  '  US State test 1 Connecticut $l'",
     "     VISIBLE:  '  US State test 1 Connecticut $l', cursor=0",
     "BRAILLE LINE:  '  US State test 1 Connecticut $l'",
     "     VISIBLE:  '  US State test 1 Connecticut $l', cursor=0",
     "SPEECH OUTPUT: '  US State test 1 text Connecticut selected'",
     "SPEECH OUTPUT: 'Connecticut'"]))

########################################################################
# Up Arrow amongst the newly-displayed items. One should not be able
# to arrow out of the combo box.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "1. Up Arrow", 
    ["BUG? - Too verbose",
    "BRAILLE LINE:  'US State test 1 Connecticut $l'",
     "     VISIBLE:  'US State test 1 Connecticut $l', cursor=0",
     "BRAILLE LINE:  'US State test 1 C $l'",
     "     VISIBLE:  'US State test 1 C $l', cursor=0",
     "BRAILLE LINE:  'US State test 1 Colorado $l'",
     "     VISIBLE:  'US State test 1 Colorado $l', cursor=0",
     "BRAILLE LINE:  '• Colorado ListItem'",
     "     VISIBLE:  '• Colorado ListItem', cursor=1",
     "BRAILLE LINE:  '  US State test 1 Colorado $l'",
     "     VISIBLE:  '  US State test 1 Colorado $l', cursor=0",
     "BRAILLE LINE:  '  US State test 1 Colorado $l'",
     "     VISIBLE:  '  US State test 1 Colorado $l', cursor=0",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: '• Colorado'",
     "SPEECH OUTPUT: '  US State test 1 text Colorado selected'",
     "SPEECH OUTPUT: 'Colorado'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "2. Up Arrow", 
    ["BUG? - Too verbose",
    "BRAILLE LINE:  'US State test 1 Colorado $l'",
     "     VISIBLE:  'US State test 1 Colorado $l', cursor=0",
     "BRAILLE LINE:  'US State test 1 C $l'",
     "     VISIBLE:  'US State test 1 C $l', cursor=0",
     "BRAILLE LINE:  '  US State test 1 California $l'",
     "     VISIBLE:  '  US State test 1 California $l', cursor=29",
     "BRAILLE LINE:  '• California ListItem'",
     "     VISIBLE:  '• California ListItem', cursor=1",
     "BRAILLE LINE:  '  US State test 1 California $l'",
     "     VISIBLE:  '  US State test 1 California $l', cursor=0",
     "BRAILLE LINE:  '  US State test 1 California $l'",
     "     VISIBLE:  '  US State test 1 California $l', cursor=0",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: '• California'",
     "SPEECH OUTPUT: '  US State test 1 text California selected'",
     "SPEECH OUTPUT: 'California'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "3. Up Arrow", 
    ["BUG? - Too verbose",
    "BRAILLE LINE:  'US State test 1 California $l'",
     "     VISIBLE:  'US State test 1 California $l', cursor=0",
     "BRAILLE LINE:  'US State test 1 C $l'",
     "     VISIBLE:  'US State test 1 C $l', cursor=0",
     "BRAILLE LINE:  'US State test 1 California $l'",
     "     VISIBLE:  'US State test 1 California $l', cursor=0",
     "BRAILLE LINE:  '  US State test 1 California $l'",
     "     VISIBLE:  '  US State test 1 California $l', cursor=0",
     "BRAILLE LINE:  '  US State test 1 California $l'",
     "     VISIBLE:  '  US State test 1 California $l', cursor=0",
     "SPEECH OUTPUT: '  US State test 1 text California selected'",
     "SPEECH OUTPUT: 'California'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I - Combo box expanded", 
    ["BUG? - No indication that this is a combo box",
    "BRAILLE LINE:  'US State test 1 California $l'",
     "     VISIBLE:  'US State test 1 California $l', cursor=0",
     "SPEECH OUTPUT: 'US State test 1'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'alifornia'",
     "SPEECH OUTPUT: 'selected'",
     "SPEECH OUTPUT: ''"]))

########################################################################
# Escape to collapse the combo box.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Escape"))
sequence.append(utils.AssertPresentationAction(
    "Escape", 
    [""]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I - Combo box collapsed", 
    ["BUG? - Should we indicate that we're in a combo box now that it is collapsed?",
    "BRAILLE LINE:  'US State test 1 California $l'",
     "     VISIBLE:  'US State test 1 California $l', cursor=0",
     "SPEECH OUTPUT: 'US State test 1'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'alifornia'",
     "SPEECH OUTPUT: 'selected'",
     "SPEECH OUTPUT: ''"]))

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
