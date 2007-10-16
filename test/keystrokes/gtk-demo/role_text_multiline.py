#!/usr/bin/python

"""Test of multiline editable text using the gtk-demo Application Main Window
   demo.
"""

from macaroon.playback import *

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))

########################################################################
# Once gtk-demo is running, invoke the Application Main Window demo
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Application main window", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the demo comes up, go to the text area and type.
#
#sequence.append(WaitForWindowActivate("Application Window",None))
sequence.append(WaitForFocus("Open", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("This is a test.", 500))
sequence.append(KeyComboAction("Return", 500))
sequence.append(KeyComboAction("Return", 500))
sequence.append(TypeAction("I'm just typing away like a mad little monkey with nothing better to do in my life than eat fruit and type.", 500))
sequence.append(KeyComboAction("Return", 500))
sequence.append(TypeAction("The keyboard sure can get sticky.", 500))
sequence.append(KeyComboAction("Return", 500))
sequence.append(TypeAction("Tis this and thus thou art in Rome?", 500))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# Go to the beginning of the text area.  The following should be
# presented:
#
# BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test. $l'
#      VISIBLE:  'This is a test. $l', cursor=1
#
# SPEECH OUTPUT: 'This is a test.'
#
sequence.append(KeyComboAction("<Control>Home", 500))

########################################################################
# Now, arrow right to the end of the word "This" and select "is a test"
# word by word.  When you are done the last thing presented should be:
#
# BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test. $l'
#      VISIBLE:  'This is a test. $l', cursor=15
#
# SPEECH OUTPUT: ' test'
# SPEECH OUTPUT: 'selected'
# SPEECH OUTPUT: ' is a test'
# SPEECH OUTPUT: 'selected'
#
sequence.append(KeyComboAction("Right", 500))
sequence.append(KeyComboAction("Right", 500))
sequence.append(KeyComboAction("Right", 500))
sequence.append(KeyComboAction("Right", 500))
sequence.append(KeyComboAction("<Shift><Control>Right", 500))
sequence.append(KeyComboAction("<Shift><Control>Right", 500))
sequence.append(KeyComboAction("<Shift><Control>Right", 500))

########################################################################
# Unselect "test".  The following should be presented:
#
# BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test. $l'
#      VISIBLE:  'This is a test. $l', cursor=11
#
# SPEECH OUTPUT: 'test'
# SPEECH OUTPUT: 'unselected'
#
sequence.append(KeyComboAction("<Shift><Control>Left", 500))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented:
#
# BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test. $l'
#      VISIBLE:  'This is a test. $l', cursor=11
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'text'
# SPEECH OUTPUT: ' is a '
# SPEECH OUTPUT: 'selected'
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Arrow down to "I'm typing away..." and Select to the end of the line.
# The following should be presented:
#
# BRAILLE LINE:  'I'm just typing away like a monkey with nothing better to do in my life than eat fruit and type. $l'
#      VISIBLE:  'y life than eat fruit and type. ', cursor=32
#
# SPEECH OUTPUT: 'yping away like a monkey with nothing better to do in my life than eat fruit and type.'
# SPEECH OUTPUT: 'selected'
#
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down", 500))
sequence.append(KeyComboAction("<Shift>End", 500))

########################################################################
# Right arrow to the beginning of the next line.  The following should
# be presented:
#
# BRAILLE LINE:  'The keyboard sure can get sticky. $l'
#      VISIBLE:  'The keyboard sure can get sticky', cursor=1
#      
# SPEECH OUTPUT: 'newline'
# SPEECH OUTPUT: 'T'
#
sequence.append(KeyComboAction("Right", 500))

########################################################################
# Try a "SayAll".  The following should be presented:
#
# BRAILLE LINE:  'Tis this and thus thou art in Rome? $l'
#      VISIBLE:  'this and thus thou art in Rome? ', cursor=32
#
# SPEECH OUTPUT: '
# The keyboard sure can get sticky.'
# SPEECH OUTPUT: '
# Tis this and thus thou art in Rome?'
# SPEECH OUTPUT: '
# '
#
sequence.append(KeyComboAction("KP_Add", 500))
sequence.append(PauseAction(3000))

########################################################################
# Dismiss the menu and close the Application Window demo window
#
sequence.append(KeyComboAction("<Alt>F4"))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
