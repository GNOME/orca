#!/bin/bash
#
# runall.sh can take the following optional parameters:
#
# -c                 - analyze test coverage instead of regression testing
# -h|--help          - print a usage message.
# -k <keystrokesDir> - alternate keystroke directory (default is ../keystrokes).
# -r <resultsDir>    - alternate results directory (default is ../results).
# -s                 - require the tester to press return between each test
#

OPERATING_SYSTEMS="SunOS Linux"
foo=`dirname $0`
harnessDir=`cd $foo; pwd`
keystrokesDir=$harnessDir/../keystrokes
resultsDir=$harnessDir/../results

# Number of seconds to wait between each test
#
REGRESSION_WAIT_TIME=20
COVERAGE_WAIT_TIME=10

# OpenOffice 2.2 executables are installed in 
# /usr/lib/openoffice/program
#
export PATH=$PATH:/usr/lib/openoffice/program

coverageMode=0

process_cl () {
    while [ $# != 0 ]; do
        case "$1" in
            -c )
                coverageMode=1
		;;
            -k )
                shift
                if [ $# == 0 ]; then
                    echo "Option -k requires an argument."
                    exit 1
                fi
                keystrokesDir=$1
                ;;
            -r )
                shift
                if [ $# == 0 ]; then
                    echo "Option -r requires an argument."
                    exit 1
                fi
                resultsDir=$1
                ;;
            -s )
                stepMode=1
                ;;
            -h|--help)
                echo "Usage: $0 [options]"
                echo "options:"
		echo "   -c                perform code coverage analysis"
                echo "   -h, --help        print this usage message"
                echo "   -k keystrokeDir   specify an alternate keystrokes directory"
                echo "   -r resultsDir     specify an alternate results directory"
                echo "   -s                require a return to be pressed between keystrokes files"
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                exit 1
                ;;
        esac
        shift
    done
}

# Process the users command line options.
#
process_cl "${@}"
if [ "$coverageMode" -eq "1" ]
then
    WAIT_TIME=$COVERAGE_WAIT_TIME
else
    WAIT_TIME=$REGRESSION_WAIT_TIME
fi


if [ "$coverageMode" -eq 1 ]
then 	 
    echo generating coverage map...
    coverageDir=../coverage/`date +%Y-%m-%d_%H:%M:%S`
    trace2html.py -o $coverageDir -w orca -r runorca.py &
    trace_pid=$!
    sleep $WAIT_TIME 	 
    echo ...finished generating coverage map.
fi

# Look in the keystrokes directory for directories.
# The name of each directory under the keystrokes directory
# is expected to be the name of an application to run.  For
# example, the gnome-terminal keystrokes should live under
# a directory called gnome-terminal.  If there isn't an
# application associated with the directory name, we just
# assume the test should apply to the desktop in general.
#
# There is expected to be a keystrokes file in each of the
# found sub-directories. We go ahead and run this using our
# runone.sh script.
#
dirprefix=`date +%Y-%m-%d_%H:%M:%S`
for testDir in `find $keystrokesDir -type d | sort`
do
  application=`basename $testDir`
  if [ $application != ".svn" ] && [ $application != `basename $keystrokesDir` ]
    then

# (Bug #359919). Check to see if the application exists.
# If it does, then supply that as the $2 parameter to the runone.sh command.
# If it doesn't exist see if the name is in a list of system types that
# we care about (currently "SunOS" and "Linux").
#   If it is, then compare the directory name against the result of running
#   `uname`.
#     If they match, then run the scripts in that directory.
#     If they don't match, ignore that directory.
#   If it isn't, then don't supply a $2 parameter to the runone.sh command.

      oldifs="$IFS"
      IFS=:
      found=0
      for dir in $PATH; do
        test -x "$dir/$application" && {
          found=1
          break
        }
      done
      IFS="$oldifs"
      outputdir=$dirprefix/$application
      currentdir=`pwd`

      # We run under ./tmp as a means to help provide consistent
      # output for things that expose directory paths.
      #
      mkdir -p ./tmp/$application
      cd ./tmp/$application
      for testFile in `find $testDir -type f -name "*.keys" | sort`; do
        echo ========================================
        echo Running $testFile
        if [ "$found" -gt 0 ]
        then
          $harnessDir/runone.sh $testFile $application $coverageMode
        else
          osType=`uname`
          for os in $OPERATING_SYSTEMS; do
            if [ $application == $os ]
            then
              found=1
              if [ $osType == $os ]
              then
                $harnessDir/runone.sh $testFile $coverageMode
              fi
            fi
          done
          if [ "$found" -eq 0 ]
          then
            $harnessDir/runone.sh $testFile $coverageMode
          fi
        fi

        # Wait for application to finish shutting down.
        sleep $WAIT_TIME

        # Copy the results (.orca) file to the output directory.
        # This is the file that will be used for regression
        # testing. 
        newResultsFiles=`basename $testFile .keys`
        mkdir -p $currentdir/$outputdir
        cp $newResultsFiles.* $currentdir/$outputdir

        # Compare the results file with the golden results file.
        # echo Comparing results for $testFile
        # expectedResultsFile=$resultsDir/$application/$newResultsFile
        # diff -s $expectedResultsFile $newResultsFile

        echo Finished running $testFile.
        if [ "x$stepMode" == "x1" ]
        then
          echo Press Return to continue...
          read foo
        fi
        echo ========================================
      done
      cd $currentdir
      rm -rf ./tmp/$application
  fi
done
echo $dirprefix completed at `date +%Y-%m-%d_%H:%M:%S`
