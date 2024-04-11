#!/bin/bash

useage() 
{
	echo './runone.sh keystroke_file.py [application_name] [0|1]'
echo 'application_name is the name of the application to run'
echo '0 = start and stop orca inside this shell script'
echo '1 = assume orca is already running'
echo " " # for a blank line

exit 1
}

#
# Set up our accessibility environment for those apps that
# don't do it on their own.
#
export GTK_MODULES=:gail:atk-bridge:
export PATH=/usr/lib/openoffice/program:$PATH
export PS1='$ '

foo=`dirname $0`
harnessDir=`cd $foo; pwd`
export PYTHONPATH=$harnessDir:$PYTHONPATH
export PATH=$harnessDir/bin:$PATH

# Switch off i18n transformation.
export LANG=C
export LC_ALL=C

if [ "$1" = "-h" -o "$1" = "-?" -o "$1" = "--help" -o $# -eq 0 ]
then
	useage
fi

debugFile=`basename $1 .py`

cp `dirname $0`/orca-customizations.py.in orca-customizations.py
CUSTOMIZATIONS_FILE=`dirname $1`/$debugFile.customizations
if [ -f $CUSTOMIZATIONS_FILE ]
then
    cat $CUSTOMIZATIONS_FILE >> orca-customizations.py
fi

SETTINGS_FILE=`dirname $1`/$debugFile.settings
if [ ! -f $SETTINGS_FILE ]
then
    SETTINGS_FILE=`dirname $0`/user-settings.conf.in
fi
cp $SETTINGS_FILE user-settings.conf


# Allow us to pass parameters to the command line of the application.
#
# If a <testfilename>.params file exists, it contains parameters to
# pass to the command line of the application.
#
PARAMS_FILE=`dirname $1`/$debugFile.params
if [ -f $PARAMS_FILE ]
then
    if [ "x$JDK_DEMO_DIR" == "x" ]
    then
        JDK_DEMO_DIR="/usr/jdk/latest/demo"
    fi
    TEST_DIR=`dirname $1`
    source $PARAMS_FILE
fi

# Run the app (or gtk-demo if no app was given) and let it settle in.
#
ARGS=""
if [ -n "$3" ]
then
    APP_NAME=$2
    orcaRunning=$3
else
   APP_NAME=gtk-demo
   if [ -n "$2" ]
   then
       orcaRunning=$2
   else
       orcaRunning=0
   fi
fi

if [ "$APP_NAME" == "swriter" ] || [ "$APP_NAME" == "oowriter" ] || [ "$APP_NAME" == "scalc" ] || [ "$APP_NAME" == "oocalc" ] || [ "$APP_NAME" == "simpress" ] || [ "$APP_NAME" == "ooimpress" ] || [ "$APP_NAME" == "sbase" ] || [ "$APP_NAME" == "oobase" ] || [ "$APP_NAME" == "soffice" ] || [ "$APP_NAME" == "ooffice" ]
then
    SOFFICE=1
fi

# If we're using Firefox, give it a known profile to work from.
#
if [ "$APP_NAME" = "firefox" ]
then
    FF_PROFILE_DIR=/tmp/FirefoxProfile
    mkdir -p $FF_PROFILE_DIR
    cp $harnessDir/../html/FirefoxProfile/prefs.js $FF_PROFILE_DIR
    cp $harnessDir/../html/FirefoxProfile/bookmarks.html $FF_PROFILE_DIR
    cp $harnessDir/../html/FirefoxProfile/extensions.rdf $FF_PROFILE_DIR
    ARGS="-profile $FF_PROFILE_DIR -width 1000 -height 650"
fi

# Consistent profile for testing Epiphany.
#
if [ "$APP_NAME" = "epiphany" ]
then
    EWB_PROFILE_DIR=/tmp/EpiphanyProfile
    mkdir -p $EWB_PROFILE_DIR
    cp $harnessDir/../html/EpiphanyProfile/bookmarks.rdf $EWB_PROFILE_DIR
    cp $harnessDir/../html/EpiphanyProfile/states.xml $EWB_PROFILE_DIR
    ARGS="-p --profile=$EWB_PROFILE_DIR"
fi

if [ "x$SOFFICE" == "x1" ]
then
    LO_PROFILE_DIR=/tmp/soffice-profile
    ARGS="--norestore --nologo --nolockcheck -env:UserInstallation=file://$LO_PROFILE_DIR"
fi

if [ "$APP_NAME" = "gnome-terminal" ]
then
    TERMINAL_WORKING_DIR=/tmp/gnome-terminal-wd
    mkdir $TERMINAL_WORKING_DIR
    ARGS="--working-directory=$TERMINAL_WORKING_DIR"
fi

if [ $orcaRunning -eq 0 ]
then
    $harnessDir/runorca.py --user-prefs `pwd` --debug-file $debugFile &
    sleep 4
fi

# Start the test application and let it settle in. Two processes
# are started for OpenOffice.
#
echo starting test application $APP_NAME $ARGS $PARAMS ...
$APP_NAME $ARGS $PARAMS &
APP_PID=$!

# Play the keystrokes.
#
python3 $1

if [ $orcaRunning -eq 0 ]
then
    pkill -9 orca > /dev/null 2>&1
fi

# Terminate the running application
if [ "x$SOFFICE" == "x1" ]
then
    APP_PID=$(ps -eo pid,ruid,args | grep norestore | grep -v grep | awk '{ print $1 }')
    kill $APP_PID > /dev/null 2>&1
    rm -rf $LO_PROFILE_DIR
fi

if [ "$APP_NAME" == "gnome-terminal" ]
then
    pkill $APP_NAME > /dev/null 2>&1
    rm -rf $TERMINAL_WORKING_DIR
fi

if [ "$APP_NAME" == "epiphany" ]
then
    pkill epiphany > /dev/null 2>&1
    rm -rf $EWB_PROFILE_DIR
fi

if [ "$APP_NAME" == "firefox" ]
then
    pkill firefox > /dev/null 2>&1
    rm -rf $FF_PROFILE_DIR
else
    pkill $APP_NAME > /dev/null 2>&1
fi
