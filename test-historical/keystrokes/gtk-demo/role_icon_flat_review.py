#!/usr/bin/python

"""Test of icon output."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Images"))
sequence.append(KeyComboAction("Escape"))
sequence.append(KeyComboAction("Up"))
sequence.append(KeyComboAction("<Shift>Right"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. bin icon",
    ["BRAILLE LINE:  'gtk-demo application GtkIconView demo frame layered pane bin icon'",
     "     VISIBLE:  'bin icon', cursor=1",
     "SPEECH OUTPUT: 'bin icon.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "2. Review current line",
    ["BRAILLE LINE:  'bin boot dev etc home lib lib64 $l'",
     "     VISIBLE:  'bin boot dev etc home lib lib64 ', cursor=1",
     "SPEECH OUTPUT: 'bin boot dev etc home lib lib64'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "3. Review current word",
    ["BRAILLE LINE:  'bin boot dev etc home lib lib64 $l'",
     "     VISIBLE:  'bin boot dev etc home lib lib64 ', cursor=1",
     "SPEECH OUTPUT: 'bin'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "4. Review next word",
    ["BRAILLE LINE:  'bin boot dev etc home lib lib64 $l'",
     "     VISIBLE:  'boot dev etc home lib lib64 $l', cursor=1",
     "SPEECH OUTPUT: 'boot'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_2"))
sequence.append(utils.AssertPresentationAction(
    "5. Review current char",
    ["BRAILLE LINE:  'bin boot dev etc home lib lib64 $l'",
     "     VISIBLE:  'boot dev etc home lib lib64 $l', cursor=1",
     "SPEECH OUTPUT: 'boot'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_6"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "6. Review item below",
    ["BRAILLE LINE:  'lost+found media mnt opt proc root run $l'",
     "     VISIBLE:  'media mnt opt proc root run $l', cursor=1",
     "SPEECH OUTPUT: 'media'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_6"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "7. Review item below",
    ["BRAILLE LINE:  'sbin srv sys tmp usr var $l'",
     "     VISIBLE:  'sbin srv sys tmp usr var $l', cursor=6",
     "SPEECH OUTPUT: 'srv'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_4"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "8. Review item above",
    ["BRAILLE LINE:  'lost+found media mnt opt proc root run $l'",
     "     VISIBLE:  'media mnt opt proc root run $l', cursor=1",
     "SPEECH OUTPUT: 'media'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_4"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "9. Review item above",
    ["BRAILLE LINE:  'bin boot dev etc home lib lib64 $l'",
     "     VISIBLE:  'boot dev etc home lib lib64 $l', cursor=1",
     "SPEECH OUTPUT: 'boot'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "10. Review next line",
    ["BRAILLE LINE:  'lost+found media mnt opt proc root run $l'",
     "     VISIBLE:  'lost+found media mnt opt proc ro', cursor=1",
     "SPEECH OUTPUT: 'lost+found media mnt opt proc root run'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "11. Review next word",
    ["BRAILLE LINE:  'lost+found media mnt opt proc root run $l'",
     "     VISIBLE:  'media mnt opt proc root run $l', cursor=1",
     "SPEECH OUTPUT: 'media'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_3"))
sequence.append(utils.AssertPresentationAction(
    "12. Review next char",
    ["BRAILLE LINE:  'lost+found media mnt opt proc root run $l'",
     "     VISIBLE:  'mnt opt proc root run $l', cursor=1",
     "SPEECH OUTPUT: 'mnt'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "13. Review previous line",
    ["BRAILLE LINE:  'bin boot dev etc home lib lib64 $l'",
     "     VISIBLE:  'bin boot dev etc home lib lib64 ', cursor=1",
     "SPEECH OUTPUT: 'bin boot dev etc home lib lib64'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "14. Review previous line",
    ["BRAILLE LINE:  'Up Home $l'",
     "     VISIBLE:  'Up Home $l', cursor=1",
     "SPEECH OUTPUT: 'Up Home'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
