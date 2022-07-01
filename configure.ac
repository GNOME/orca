m4_define([orca_version], [41.4])

m4_define(pygobject_required_version, 3.18)
m4_define(atspi_required_version, 2.26)
m4_define(atkbridge_required_version, 2.26)

AC_INIT([orca],
        [orca_version],
        [https://gitlab.gnome.org/GNOME/orca/-/issues/],
        [orca])

AC_CONFIG_MACRO_DIR([m4])

AM_INIT_AUTOMAKE([1.11 tar-ustar no-dist-gzip dist-xz])
AM_MAINTAINER_MODE([enable])

dnl Gettext stuff
# FIXME: Remove AM_GNU_GETTEXT_VERSION once autoreconf supports REQUIRE_VERSION
AM_GNU_GETTEXT_VERSION([0.19.8])
AM_GNU_GETTEXT_REQUIRE_VERSION([0.19.8])
AM_GNU_GETTEXT([external])

GETTEXT_PACKAGE=AC_PACKAGE_TARNAME
AC_SUBST(GETTEXT_PACKAGE)
AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE,"$GETTEXT_PACKAGE", [gettext package])

# User Documentation
YELP_HELP_INIT

PKG_CHECK_MODULES([PYGOBJECT], [pygobject-3.0 >= pygobject_required_version])
PKG_CHECK_MODULES([ATSPI2], [atspi-2 >= atspi_required_version])
PKG_CHECK_MODULES([ATKBRIDGE], [atk-bridge-2.0 >= atkbridge_required_version])
PKG_CHECK_MODULES([GSTREAMER], [gstreamer-1.0], [gstreamer="yes"], [gstreamer="no"])

dnl Needed programs
AC_PROG_INSTALL

dnl Check for python and python modules needed by Orca
dnl TODO: check for incompatibilities between Orca and liblouis
dnl per http://live.gnome.org/Orca/Braille
AM_PATH_PYTHON(3.3)

# Don't require the DISPLAY to be set - the gtk checking will fail 
# if DISPLAY is not set, and we don't like that.

AM_CHECK_PYMOD(gi,,,[AC_MSG_ERROR(Could not find python module: gi)])
AM_CHECK_PYMOD(json,,,[AC_MSG_ERROR(Could not find python module: json)])
AM_CHECK_PYMOD(brlapi,,[brlapi_available="yes"],[brlapi_available="no"])
AM_CHECK_PYMOD(speechd,,[speechd_available="yes"],[speechd_available="no"])
AC_ARG_WITH([liblouis],
  AS_HELP_STRING([--without-liblouis], [Disable liblouis support]))

AS_IF([test "x$with_liblouis" != xno],
  [AM_CHECK_PYMOD(louis,,[louis_available="yes"],[louis_available="no"])],
  [louis_available=no])

if test "x$with_liblouis" = xyes -a "x$louis_available" = xno; then
  AC_MSG_ERROR([Liblouis was requested but could not be found])
fi

LOUIS_TABLE_DIR=""
if test x$louis_available = "xyes"; then
  LOUIS_TABLE_DIR=`pkg-config --variable=tablesdir liblouis`
fi
AC_SUBST(LOUIS_TABLE_DIR)

REVISION=`git rev-parse --short HEAD 2> /dev/null`
AC_SUBST(REVISION)

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
src/orca/scripts/apps/Banshee/Makefile
src/orca/scripts/apps/Eclipse/Makefile
src/orca/scripts/apps/ekiga/Makefile
src/orca/scripts/apps/empathy/Makefile
src/orca/scripts/apps/epiphany/Makefile
src/orca/scripts/apps/evince/Makefile
src/orca/scripts/apps/evolution/Makefile
src/orca/scripts/apps/gajim/Makefile
src/orca/scripts/apps/gcalctool/Makefile
src/orca/scripts/apps/gedit/Makefile
src/orca/scripts/apps/gnome-documents/Makefile
src/orca/scripts/apps/gnome-keyring-ask/Makefile
src/orca/scripts/apps/gnome-panel/Makefile
src/orca/scripts/apps/gnome-screensaver-dialog/Makefile
src/orca/scripts/apps/gnome-search-tool/Makefile
src/orca/scripts/apps/gnome-shell/Makefile
src/orca/scripts/apps/gnome-window-properties/Makefile
src/orca/scripts/apps/kwin/Makefile
src/orca/scripts/apps/Instantbird/Makefile
src/orca/scripts/apps/notification-daemon/Makefile
src/orca/scripts/apps/notify-osd/Makefile
src/orca/scripts/apps/Mozilla/Makefile
src/orca/scripts/apps/pidgin/Makefile
src/orca/scripts/apps/rhythmbox/Makefile
src/orca/scripts/apps/soffice/Makefile
src/orca/scripts/apps/SeaMonkey/Makefile
src/orca/scripts/apps/smuxi-frontend-gnome/Makefile
src/orca/scripts/apps/Thunderbird/Makefile
src/orca/scripts/apps/xfwm4/Makefile
src/orca/scripts/switcher/Makefile
src/orca/scripts/terminal/Makefile
src/orca/scripts/web/Makefile
src/orca/scripts/toolkits/Makefile
src/orca/scripts/toolkits/Chromium/Makefile
src/orca/scripts/toolkits/Gecko/Makefile
src/orca/scripts/toolkits/J2SE-access-bridge/Makefile
src/orca/scripts/toolkits/clutter/Makefile
src/orca/scripts/toolkits/GAIL/Makefile
src/orca/scripts/toolkits/Qt/Makefile
src/orca/scripts/toolkits/WebKitGtk/Makefile
src/orca/scripts/toolkits/gtk/Makefile
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

if test "x$speechd_available" = "xno" ; then
echo
echo "NOTE: Speech support requires speech-dispatcher >= 0.8."
fi

if test "x$gstreamer" = "xno" ; then
echo
echo "NOTE: Sound support requires gstreamer-1.0."
fi

echo
echo Use speech-dispatcher: $speechd_available
echo Use brltty: $brlapi_available
echo Use liblouis: $louis_available
echo Use gstreamer: $gstreamer
echo
