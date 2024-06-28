#!/usr/bin/python

"""Test of learn mode."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(TypeAction("h"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))

sequence.append(KeyComboAction("F1"))
sequence.append(PauseAction(2000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("k"))
sequence.append(utils.AssertPresentationAction(
    "1. k for next link",
    ["BRAILLE LINE:  ' Welcome to Orca'",
     "     VISIBLE:  ' Welcome to Orca', cursor=2",
     "BRAILLE LINE:  ' Welcome to Orca'",
     "     VISIBLE:  ' Welcome to Orca', cursor=2",
     "SPEECH OUTPUT: 'Welcome to Orca",
     "Introducing the Orca screen reader",
     " link'"]))

sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(2000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("p"))
sequence.append(utils.AssertPresentationAction(
    "2. p for next paragraph",
    ["BRAILLE LINE:  ' Orca is a free, open source, flexible, and extensible screen reader that provides access to the graphical desktop via speech and refreshable braille.'",
     "     VISIBLE:  'Orca is a free, open source, fle', cursor=1",
     "BRAILLE LINE:  ' Orca is a free, open source, flexible, and extensible screen reader that provides access to the graphical desktop via speech and refreshable braille.'",
     "     VISIBLE:  'Orca is a free, open source, fle', cursor=1",
     "SPEECH OUTPUT: 'Orca is a free, open source, flexible, and extensible screen reader that provides access to the graphical desktop via speech and refreshable braille.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("p"))
sequence.append(utils.AssertPresentationAction(
    "3. p for next paragraph",
    ["BRAILLE LINE:  ' Orca works with applications and toolkits that support the Assistive Technology Service Provider Interface (AT-SPI), which is the primary assistive technology infrastructure for Linux and Solaris. Applications and toolkits supporting the AT-SPI include the GNOME Gtk+ toolkit, the Java platform's Swing toolkit, LibreOffice, Gecko, and WebKitGtk. AT-SPI support for the KDE Qt toolkit is being pursued.'",
     "     VISIBLE:  'Orca works with applications and', cursor=1",
     "BRAILLE LINE:  ' Orca works with applications and toolkits that support the Assistive Technology Service Provider Interface (AT-SPI), which is the primary assistive technology infrastructure for Linux and Solaris. Applications and toolkits supporting the AT-SPI include the GNOME Gtk+ toolkit, the Java platform's Swing toolkit, LibreOffice, Gecko, and WebKitGtk. AT-SPI support for the KDE Qt toolkit is being pursued.'",
     "     VISIBLE:  'Orca works with applications and', cursor=1",
     "SPEECH OUTPUT: 'Orca works with applications and toolkits that support the Assistive Technology Service Provider Interface (AT-SPI), which is the primary assistive technology infrastructure for Linux and Solaris. Applications and toolkits supporting the AT-SPI include the GNOME Gtk+ toolkit, the Java platform's Swing toolkit, LibreOffice, Gecko, and WebKitGtk. AT-SPI support for the KDE Qt toolkit is being pursued.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("p"))
sequence.append(utils.AssertPresentationAction(
    "4. p for next paragraph",
    ["BRAILLE LINE:  ' To launch Orca:'",
     "     VISIBLE:  ' To launch Orca:', cursor=2",
     "BRAILLE LINE:  ' To launch Orca:'",
     "     VISIBLE:  ' To launch Orca:', cursor=2",
     "SPEECH OUTPUT: 'To launch Orca:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("p"))
sequence.append(utils.AssertPresentationAction(
    "5. p for next paragraph",
    ["BRAILLE LINE:  ' The method for configuring Orca to be launched automatically as your preferred screen reader will depend upon which desktop environment you use. For instance, in GNOME 3.x this option can be found in the Universal Access Control Center panel on the Seeing page.'",
     "     VISIBLE:  'The method for configuring Orca ', cursor=1",
     "BRAILLE LINE:  ' The method for configuring Orca to be launched automatically as your preferred screen reader will depend upon which desktop environment you use. For instance, in GNOME 3.x this option can be found in the Universal Access Control Center panel on the Seeing page.'",
     "     VISIBLE:  'The method for configuring Orca ', cursor=1",
     "SPEECH OUTPUT: 'The method for configuring Orca to be launched automatically as your preferred screen reader will depend upon which desktop environment you use. For instance, in GNOME 3.x this option can be found in the Universal Access Control Center panel on the Seeing page.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("p"))
sequence.append(utils.AssertPresentationAction(
    "6. p for next paragraph",
    ["BRAILLE LINE:  ' To toggle Orca on and off in GNOME, press Super+Alt+S.'",
     "     VISIBLE:  'To toggle Orca on and off in GNO', cursor=1",
     "BRAILLE LINE:  ' To toggle Orca on and off in GNOME, press Super+Alt+S.'",
     "     VISIBLE:  'To toggle Orca on and off in GNO', cursor=1",
     "SPEECH OUTPUT: 'To toggle Orca on and off in GNOME, press Super+Alt+S.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("p"))
sequence.append(utils.AssertPresentationAction(
    "7. p for next paragraph",
    ["BRAILLE LINE:  ' Type orca, along with any optional parameters, in a terminal window or within the Run dialog and then press Return.'",
     "     VISIBLE:  'Type orca, along with any option', cursor=1",
     "BRAILLE LINE:  ' Type orca, along with any optional parameters, in a terminal window or within the Run dialog and then press Return.'",
     "     VISIBLE:  'Type orca, along with any option', cursor=1",
     "SPEECH OUTPUT: 'Type orca, along with any optional parameters, in a terminal window or within the Run dialog and then press Return.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>p"))
sequence.append(utils.AssertPresentationAction(
    "8. shift+p for previous paragraph",
    ["BRAILLE LINE:  ' To toggle Orca on and off in GNOME, press Super+Alt+S.'",
     "     VISIBLE:  'To toggle Orca on and off in GNO', cursor=1",
     "BRAILLE LINE:  ' To toggle Orca on and off in GNOME, press Super+Alt+S.'",
     "     VISIBLE:  'To toggle Orca on and off in GNO', cursor=1",
     "SPEECH OUTPUT: 'To toggle Orca on and off in GNOME, press Super+Alt+S.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>p"))
sequence.append(utils.AssertPresentationAction(
    "9. shift+p for previous paragraph",
    ["BRAILLE LINE:  ' The method for configuring Orca to be launched automatically as your preferred screen reader will depend upon which desktop environment you use. For instance, in GNOME 3.x this option can be found in the Universal Access Control Center panel on the Seeing page.'",
     "     VISIBLE:  'The method for configuring Orca ', cursor=1",
     "BRAILLE LINE:  ' The method for configuring Orca to be launched automatically as your preferred screen reader will depend upon which desktop environment you use. For instance, in GNOME 3.x this option can be found in the Universal Access Control Center panel on the Seeing page.'",
     "     VISIBLE:  'The method for configuring Orca ', cursor=1",
     "SPEECH OUTPUT: 'The method for configuring Orca to be launched automatically as your preferred screen reader will depend upon which desktop environment you use. For instance, in GNOME 3.x this option can be found in the Universal Access Control Center panel on the Seeing page.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>p"))
sequence.append(utils.AssertPresentationAction(
    "10. shift+p for previous paragraph",
    ["BRAILLE LINE:  ' To launch Orca:'",
     "     VISIBLE:  ' To launch Orca:', cursor=2",
     "BRAILLE LINE:  ' To launch Orca:'",
     "     VISIBLE:  ' To launch Orca:', cursor=2",
     "SPEECH OUTPUT: 'To launch Orca:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>p"))
sequence.append(utils.AssertPresentationAction(
    "11. shift+p for previous paragraph",
    ["BRAILLE LINE:  ' Orca works with applications and toolkits that support the Assistive Technology Service Provider Interface (AT-SPI), which is the primary assistive technology infrastructure for Linux and Solaris. Applications and toolkits supporting the AT-SPI include the GNOME Gtk+ toolkit, the Java platform's Swing toolkit, LibreOffice, Gecko, and WebKitGtk. AT-SPI support for the KDE Qt toolkit is being pursued.'",
     "     VISIBLE:  'Orca works with applications and', cursor=1",
     "BRAILLE LINE:  ' Orca works with applications and toolkits that support the Assistive Technology Service Provider Interface (AT-SPI), which is the primary assistive technology infrastructure for Linux and Solaris. Applications and toolkits supporting the AT-SPI include the GNOME Gtk+ toolkit, the Java platform's Swing toolkit, LibreOffice, Gecko, and WebKitGtk. AT-SPI support for the KDE Qt toolkit is being pursued.'",
     "     VISIBLE:  'Orca works with applications and', cursor=1",
     "SPEECH OUTPUT: 'Orca works with applications and toolkits that support the Assistive Technology Service Provider Interface (AT-SPI), which is the primary assistive technology infrastructure for Linux and Solaris. Applications and toolkits supporting the AT-SPI include the GNOME Gtk+ toolkit, the Java platform's Swing toolkit, LibreOffice, Gecko, and WebKitGtk. AT-SPI support for the KDE Qt toolkit is being pursued.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>p"))
sequence.append(utils.AssertPresentationAction(
    "12. shift+p for previous paragraph",
    ["BRAILLE LINE:  ' Orca is a free, open source, flexible, and extensible screen reader that provides access to the graphical desktop via speech and refreshable braille.'",
     "     VISIBLE:  'Orca is a free, open source, fle', cursor=1",
     "BRAILLE LINE:  ' Orca is a free, open source, flexible, and extensible screen reader that provides access to the graphical desktop via speech and refreshable braille.'",
     "     VISIBLE:  'Orca is a free, open source, fle', cursor=1",
     "SPEECH OUTPUT: 'Orca is a free, open source, flexible, and extensible screen reader that provides access to the graphical desktop via speech and refreshable braille.'"]))

sequence.append(KeyComboAction("<Alt>F4"))
sequence.append(utils.AssertionSummaryAction())
sequence.start()
