#!/bin/bash
#
# Script to run pylint on the Orca source code.
# See http://live.gnome.org/Orca/Pylint for more info.
#
INSTALL_DIR=/usr/lib/python2.5/site-packages
for foo in `ls $INSTALL_DIR/orca/*.py $INSTALL_DIR/orca/scripts/*.py`
do
    pylint --init-hook="import pyatspi" $foo > `basename $foo .py`.pylint 2>&1
done
grep "code has been rated" *.pylint | cut -f1 -d\( \
| sed "s/.pylint:Your code has been rated at / /" \
| sed "s^/10^^" | sort -n -k 2,2
echo Errors exist in the following files:
grep "E[0-9][0-9][0-9][0-9]" *.pylint | grep -v I0011 | cut -f1 -d: | sort -u \
| xargs grep "code has been rated" | cut -f1 -d.
