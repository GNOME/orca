#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(TypeAction("man orca"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "1. Review current line",
    ["BRAILLE LINE:  ' Manual page orca(1) line 1 (press h for help or q to quit) $l'",
     "     VISIBLE:  ' (press h for help or q to quit)', cursor=32",
     "SPEECH OUTPUT: ' Manual page orca(1) line 1 (press h for help or q to quit)",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "2. Review previous line",
    ["BRAILLE LINE:  '              When starting orca, initiate the GUI-based configuration. $l'",
     "     VISIBLE:  '              When starting orca', cursor=1",
     "SPEECH OUTPUT: '              When starting orca, initiate the GUI-based configuration.",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "3. Review previous line",
    ["BRAILLE LINE:  '       -s, --setup $l'",
     "     VISIBLE:  '       -s, --setup $l', cursor=1",
     "SPEECH OUTPUT: '       -s, --setup",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "4. Review next line",
    ["BRAILLE LINE:  '              When starting orca, initiate the GUI-based configuration. $l'",
     "     VISIBLE:  '              When starting orca', cursor=1",
     "SPEECH OUTPUT: '              When starting orca, initiate the GUI-based configuration.",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_7"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "5. Review first line",
    ["BRAILLE LINE:  'File Edit View Search Terminal Help $l'",
     "     VISIBLE:  'File Edit View Search Terminal H', cursor=1",
     "SPEECH OUTPUT: 'File Edit View Search Terminal Help'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "6. Review next line",
    ["BRAILLE LINE:  'orca(1)                     General Commands Manual                    orca(1) $l'",
     "     VISIBLE:  'orca(1)                     Gene', cursor=1",
     "SPEECH OUTPUT: 'orca(1)                     General Commands Manual                    orca(1)",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "7. Review next line",
    ["BRAILLE LINE:  'vertical scroll bar 3% $l'",
     "     VISIBLE:  'vertical scroll bar 3% $l', cursor=1",
     "SPEECH OUTPUT: 'vertical scroll bar 3 percent.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "8. Review next line",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "9. Review next line",
    ["BRAILLE LINE:  'NAME $l'",
     "     VISIBLE:  'NAME $l', cursor=1",
     "SPEECH OUTPUT: 'NAME",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "10. Review next line",
    ["BRAILLE LINE:  '       orca - a scriptable screen reader $l'",
     "     VISIBLE:  '       orca - a scriptable scree', cursor=1",
     "SPEECH OUTPUT: '       orca - a scriptable screen reader",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>f"))
sequence.append(utils.AssertPresentationAction(
    "11. Forward one page",
    ["BRAILLE LINE:  ' Manual page orca(1) line 24 (press h for help or q to quit)'",
     "     VISIBLE:  '(press h for help or q to quit)', cursor=32",
     "BRAILLE LINE:  ' Manual page orca(1) line 24 (press h for help or q to quit)'",
     "     VISIBLE:  '(press h for help or q to quit)', cursor=32",
     "BRAILLE LINE:  ' Manual page orca(1) line 24 (press h for help or q to quit)'",
     "     VISIBLE:  '(press h for help or q to quit)', cursor=32",
     "BRAILLE LINE:  ' Manual page orca(1) line 24 (press h for help or q to quit)'",
     "     VISIBLE:  '(press h for help or q to quit)', cursor=32",
     "SPEECH OUTPUT: '              When starting orca, use dirname as an  alternate  directory  for",
     "              the user preferences.",
     "",
     "       -e, --enable=speech|braille|braille-monitor",
     "              When starting orca, force the enabling of the supplied options.",
     "",
     "       -d, --disable=speech|braille|braille-monitor",
     "              When starting orca, force the disabling of the supplied options.",
     "",
     "       -l, --list-apps",
     "              Prints  the  names  of  all  the currently running applications.",
     "              This is used primarily for debugging purposes to see if orca can",
     "              talk  to the accessibility infrastructure.  Note that if orca is",
     "              already running, this will not kill the other orca process.   It",
     "              will  just list the currently running applications, and you will",
     "              see orca listed twice: once for the existing orca and  once  for",
     "              this instance.",
     "",
     "       --debug",
     "              Enables  debug  output  for orca and sends all debug output to a",
     "              file with a name of the form 'debug-YYYY-MM-DD-HH:MM:SS.out'  in",
     " Manual page orca(1) line 24 (press h for help or q to quit)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "12. Review current line",
    ["KNOWN ISSUE: We currently deliberately exit flat review and return to the bottom of the window",
    "BRAILLE LINE:  ' Manual page orca(1) line 24 (press h for help or q to quit) $l'",
     "     VISIBLE:  ' (press h for help or q to quit)', cursor=32",
     "SPEECH OUTPUT: ' Manual page orca(1) line 24 (press h for help or q to quit)",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "13. Review previous line",
    ["BRAILLE LINE:  '              file with a name of the form 'debug-YYYY-MM-DD-HH:MM:SS.out'  in $l'",
     "     VISIBLE:  '              file with a name o', cursor=1",
     "SPEECH OUTPUT: '              file with a name of the form 'debug-YYYY-MM-DD-HH:MM:SS.out'  in",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "14. Review previous line",
    ["BRAILLE LINE:  '              Enables  debug  output  for orca and sends all debug output to a $l'",
     "     VISIBLE:  '              Enables  debug  ou', cursor=1",
     "SPEECH OUTPUT: '              Enables  debug  output  for orca and sends all debug output to a",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_7"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "15. Review first line",
    ["BRAILLE LINE:  'File Edit View Search Terminal Help $l'",
     "     VISIBLE:  'File Edit View Search Terminal H', cursor=1",
     "SPEECH OUTPUT: 'File Edit View Search Terminal Help'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "16. Review next line",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "17. Review next line",
    ["BRAILLE LINE:  'vertical scroll bar 26% $l'",
     "     VISIBLE:  'vertical scroll bar 26% $l', cursor=1",
     "SPEECH OUTPUT: 'vertical scroll bar 26 percent.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "18. Review next line",
    ["BRAILLE LINE:  '       -u, --user-prefs-dir=dirname $l'",
     "     VISIBLE:  '       -u, --user-prefs-dir=dirn', cursor=1",
     "SPEECH OUTPUT: '       -u, --user-prefs-dir=dirname",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>b"))
sequence.append(utils.AssertPresentationAction(
    "19. Back one page",
    ["BRAILLE LINE:  ' Manual page orca(1) line 1 (press h for help or q to quit)'",
     "     VISIBLE:  '(press h for help or q to quit)', cursor=32",
     "BRAILLE LINE:  ' Manual page orca(1) line 1 (press h for help or q to quit)'",
     "     VISIBLE:  '(press h for help or q to quit)', cursor=32",
     "BRAILLE LINE:  ' Manual page orca(1) line 1 (press h for help or q to quit)'",
     "     VISIBLE:  '(press h for help or q to quit)', cursor=32",
     "SPEECH OUTPUT: 'orca(1)                     General Commands Manual                    orca(1)",
     "",
     "NAME",
     "       orca - a scriptable screen reader",
     "",
     "SYNOPSIS",
     "       orca [option...]",
     "",
     "DESCRIPTION",
     "       orca is a screen reader for people with visual impairments, it provides",
     "       alternative access  to  the  desktop  by  using  speech  synthesis  and",
     "       braille.",
     "",
     "       orca  works  with  applications and toolkits that support the Assistive",
     "       Technology Service Provider Interface (AT-SPI), which  is  the  primary",
     "       assistive technology infrastructure for Linux and Solaris. Applications",
     "       and toolkits supporting the AT-SPI include the GNOME Gtk+ toolkit,  the",
     "       Java  platform's  Swing toolkit, LibreOffice, Gecko, and WebKitGtk. AT-",
     "       SPI support for the KDE Qt toolkit is being pursued.",
     "",
     "OPTIONS",
     "       -s, --setup",
     "              When starting orca, initiate the GUI-based configuration.",
     " Manual page orca(1) line 1 (press h for help or q to quit)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "20. Review current line",
    ["BRAILLE LINE:  ' Manual page orca(1) line 1 (press h for help or q to quit) $l'",
     "     VISIBLE:  ' (press h for help or q to quit)', cursor=32",
     "SPEECH OUTPUT: ' Manual page orca(1) line 1 (press h for help or q to quit)",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "21. Review previous line",
    ["BRAILLE LINE:  '              When starting orca, initiate the GUI-based configuration. $l'",
     "     VISIBLE:  '              When starting orca', cursor=1",
     "SPEECH OUTPUT: '              When starting orca, initiate the GUI-based configuration.",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "22. Review previous line",
    ["BRAILLE LINE:  '       -s, --setup $l'",
     "     VISIBLE:  '       -s, --setup $l', cursor=1",
     "SPEECH OUTPUT: '       -s, --setup",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_7"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "23. Review first line",
    ["BRAILLE LINE:  'File Edit View Search Terminal Help $l'",
     "     VISIBLE:  'File Edit View Search Terminal H', cursor=1",
     "SPEECH OUTPUT: 'File Edit View Search Terminal Help'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "24. Review next line",
    ["BRAILLE LINE:  'orca(1)                     General Commands Manual                    orca(1) $l'",
     "     VISIBLE:  'orca(1)                     Gene', cursor=1",
     "SPEECH OUTPUT: 'orca(1)                     General Commands Manual                    orca(1)",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "25. Review next line",
    ["BRAILLE LINE:  'vertical scroll bar 26% $l'",
     "     VISIBLE:  'vertical scroll bar 26% $l', cursor=1",
     "SPEECH OUTPUT: 'vertical scroll bar 26 percent.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "26. Review next line",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "27. Review next line",
    ["BRAILLE LINE:  'NAME $l'",
     "     VISIBLE:  'NAME $l', cursor=1",
     "SPEECH OUTPUT: 'NAME",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "28. Review next line",
    ["BRAILLE LINE:  '       orca - a scriptable screen reader $l'",
     "     VISIBLE:  '       orca - a scriptable scree', cursor=1",
     "SPEECH OUTPUT: '       orca - a scriptable screen reader",
     "'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
