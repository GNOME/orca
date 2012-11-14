m4_define([orca_major_version], [3])
m4_define([orca_minor_version], [6])
m4_define([orca_micro_version], [3])
m4_define([orca_version],
          [orca_major_version.orca_minor_version.orca_micro_version])

m4_define(gtk_required_version, 3.5.16)
m4_define(pygobject_required_version, 3.2.2)
m4_define(atspi_required_version, 2.5.91)
m4_define(atkbridge_required_version, 2.5.91)
m4_define(atk_required_version, 2.5.91)

AC_INIT([orca],
        [orca_version],
        [http://bugzilla.gnome.org/enter_bug.cgi?product=orca],
        [orca])

AC_CONFIG_MACRO_DIR([m4])

AM_INIT_AUTOMAKE([1.11 tar-ustar no-dist-gzip dist-xz])
AM_MAINTAINER_MODE([enable])

dnl Gettext stuff
IT_PROG_INTLTOOL([0.40.0])

AM_GNU_GETTEXT_VERSION([0.17])
AM_GNU_GETTEXT([external])

GETTEXT_PACKAGE=AC_PACKAGE_TARNAME
AC_SUBST(GETTEXT_PACKAGE)
AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE,"$GETTEXT_PACKAGE", [gettext package])

# User Documentation
YELP_HELP_INIT

PKG_CHECK_MODULES([GTK], [gtk+-3.0 >= gtk_required_version])
PKG_CHECK_MODULES([PYGOBJECT], [pygobject-3.0 >= pygobject_required_version])
PKG_CHECK_MODULES([ATSPI2], [atspi-2 >= atspi_required_version])
PKG_CHECK_MODULES([ATKBRIDGE], [atk-bridge-2.0 >= atkbridge_required_version])
PKG_CHECK_MODULES([ATK], [atk >= atk_required_version])

dnl Needed programs
AC_PROG_INSTALL

dnl Check for python and python modules needed by Orca
dnl TODO: check for incompatibilities between Orca and liblouis
dnl per http://live.gnome.org/Orca/Braille
AM_PATH_PYTHON(2.7)
#AM_CHECK_PYMOD(gobject,,,[AC_MSG_ERROR(Could not find python module: gobject)])
# Don't require the DISPLAY to be set - the gtk checking will fail 
# if DISPLAY is not set, and we don't like that.

AM_CHECK_PYMOD(cairo,,,[AC_MSG_ERROR(Could not find python module: cairo)])
AM_CHECK_PYMOD(json,,,[AC_MSG_ERROR(Could not find python module: json)])
AM_CHECK_PYMOD(brlapi,,[brlapi_available="yes"],[brlapi_available="no"])
AM_CHECK_PYMOD(speechd,,[speechd_available="yes"],[speechd_available="no"])
LOUIS_TABLE_DIR=""
AM_CHECK_PYMOD(louis,,[louis_available="yes"],[louis_available="no"])
if test x$louis_available = "xyes"; then
  LOUIS_TABLE_DIR=`pkg-config --variable=tablesdir liblouis`
fi
AC_SUBST(LOUIS_TABLE_DIR)

dnl Check for the OS. On *Solaris systems the PATH must be set
PLATFORM=`uname -a`
case "${PLATFORM}" in
    *SunOS*)
            PLATFORM_PATH=":/usr/ccs/bin:/usr/bin:/usr/sbin:/bin:/usr/sfw/bin:/usr/openwin/bin:/usr/X11R6/bin"
            ;;
    *Linux*)
            PLATFORM_PATH=":/usr/bin:/usr/sbin:/bin"
            ;;
esac
AC_SUBST(PLATFORM_PATH)

AC_OUTPUT([ 
run_pylint.sh
Makefile
docs/Makefile
docs/man/Makefile
po/Makefile.in
help/Makefile
icons/Makefile
src/Makefile
src/orca/Makefile
src/orca/scripts/Makefile
src/orca/scripts/apps/Makefile
src/orca/scripts/apps/acroread/Makefile
src/orca/scripts/apps/Banshee/Makefile
src/orca/scripts/apps/ddu/Makefile
src/orca/scripts/apps/Eclipse/Makefile
src/orca/scripts/apps/ekiga/Makefile
src/orca/scripts/apps/empathy/Makefile
src/orca/scripts/apps/evolution/Makefile
src/orca/scripts/apps/gajim/Makefile
src/orca/scripts/apps/gcalctool/Makefile
src/orca/scripts/apps/gdmlogin/Makefile
src/orca/scripts/apps/gdm-simple-greeter/Makefile
src/orca/scripts/apps/gedit/Makefile
src/orca/scripts/apps/gnome_segv2/Makefile
src/orca/scripts/apps/gnome-keyring-ask/Makefile
src/orca/scripts/apps/gnome-mud/Makefile
src/orca/scripts/apps/gnome-panel/Makefile
src/orca/scripts/apps/gnome-screensaver-dialog/Makefile
src/orca/scripts/apps/gnome-search-tool/Makefile
src/orca/scripts/apps/gnome-system-monitor/Makefile
src/orca/scripts/apps/gnome-terminal/Makefile
src/orca/scripts/apps/gnome-window-properties/Makefile
src/orca/scripts/apps/gtk-window-decorator/Makefile
src/orca/scripts/apps/Instantbird/Makefile
src/orca/scripts/apps/liferea/Makefile
src/orca/scripts/apps/metacity/Makefile
src/orca/scripts/apps/notification-daemon/Makefile
src/orca/scripts/apps/notify-osd/Makefile
src/orca/scripts/apps/nautilus/Makefile
src/orca/scripts/apps/Mozilla/Makefile
src/orca/scripts/apps/packagemanager/Makefile
src/orca/scripts/apps/pidgin/Makefile
src/orca/scripts/apps/planner/Makefile
src/orca/scripts/apps/rhythmbox/Makefile
src/orca/scripts/apps/soffice/Makefile
src/orca/scripts/apps/Thunderbird/Makefile
src/orca/scripts/apps/xfwm4/Makefile
src/orca/scripts/toolkits/Makefile
src/orca/scripts/toolkits/Gecko/Makefile
src/orca/scripts/toolkits/J2SE-access-bridge/Makefile
src/orca/scripts/toolkits/CALLY/Makefile
src/orca/scripts/toolkits/WebKitGtk/Makefile
src/orca/backends/Makefile
src/orca/orca_bin.py
src/orca/orca_i18n.py
src/orca/orca_platform.py
],[chmod +x run_pylint.sh ; cp src/orca/orca_bin.py src/orca/orca])

if test "x$brlapi_available" = "xno" ; then
echo
echo "NOTE: Braille support requires BrlTTY >= 3.9 and BrlAPI >= 0.5.1."
fi
if test "x$wnck_available" = "xno" ; then
echo
echo "NOTE: Mouse review requires wnck, which was not found."
fi
echo
echo Use speech-dispatcher: $speechd_available
echo Use brltty: $brlapi_available
echo Use liblouis: $louis_available
echo
