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
    ["BRAILLE LINE:  'Test: z Link y Link x Link w Link v Link u Link t Link s Link r Link q Link p Link o Link n Link m Link l Link k Link j Link i Link h Link g Link f Link e Link d Link c Link b Link a Link'",
     "     VISIBLE:  'z Link y Link x Link w Link v Li', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'z link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "3. Tab",
    ["BRAILLE LINE:  'Test: z Link y Link x Link w Link v Link u Link t Link s Link r Link q Link p Link o Link n Link m Link l Link k Link j Link i Link h Link g Link f Link e Link d Link c Link b Link a Link'",
     "     VISIBLE:  'y Link x Link w Link v Link u Li', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'y link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "4. Tab",
    ["BRAILLE LINE:  'Test: z Link y Link x Link w Link v Link u Link t Link s Link r Link q Link p Link o Link n Link m Link l Link k Link j Link i Link h Link g Link f Link e Link d Link c Link b Link a Link'",
     "     VISIBLE:  'x Link w Link v Link u Link t Li', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'x link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "5. Tab",
    ["BRAILLE LINE:  'Test: z Link y Link x Link w Link v Link u Link t Link s Link r Link q Link p Link o Link n Link m Link l Link k Link j Link i Link h Link g Link f Link e Link d Link c Link b Link a Link'",
     "     VISIBLE:  'w Link v Link u Link t Link s Li', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'w link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "6. Tab",
    ["BRAILLE LINE:  'Test: z Link y Link x Link w Link v Link u Link t Link s Link r Link q Link p Link o Link n Link m Link l Link k Link j Link i Link h Link g Link f Link e Link d Link c Link b Link a Link'",
     "     VISIBLE:  'v Link u Link t Link s Link r Li', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'v link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "7. Tab",
    ["BRAILLE LINE:  'Test: z Link y Link x Link w Link v Link u Link t Link s Link r Link q Link p Link o Link n Link m Link l Link k Link j Link i Link h Link g Link f Link e Link d Link c Link b Link a Link'",
     "     VISIBLE:  'u Link t Link s Link r Link q Li', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'u link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "8. Tab",
    ["BRAILLE LINE:  'Test: z Link y Link x Link w Link v Link u Link t Link s Link r Link q Link p Link o Link n Link m Link l Link k Link j Link i Link h Link g Link f Link e Link d Link c Link b Link a Link'",
     "     VISIBLE:  't Link s Link r Link q Link p Li', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 't link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "9. Tab",
    ["BRAILLE LINE:  'Test: z Link y Link x Link w Link v Link u Link t Link s Link r Link q Link p Link o Link n Link m Link l Link k Link j Link i Link h Link g Link f Link e Link d Link c Link b Link a Link'",
     "     VISIBLE:  's Link r Link q Link p Link o Li', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 's link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "10. Tab",
    ["BRAILLE LINE:  'Test: z Link y Link x Link w Link v Link u Link t Link s Link r Link q Link p Link o Link n Link m Link l Link k Link j Link i Link h Link g Link f Link e Link d Link c Link b Link a Link'",
     "     VISIBLE:  'r Link q Link p Link o Link n Li', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'r link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "11. Tab",
    ["BRAILLE LINE:  'Test: z Link y Link x Link w Link v Link u Link t Link s Link r Link q Link p Link o Link n Link m Link l Link k Link j Link i Link h Link g Link f Link e Link d Link c Link b Link a Link'",
     "     VISIBLE:  'q Link p Link o Link n Link m Li', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'q link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "12. Tab",
    ["BRAILLE LINE:  'Test: z Link y Link x Link w Link v Link u Link t Link s Link r Link q Link p Link o Link n Link m Link l Link k Link j Link i Link h Link g Link f Link e Link d Link c Link b Link a Link'",
     "     VISIBLE:  'p Link o Link n Link m Link l Li', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'p link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "13. Tab",
    ["BRAILLE LINE:  'Test: z Link y Link x Link w Link v Link u Link t Link s Link r Link q Link p Link o Link n Link m Link l Link k Link j Link i Link h Link g Link f Link e Link d Link c Link b Link a Link'",
     "     VISIBLE:  'o Link n Link m Link l Link k Li', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'o link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "14. Tab",
    ["BRAILLE LINE:  'Test: z Link y Link x Link w Link v Link u Link t Link s Link r Link q Link p Link o Link n Link m Link l Link k Link j Link i Link h Link g Link f Link e Link d Link c Link b Link a Link'",
     "     VISIBLE:  'n Link m Link l Link k Link j Li', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'n link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "15. Tab",
    ["BRAILLE LINE:  'Test: z Link y Link x Link w Link v Link u Link t Link s Link r Link q Link p Link o Link n Link m Link l Link k Link j Link i Link h Link g Link f Link e Link d Link c Link b Link a Link'",
     "     VISIBLE:  'm Link l Link k Link j Link i Li', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'm link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "16. Tab",
    ["BRAILLE LINE:  'Test: z Link y Link x Link w Link v Link u Link t Link s Link r Link q Link p Link o Link n Link m Link l Link k Link j Link i Link h Link g Link f Link e Link d Link c Link b Link a Link'",
     "     VISIBLE:  'l Link k Link j Link i Link h Li', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'l link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "17. Tab",
    ["BRAILLE LINE:  'Test: z Link y Link x Link w Link v Link u Link t Link s Link r Link q Link p Link o Link n Link m Link l Link k Link j Link i Link h Link g Link f Link e Link d Link c Link b Link a Link'",
     "     VISIBLE:  'k Link j Link i Link h Link g Li', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'k link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "18. Tab",
    ["BRAILLE LINE:  'Test: z Link y Link x Link w Link v Link u Link t Link s Link r Link q Link p Link o Link n Link m Link l Link k Link j Link i Link h Link g Link f Link e Link d Link c Link b Link a Link'",
     "     VISIBLE:  'j Link i Link h Link g Link f Li', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'j link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "19. Tab",
    ["BRAILLE LINE:  'Test: z Link y Link x Link w Link v Link u Link t Link s Link r Link q Link p Link o Link n Link m Link l Link k Link j Link i Link h Link g Link f Link e Link d Link c Link b Link a Link'",
     "     VISIBLE:  'i Link h Link g Link f Link e Li', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'i link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "20. Tab",
    ["BRAILLE LINE:  'Test: z Link y Link x Link w Link v Link u Link t Link s Link r Link q Link p Link o Link n Link m Link l Link k Link j Link i Link h Link g Link f Link e Link d Link c Link b Link a Link'",
     "     VISIBLE:  'h Link g Link f Link e Link d Li', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'h link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "21. Tab",
    ["BRAILLE LINE:  'Test: z Link y Link x Link w Link v Link u Link t Link s Link r Link q Link p Link o Link n Link m Link l Link k Link j Link i Link h Link g Link f Link e Link d Link c Link b Link a Link'",
     "     VISIBLE:  'g Link f Link e Link d Link c Li', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'g link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "22. Tab",
    ["BRAILLE LINE:  'Test: z Link y Link x Link w Link v Link u Link t Link s Link r Link q Link p Link o Link n Link m Link l Link k Link j Link i Link h Link g Link f Link e Link d Link c Link b Link a Link'",
     "     VISIBLE:  'f Link e Link d Link c Link b Li', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'f link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "23. Tab",
    ["BRAILLE LINE:  'Test: z Link y Link x Link w Link v Link u Link t Link s Link r Link q Link p Link o Link n Link m Link l Link k Link j Link i Link h Link g Link f Link e Link d Link c Link b Link a Link'",
     "     VISIBLE:  'e Link d Link c Link b Link a Li', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'e link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "24. Tab",
    ["BRAILLE LINE:  'Test: z Link y Link x Link w Link v Link u Link t Link s Link r Link q Link p Link o Link n Link m Link l Link k Link j Link i Link h Link g Link f Link e Link d Link c Link b Link a Link'",
     "     VISIBLE:  'd Link c Link b Link a Link', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'd link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "25. Tab",
    ["BRAILLE LINE:  'Test: z Link y Link x Link w Link v Link u Link t Link s Link r Link q Link p Link o Link n Link m Link l Link k Link j Link i Link h Link g Link f Link e Link d Link c Link b Link a Link'",
     "     VISIBLE:  'c Link b Link a Link', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'c link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "26. Tab",
    ["BRAILLE LINE:  'Test: z Link y Link x Link w Link v Link u Link t Link s Link r Link q Link p Link o Link n Link m Link l Link k Link j Link i Link h Link g Link f Link e Link d Link c Link b Link a Link'",
     "     VISIBLE:  'b Link a Link', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'b link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "27. Tab",
    ["BRAILLE LINE:  'Test: z Link y Link x Link w Link v Link u Link t Link s Link r Link q Link p Link o Link n Link m Link l Link k Link j Link i Link h Link g Link f Link e Link d Link c Link b Link a Link'",
     "     VISIBLE:  'a Link', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'a link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "28. Tab",
    ["BRAILLE LINE:  'wk09_frozenmovie Link Image'",
     "     VISIBLE:  'wk09_frozenmovie Link Image', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'wk09_frozenmovie link image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "29. Tab",
    ["BRAILLE LINE:  'shop.safeway.com Link Rancher's Reserve Link'",
     "     VISIBLE:  'shop.safeway.com Link Rancher's ', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'shop.safeway.com link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "30. Tab",
    ["BRAILLE LINE:  'shop.safeway.com Link Rancher's Reserve Link'",
     "     VISIBLE:  'Rancher's Reserve Link', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Rancher's Reserve link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "31. Tab",
    ["BRAILLE LINE:  'www.vons.com Link www.dominicks.com Link www.randalls.com Link www.tomthumb.com Link www.genuardis.com Link www.pavilions.com Link www.carrsqc.com Link'",
     "     VISIBLE:  'www.vons.com Link www.dominicks.', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'www.vons.com link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "32. Tab",
    ["BRAILLE LINE:  'www.vons.com Link www.dominicks.com Link www.randalls.com Link www.tomthumb.com Link www.genuardis.com Link www.pavilions.com Link www.carrsqc.com Link'",
     "     VISIBLE:  'www.dominicks.com Link www.randa', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'www.dominicks.com link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "33. Tab",
    ["BRAILLE LINE:  'www.vons.com Link www.dominicks.com Link www.randalls.com Link www.tomthumb.com Link www.genuardis.com Link www.pavilions.com Link www.carrsqc.com Link'",
     "     VISIBLE:  'www.randalls.com Link www.tomthu', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'www.randalls.com link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "34. Tab",
    ["BRAILLE LINE:  'www.vons.com Link www.dominicks.com Link www.randalls.com Link www.tomthumb.com Link www.genuardis.com Link www.pavilions.com Link www.carrsqc.com Link'",
     "     VISIBLE:  'www.tomthumb.com Link www.genuar', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'www.tomthumb.com link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "35. Tab",
    ["BRAILLE LINE:  'www.vons.com Link www.dominicks.com Link www.randalls.com Link www.tomthumb.com Link www.genuardis.com Link www.pavilions.com Link www.carrsqc.com Link'",
     "     VISIBLE:  'www.genuardis.com Link www.pavil', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'www.genuardis.com link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "36. Tab",
    ["BRAILLE LINE:  'www.vons.com Link www.dominicks.com Link www.randalls.com Link www.tomthumb.com Link www.genuardis.com Link www.pavilions.com Link www.carrsqc.com Link'",
     "     VISIBLE:  'www.pavilions.com Link www.carrs', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'www.pavilions.com link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "37. Tab",
    ["BRAILLE LINE:  'www.vons.com Link www.dominicks.com Link www.randalls.com Link www.tomthumb.com Link www.genuardis.com Link www.pavilions.com Link www.carrsqc.com Link'",
     "     VISIBLE:  'www.carrsqc.com Link', cursor=1",
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
