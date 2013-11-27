#!/bin/bash

useage() 
{
	echo './runone.sh keystroke_file.py [application_name] [0|1]'
echo 'application_name is the name of the application to run'
echo '0 = start and stop orca inside this shell script'
echo '1 = assume orca is already running'
echo " " # for a blank line
	echo 'See http://live.gnome.org/Orca/RegressionTesting for more info.'

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

#echo runone.sh: $*

debugFile=`basename $1 .py`

# Number of seconds to wait for Orca and the application to start
#
WAIT_TIME=10

# Set up the stuff we want to always be set for every test, regardless
# if there is a *.params file for the test or not.
#
currentDir=`pwd`

cp `dirname $0`/orca-customizations.py.in orca-customizations.py

# If a <testfilename>.customizations file exists, add those settings to
# what is specified in the default orca-customizations-py.in.
#
CUSTOMIZATIONS_FILE=`dirname $1`/$debugFile.customizations
if [ -f $CUSTOMIZATIONS_FILE ]
then
    cat $CUSTOMIZATIONS_FILE >> orca-customizations.py
fi
cat >> orca-customizations.py << EOF

orca.settings.userPrefsDir = '$currentDir'

if not orca.debug.debugFile:
    orca.debug.debugFile = open('$debugFile.debug', 'w')

    import logging
    for logger in ['braille', 'speech']:
        log = logging.getLogger(logger)
        formatter = logging.Formatter('%(name)s.%(message)s')
        handler = logging.FileHandler('$debugFile.%s' % logger, 'w')
        handler.setFormatter(formatter)
        log.addHandler(handler)
        log.setLevel(logging.INFO)

EOF

# Set up our local user settings file for the output format we want.
#
# If a <testfilename>.settings file exists, should use that instead of
# the default user-settings.conf.in.
#
# (Orca will look in our local directory first for user-settings.conf
# before looking in the usual location)
#
SETTINGS_FILE=`dirname $1`/$debugFile.settings
if [ ! -f $SETTINGS_FILE ]
then
    SETTINGS_FILE=`dirname $0`/user-settings.conf.in
fi
cp $SETTINGS_FILE user-settings.conf
#echo "Using settings file:" $SETTINGS_FILE

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

# FIXME(LMS): Temporary hack to tell OpenOffice Writer and Calc
# to not attempt to recover edited files after a crash. There
# should be a general way specify command line arguments when
# starting test applications.
#
if [ "$APP_NAME" == "swriter" ] || [ "$APP_NAME" == "oowriter" ] || [ "$APP_NAME" == "scalc" ] || [ "$APP_NAME" == "oocalc" ] || [ "$APP_NAME" == "simpress" ] || [ "$APP_NAME" == "ooimpress" ] || [ "$APP_NAME" == "sbase" ] || [ "$APP_NAME" == "oobase" ] || [ "$APP_NAME" == "soffice" ] || [ "$APP_NAME" == "ooffice" ]
then
    SOFFICE=1
    ARGS="-norestore"
fi

# If we're using Firefox, give it a known profile to work from.
#
if [ "$APP_NAME" = "firefox" ]
then
    FF_PROFILE_DIR=/tmp/FirefoxProfile
    mkdir -p $FF_PROFILE_DIR
    cp $harnessDir/../html/FirefoxProfile/prefs.js $FF_PROFILE_DIR
    cp $harnessDir/../html/FirefoxProfile/localstore.rdf $FF_PROFILE_DIR
    cp $harnessDir/../html/FirefoxProfile/bookmarks.html $FF_PROFILE_DIR
    cp $harnessDir/../html/FirefoxProfile/extensions.rdf $FF_PROFILE_DIR
    ARGS="-profile $FF_PROFILE_DIR"
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

if [ $orcaRunning -eq 0 ]
then
    # Run orca and let it settle in.
    #echo starting Orca...
    orca --user-prefs `pwd`&
    sleep $WAIT_TIME
fi

# Start the test application and let it settle in. Two processes
# are started for OpenOffice.
#
echo starting test application $APP_NAME $ARGS $PARAMS ...
$APP_NAME $ARGS $PARAMS &
#sleep $WAIT_TIME
APP_PID=$!

#echo $APP_NAME pid $APP_PID

# Play the keystrokes.
#
python3 $1

# Let things settle for a couple seconds...
#
#sleep $WAIT_TIME

if [ $orcaRunning -eq 0 ]
then
    # Terminate Orca
    #echo terminating Orca
    pkill -9 orca > /dev/null 2>&1
fi

# Terminate the running application
if [ "x$SOFFICE" == "x1" ]
then
    APP_PID=$(ps -eo pid,ruid,args | grep norestore | grep -v grep | awk '{ print $1 }')
fi

if [ "$APP_NAME" == "epiphany" ]
then
    pkill epiphany > /dev/null 2>&1
    rm -rf $EWB_PROFILE_DIR
fi

if [ "$APP_NAME" == "firefox" ]
then
    #echo killing firefox
    pkill firefox > /dev/null 2>&1
    rm -rf $FF_PROFILE_DIR
else
    #echo killing app $APP_NAME $APP_PID
    kill -9 $APP_PID > /dev/null 2>&1
fi

# Temporary hack to kill gnome-help help if it's running.
HELP_PID=$(ps -A | grep gnome-help | cut -d' ' -f1)
kill -9 $HELP_PID > /dev/null 2>&1
