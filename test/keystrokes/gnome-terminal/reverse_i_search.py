#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()
sequence.append(PauseAction(3000))
sequence.append(TypeAction("echo hello world"))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("echo hey guys"))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("echo goodbye world"))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("cat foo"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>r"))
sequence.append(utils.AssertPresentationAction(
    "1. Ctrl+R",
    ["BRAILLE LINE:  '(reverse-i-search)`': '",
     "     VISIBLE:  '(reverse-i-search)`': ', cursor=23",
     "SPEECH OUTPUT: '(reverse-i-search)`':'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("c"))
sequence.append(utils.AssertPresentationAction(
    "2. Type 'c'",
    ["BRAILLE LINE:  '(reverse-i-search)`c': cat foo'",
     "     VISIBLE:  '(reverse-i-search)`c': cat foo', cursor=24",
     "SPEECH OUTPUT: 'c': cat foo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("a"))
sequence.append(utils.AssertPresentationAction(
    "3. Type 'a'",
    ["BRAILLE LINE:  '(reverse-i-search)`ca': cat foo'",
     "     VISIBLE:  '(reverse-i-search)`ca': cat foo', cursor=25",
     "BRAILLE LINE:  '(reverse-i-search)`ca': cat foo'",
     "     VISIBLE:  '(reverse-i-search)`ca': cat foo', cursor=25"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "4. BackSpace",
    ["BRAILLE LINE:  '(reverse-i-search)`c': cat foo'",
     "     VISIBLE:  '(reverse-i-search)`c': cat foo', cursor=24",
     "BRAILLE LINE:  '(reverse-i-search)`c': cat foo'",
     "     VISIBLE:  '(reverse-i-search)`c': cat foo', cursor=24",
     "SPEECH OUTPUT: 'a'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "5. BackSpace",
    ["BRAILLE LINE:  '(failed reverse-i-search)`': cat foo'",
     "     VISIBLE:  '(failed reverse-i-search)`': cat', cursor=30",
     "BRAILLE LINE:  '(failed reverse-i-search)`': cat foo'",
     "     VISIBLE:  '(failed reverse-i-search)`': cat', cursor=30",
     "BRAILLE LINE:  '(failed reverse-i-search)`': cat foo'",
     "     VISIBLE:  '(failed reverse-i-search)`': cat', cursor=30",
     "SPEECH OUTPUT: 'reverse-i-search)`c'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("e"))
sequence.append(utils.AssertPresentationAction(
    "6. Type 'e'",
    ["BRAILLE LINE:  '(reverse-i-search)`e': echo goodbye world'",
     "     VISIBLE:  'verse-i-search)`e': echo goodbye', cursor=32",
     "SPEECH OUTPUT: 'reverse-i-search)`e': echo goodbye world'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("cho "))
sequence.append(utils.AssertPresentationAction(
    "7. Type 'cho '",
    ["BRAILLE LINE:  '(reverse-i-search)`ec': echo goodbye world'",
     "     VISIBLE:  'verse-i-search)`ec': echo goodby', cursor=22",
     "BRAILLE LINE:  '(reverse-i-search)`ec': echo goodbye world'",
     "     VISIBLE:  'verse-i-search)`ec': echo goodby', cursor=22",
     "BRAILLE LINE:  '(reverse-i-search)`ech': echo goodbye world'",
     "     VISIBLE:  'verse-i-search)`ech': echo goodb', cursor=23",
     "BRAILLE LINE:  '(reverse-i-search)`ech': echo goodbye world'",
     "     VISIBLE:  'verse-i-search)`ech': echo goodb', cursor=23",
     "BRAILLE LINE:  '(reverse-i-search)`echo': echo goodbye world'",
     "     VISIBLE:  'verse-i-search)`echo': echo good', cursor=24",
     "BRAILLE LINE:  '(reverse-i-search)`echo': echo goodbye world'",
     "     VISIBLE:  'verse-i-search)`echo': echo good', cursor=24",
     "BRAILLE LINE:  '(reverse-i-search)`echo ': echo goodbye world'",
     "     VISIBLE:  'verse-i-search)`echo ': echo goo', cursor=25",
     "BRAILLE LINE:  '(reverse-i-search)`echo ': echo goodbye world'",
     "     VISIBLE:  'verse-i-search)`echo ': echo goo', cursor=25"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("he"))
sequence.append(utils.AssertPresentationAction(
    "8. Type 'he'",
    ["BRAILLE LINE:  '(reverse-i-search)`echo h': echo hey guys'",
     "     VISIBLE:  'verse-i-search)`echo h': echo he', cursor=26",
     "BRAILLE LINE:  '(reverse-i-search)`echo he': echo hey guys'",
     "     VISIBLE:  'verse-i-search)`echo he': echo h', cursor=27",
     "BRAILLE LINE:  '(reverse-i-search)`echo he': echo hey guys'",
     "     VISIBLE:  'verse-i-search)`echo he': echo h', cursor=27",
     "SPEECH OUTPUT: 'h': echo hey guys'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("l"))
sequence.append(utils.AssertPresentationAction(
    "9. Type 'l'",
    ["BRAILLE LINE:  '(reverse-i-search)`echo hel': echo hello world'",
     "     VISIBLE:  'verse-i-search)`echo hel': echo ', cursor=28",
     "SPEECH OUTPUT: 'l': echo hello world'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
