#!/bin/sh
#
# Creates a Python virtual environment in /usr/local/python and installs
# the modules from requirements.txt in it.  These modules are required
# by various jobs in the CI pipeline.
#
# Note that Orca's run-time dependencies are *not* in this
# ci/requirements.txt - those come from system packages.  The packages
# that this script installs are Python tools for use during the CI
# only, to check the code, rather than to run it.

set -eux -o pipefail

python3 -m venv /usr/local/python
source /usr/local/python/bin/activate
pip3 install --upgrade pip
pip3 install -r ci/requirements.txt
