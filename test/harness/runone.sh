#!/bin/bash

# Set up our accessibility environment for those apps that 
# don't do it on their own.
#
export GTK_MODULES=:gail:atk-bridge:

echo runone.sh: $*

debugFile=`basename $1 .keys`

# Number of seconds to wait 
REGRESSION_WAIT_TIME=20
COVERAGE_WAIT_TIME=10

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
sed "s^%debug%^$debugFile.orca^g" $SETTINGS_FILE > user-settings.py

# Run the event listener...
#
# python `dirname $0`/event_listener.py > $debugFile.events &
# sleep 2

# Run the app (or gnome-terminal if no app was given) and let it settle in.
#
if [ -n "$3" ]
then
    APP_NAME=$2
    coverageMode=$3
else
    APP_NAME=gnome-terminal
    coverageMode=$2
fi

if [ $coverageMode -eq 1 ]
then
    WAIT_TIME=$COVERAGE_WAIT_TIME
else
    WAIT_TIME=$REGRESSION_WAIT_TIME
fi

if [ $coverageMode -eq 0 ] 	 
then
    # Run orca and let it settle in.
    echo starting Orca...
    orca &
    sleep $WAIT_TIME
fi

# Start the test application and let it settle in
$APP_NAME &
APP_PID=$!
echo starting $APP_NAME pid $APP_PID 
sleep $WAIT_TIME

# Play the keystrokes.
#
python `dirname $0`/../../src/tools/play_keystrokes.py < $1

if [ $coverageMode -eq 0 ] 	 
then
    # Terminate Orca
    echo terminating Orca
    orca --quit > /dev/null 2>&1
    sleep $WAIT_TIME
fi

# Terminate the running application
echo killing app $APP_NAME $APP_PID
kill -9 $APP_PID > /dev/null 2>&1


if [ $coverageMode -eq 0 ] 	 
then
    rm user-settings.py*
fi
