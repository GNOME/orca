#!/usr/bin/python

"""Test of menu and menu item output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Application class"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("<Control>r"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>p"))
sequence.append(utils.AssertPresentationAction(
    "1. Initial menu and menu item",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame Preferences menu'",
     "     VISIBLE:  'Preferences menu', cursor=1",
     "BRAILLE LINE:  'gtk3-demo-application application Application Class frame < > Prefer Dark Theme check menu item'",
     "     VISIBLE:  '< > Prefer Dark Theme check menu', cursor=1",
     "SPEECH OUTPUT: 'Preferences menu.'",
     "SPEECH OUTPUT: 'Prefer Dark Theme check menu item not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "2. Review current line",
    ["BRAILLE LINE:  '< > Prefer Dark Theme $l'",
     "     VISIBLE:  '< > Prefer Dark Theme $l', cursor=1",
     "SPEECH OUTPUT: 'not checked Prefer Dark Theme'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "3. Review previous line",
    [""]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "4. Review next line",
    ["BRAILLE LINE:  '< > Hide Titlebar when maximized $l'",
     "     VISIBLE:  '< > Hide Titlebar when maximized', cursor=1",
     "SPEECH OUTPUT: 'not checked Hide Titlebar when maximized'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "5. Review current word",
    ["BRAILLE LINE:  '< > Hide Titlebar when maximized $l'",
     "     VISIBLE:  '< > Hide Titlebar when maximized', cursor=1",
     "SPEECH OUTPUT: 'not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "6. Review next word",
    ["BRAILLE LINE:  '< > Hide Titlebar when maximized $l'",
     "     VISIBLE:  'Hide Titlebar when maximized $l', cursor=1",
     "SPEECH OUTPUT: 'Hide '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "7. Review next word",
    ["BRAILLE LINE:  '< > Hide Titlebar when maximized $l'",
     "     VISIBLE:  'Hide Titlebar when maximized $l', cursor=6",
     "SPEECH OUTPUT: 'Titlebar '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "8. Review next line",
    ["BRAILLE LINE:  'Color $l'",
     "     VISIBLE:  'Color $l', cursor=1",
     "SPEECH OUTPUT: 'Color'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "9. Review next line",
    ["BRAILLE LINE:  'Shape $l'",
     "     VISIBLE:  'Shape $l', cursor=1",
     "SPEECH OUTPUT: 'Shape'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "10. Review next line",
    ["BRAILLE LINE:  '< > Bold $l'",
     "     VISIBLE:  '< > Bold $l', cursor=1",
     "SPEECH OUTPUT: 'not checked Bold'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "11. Review next line",
    [""]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "12. Review current word",
    ["BRAILLE LINE:  '< > Bold $l'",
     "     VISIBLE:  '< > Bold $l', cursor=1",
     "SPEECH OUTPUT: 'not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "13. Review next word",
    ["BRAILLE LINE:  '< > Bold $l'",
     "     VISIBLE:  '< > Bold $l', cursor=5",
     "SPEECH OUTPUT: 'Bold'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_2"))
sequence.append(utils.AssertPresentationAction(
    "14. Review current char",
    ["BRAILLE LINE:  '< > Bold $l'",
     "     VISIBLE:  '< > Bold $l', cursor=5",
     "SPEECH OUTPUT: 'B'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_3"))
sequence.append(utils.AssertPresentationAction(
    "15. Review next char",
    ["BRAILLE LINE:  '< > Bold $l'",
     "     VISIBLE:  '< > Bold $l', cursor=6",
     "SPEECH OUTPUT: 'o'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_1"))
sequence.append(utils.AssertPresentationAction(
    "16. Review previous char",
    ["BRAILLE LINE:  '< > Bold $l'",
     "     VISIBLE:  '< > Bold $l', cursor=5",
     "SPEECH OUTPUT: 'B'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_1"))
sequence.append(utils.AssertPresentationAction(
    "17. Review previous char",
    ["BRAILLE LINE:  '< > Bold $l'",
     "     VISIBLE:  '< > Bold $l', cursor=1",
     "SPEECH OUTPUT: 'not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_4"))
sequence.append(utils.AssertPresentationAction(
    "18. Review previous word",
    ["BRAILLE LINE:  'Shape $l'",
     "     VISIBLE:  'Shape $l', cursor=1",
     "SPEECH OUTPUT: 'Shape'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_4"))
sequence.append(utils.AssertPresentationAction(
    "19. Review previoius word",
    ["BRAILLE LINE:  'Color $l'",
     "     VISIBLE:  'Color $l', cursor=1",
     "SPEECH OUTPUT: 'Color'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Divide"))
sequence.append(utils.AssertPresentationAction(
    "20. Synthesize click to open menu",
    ["KNOWN ISSUE: For some reason only a real mouse event opens this menu",
     "BRAILLE LINE:  'gtk3-demo-application application Application Class frame Color menu'",
     "     VISIBLE:  'Color menu', cursor=1",
     "BRAILLE LINE:  'gtk3-demo-application application Application Class frame Color menu'",
     "     VISIBLE:  'Color menu', cursor=1",
     "SPEECH OUTPUT: 'Color menu.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "21. Right",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame Preferences menu &=y Red radio menu item(Ctrl+R)'",
     "     VISIBLE:  '&=y Red radio menu item(Ctrl+R)', cursor=1",
     "SPEECH OUTPUT: 'Red selected radio menu item Ctrl+R'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "22. Review current line",
    ["BRAILLE LINE:  '&=y Red $l'",
     "     VISIBLE:  '&=y Red $l', cursor=1",
     "SPEECH OUTPUT: 'selected Red'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "23. Review next line",
    ["BRAILLE LINE:  '& y Green $l'",
     "     VISIBLE:  '& y Green $l', cursor=1",
     "SPEECH OUTPUT: 'not selected Green'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "24. Review next line",
    ["BRAILLE LINE:  '& y Blue $l'",
     "     VISIBLE:  '& y Blue $l', cursor=1",
     "SPEECH OUTPUT: 'not selected Blue'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "25. Review next line",
    [""]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "26. Review previous line",
    ["BRAILLE LINE:  '& y Green $l'",
     "     VISIBLE:  '& y Green $l', cursor=1",
     "SPEECH OUTPUT: 'not selected Green'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
