#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(TypeAction("man orca"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "1. Return",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
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
sequence.append(KeyComboAction("space"))
sequence.append(utils.AssertPresentationAction(
    "2. Space",
    ["BRAILLE LINE:  ' Manual page orca(1) line 24 (press h for help or q to quit)'",
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
sequence.append(KeyComboAction("<Control>b"))
sequence.append(utils.AssertPresentationAction(
    "3. Ctrl+b",
    ["BRAILLE LINE:  ' Manual page orca(1) line 1 (press h for help or q to quit)'",
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
sequence.append(KeyComboAction("<Control>f"))
sequence.append(utils.AssertPresentationAction(
    "4. Ctrl+f",
    ["BRAILLE LINE:  ' Manual page orca(1) line 24 (press h for help or q to quit)'",
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
sequence.append(KeyComboAction("b"))
sequence.append(utils.AssertPresentationAction(
    "5. b",
    ["BRAILLE LINE:  ' Manual page orca(1) line 1 (press h for help or q to quit)'",
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
sequence.append(KeyComboAction("f"))
sequence.append(utils.AssertPresentationAction(
    "6. f",
    ["BRAILLE LINE:  ' Manual page orca(1) line 24 (press h for help or q to quit)'",
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
sequence.append(KeyComboAction("g"))
sequence.append(utils.AssertPresentationAction(
    "7. g",
    ["BRAILLE LINE:  ' Manual page orca(1) line 1 (press h for help or q to quit)'",
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
sequence.append(KeyComboAction("<Shift>g"))
sequence.append(utils.AssertPresentationAction(
    "8. Shift+g",
    ["BRAILLE LINE:  ' Manual page orca(1) line 240/262 (END) (press h for help or q to quit)'",
     "     VISIBLE:  'or q to quit\)', cursor=14",
     "SPEECH OUTPUT: '       ~/.local/share/orca/orca-scripts",
     "              Orca user orca scripts directory",
     "",
     "       ~/.local/share/orca/bookmarks",
     "              Orca user bookmarks directory",
     "",
     "       ~/.local/share/orca/app-settings",
     "              Orca user application specific settings directory",
     "",
     "AUTHOR",
     "       Orca  originated as a community effort led by the Sun Microsystems Inc.",
     "       Accessibility Program Office and with contributions from many community",
     "       members.",
     "",
     "SEE ALSO",
     "       For     more     information     please     visit    orca    wiki    at",
     "       <http://live.gnome.org/Orca> <http://live.gnome.org/Orca>",
     "",
     "       The  orca  mailing  list  <http://mail.gnome.org/mailman/listinfo/orca-",
     "       list>  To  post  a  message  to  all  orca  list, send a email to orca-",
     "       list@gnome.org",
     "",
     "GNOME                          20 September 2013                       orca(1)",
     " Manual page orca(1) line 240/262 (END) (press h for help or q to quit)'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
