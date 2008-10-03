#!/usr/bin/python

"""Test of Orca output when tabbing on a page with imagemaps.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the local "backwards" test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "backwards.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

sequence.append(WaitForFocus("Backwards Stuff",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'This looks like A to Z, but it's really Z to A.'",
     "     VISIBLE:  'This looks like A to Z, but it's', cursor=1",
     "SPEECH OUTPUT: 'This looks like A to Z, but it's really Z to A.'"]))

########################################################################
# Tab to the End.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "2. Tab",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'z y x w v u t s r q p o n m l k ', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'z link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "3. Tab",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'y x w v u t s r q p o n m l k j ', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'y link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "4. Tab",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'x w v u t s r q p o n m l k j i ', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'x link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "5. Tab",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'w v u t s r q p o n m l k j i h ', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'w link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "6. Tab",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'v u t s r q p o n m l k j i h g ', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'v link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "7. Tab",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'u t s r q p o n m l k j i h g f ', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'u link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "8. Tab",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  't s r q p o n m l k j i h g f e ', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 't link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "9. Tab",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  's r q p o n m l k j i h g f e d ', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 's link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "10. Tab",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'r q p o n m l k j i h g f e d c ', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'r link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "11. Tab",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'q p o n m l k j i h g f e d c b ', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'q link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "12. Tab",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'p o n m l k j i h g f e d c b a', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'p link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "13. Tab",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'o n m l k j i h g f e d c b a', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'o link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "14. Tab",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'n m l k j i h g f e d c b a', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'n link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "15. Tab",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'm l k j i h g f e d c b a', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'm link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "16. Tab",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'l k j i h g f e d c b a', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'l link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "17. Tab",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'k j i h g f e d c b a', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'k link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "18. Tab",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'j i h g f e d c b a', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'j link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "19. Tab",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'i h g f e d c b a', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'i link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "20. Tab",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'h g f e d c b a', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'h link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "21. Tab",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'g f e d c b a', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'g link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "22. Tab",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'f e d c b a', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'f link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "23. Tab",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'e d c b a', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'e link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "24. Tab",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'd c b a', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'd link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "25. Tab",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'c b a', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'c link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "26. Tab",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'b a', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'b link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "27. Tab",
    ["BRAILLE LINE:  'Test: z y x w v u t s r q p o n m l k j i h g f e d c b a'",
     "     VISIBLE:  'a', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'a link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "28. Tab",
    ["BRAILLE LINE:  'wk09_frozenmovie Image'",
     "     VISIBLE:  'wk09_frozenmovie Image', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'wk09_frozenmovie link image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "29. Tab",
    ["BRAILLE LINE:  'shop.safeway.com Rancher's Reserve'",
     "     VISIBLE:  'shop.safeway.com Rancher's Reser', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'shop.safeway.com link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "30. Tab",
    ["BRAILLE LINE:  'shop.safeway.com Rancher's Reserve'",
     "     VISIBLE:  'Rancher's Reserve', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Rancher's Reserve link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "31. Tab",
    ["BRAILLE LINE:  'www.vons.com www.dominicks.com www.randalls.com www.tomthumb.com www.genuardis.com www.pavilions.com www.carrsqc.com'",
     "     VISIBLE:  'www.vons.com www.dominicks.com w', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'www.vons.com link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "32. Tab",
    ["BRAILLE LINE:  'www.vons.com www.dominicks.com www.randalls.com www.tomthumb.com www.genuardis.com www.pavilions.com www.carrsqc.com'",
     "     VISIBLE:  'www.dominicks.com www.randalls.c', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'www.dominicks.com link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "33. Tab",
    ["BRAILLE LINE:  'www.vons.com www.dominicks.com www.randalls.com www.tomthumb.com www.genuardis.com www.pavilions.com www.carrsqc.com'",
     "     VISIBLE:  'www.randalls.com www.tomthumb.co', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'www.randalls.com link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "34. Tab",
    ["BRAILLE LINE:  'www.vons.com www.dominicks.com www.randalls.com www.tomthumb.com www.genuardis.com www.pavilions.com www.carrsqc.com'",
     "     VISIBLE:  'www.tomthumb.com www.genuardis.c', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'www.tomthumb.com link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "35. Tab",
    ["BRAILLE LINE:  'www.vons.com www.dominicks.com www.randalls.com www.tomthumb.com www.genuardis.com www.pavilions.com www.carrsqc.com'",
     "     VISIBLE:  'www.genuardis.com www.pavilions.', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'www.genuardis.com link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "36. Tab",
    ["BRAILLE LINE:  'www.vons.com www.dominicks.com www.randalls.com www.tomthumb.com www.genuardis.com www.pavilions.com www.carrsqc.com'",
     "     VISIBLE:  'www.pavilions.com www.carrsqc.co', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'www.pavilions.com link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "37. Tab",
    ["BRAILLE LINE:  'www.vons.com www.dominicks.com www.randalls.com www.tomthumb.com www.genuardis.com www.pavilions.com www.carrsqc.com'",
     "     VISIBLE:  'www.carrsqc.com', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'www.carrsqc.com link'"]))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
