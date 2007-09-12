#!/bin/bash
#
# runone.sh takes the following parameters:
#
#    keystroke_file.py [application_name] [0|1]
#
# where:
#
#    application_name is the name of the application to run
#    0 = start and stop orca inside this shell script
#    1 = assume orca is already running
#
# Set up our accessibility environment for those apps that
# don't do it on their own.
#
export GTK_MODULES=:gail:atk-bridge:
export PATH=/usr/lib/openoffice/program:$PATH
export PS1='$ '

echo runone.sh: $*

debugFile=`basename $1 .py`

# Number of seconds to wait for Orca and the application to start
#
WAIT_TIME=5

# Set up our local user settings file for the output format we want.
#
# If a <testfilename>.settings file exists, should use that instead of
# the default user-settings.py.in.
# We still need to run sed on it, to adjust the debug filename and
# create a user-settings.py file in the tmp directory.
#
# (Orca will look in our local directory first for user-settings.py
# before looking in ~/.orca)
#
SETTINGS_FILE=`dirname $1`/$debugFile.settings
if [ ! -f $SETTINGS_FILE ]
then
    SETTINGS_FILE=`dirname $0`/user-settings.py.in
fi
echo "Using settings file:" $SETTINGS_FILE

# Set up the logging stuff so we can record what Orca is doing.
#
cp $SETTINGS_FILE user-settings.py
cat >> user-settings.py <<EOF

orca.settings.asyncMode = False

orca.debug.debugLevel = orca.debug.LEVEL_ALL
orca.debug.debugFile = open('$debugFile.debug', 'w', 0)

import logging
for logger in ['braille', 'speech']:
    log = logging.getLogger(logger)
    formatter = logging.Formatter('%(name)s.%(message)s')
    handler = logging.FileHandler('$debugFile.%s' % logger)
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(logging.INFO)
EOF

# Allow us to pass parameters to the command line of the application.
#
# If a <testfilename>.params file exists, it contains parameters to
# pass to the command line of the application.
#
PARAMS_FILE=`dirname $1`/$debugFile.params
if [ -f $PARAMS_FILE ]
then
    PARAMS=`cat $PARAMS_FILE`
fi

# Run the app (or gnome-terminal if no app was given) and let it settle in.
#
ARGS=""
if [ -n "$3" ]
then
    APP_NAME=$2
    orcaRunning=$3
else
   APP_NAME=gnome-terminal
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
if [ "$APP_NAME" = "swriter" ] || [ "$APP_NAME" = "scalc" ] || [ "$APP_NAME" = "soffice" ]
then
    ARGS="-norestore"
fi

if [ $orcaRunning -eq 0 ]
then
    # Run orca and let it settle in.
    echo starting Orca...
    orca &
    sleep $WAIT_TIME
fi

# Don't let gnome-terminal change the title on us -- it wreaks havoc
# on the output.
#
if [ "$APP_NAME" = "gnome-terminal" ]
then
    gconftool-2 --set /apps/gnome-terminal/profiles/Default/title_mode --type string ignore
fi

# Start the test application and let it settle in. Two processes
# are started for OpenOffice.
#
echo starting test application $APP_NAME $ARGS $PARAMS ...
$APP_NAME $ARGS $PARAMS &
#sleep $WAIT_TIME
if [ "$APP_NAME" = "swriter" ] || [ "$APP_NAME" = "scalc" ] || [ "$APP_NAME" = "soffice" ]
then
    APP_PID=$(ps -eo pid,ruid,args | grep soffice | grep -v grep | awk '{ print $1 }')
else
    APP_PID=$!
fi
echo $APP_NAME pid $APP_PID

# Play the keystrokes.
#
python $1

# Let things settle for a couple seconds...
#
#sleep $WAIT_TIME

if [ $orcaRunning -eq 0 ]
then
    # Terminate Orca
    echo terminating Orca
    orca --quit > /dev/null 2>&1
fi

# Terminate the running application
echo killing app $APP_NAME $APP_PID
kill -9 $APP_PID > /dev/null 2>&1

# Temporary hack to kill gnome-help help if it's running.
HELP_PID=$(ps -A | grep gnome-help | cut -d' ' -f1)
kill -9 $HELP_PID > /dev/null 2>&1
