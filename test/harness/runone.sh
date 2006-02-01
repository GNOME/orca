#!/bin/bash

# Set up our accessibility environment for those apps that 
# don't do it on their own.
#
export GTK_MODULES=:gail:atk-bridge:

debugFile=`basename $1`

# Set up our user settings file for the output format we want.
#
sed "s^%debug%^$debugFile.orca^g" `dirname $0`/user-settings.py.in > ~/.orca/user-settings.py

# Run the event listener...
#
python `dirname $0`/event_listener.py > $debugFile.events &
sleep 2

# Run orca and let it settle in.
#
orca &
sleep 5

# Run the app and let it settle in.
#
if [ -n "$2" ]
then
    $2 &
    sleep 5
fi

# Play the keystrokes.
#
python `dirname $0`/../../src/tools/play_keystrokes.py < $1
