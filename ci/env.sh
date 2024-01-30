# Activate the Python virtual environment for CI scripts.
#
# We test for the presence of the file, since when first creating the container images for CI,
# the venv has not been created yet.  This is mostly a hack to allow having a single "env.sh"
# script instead of one for container creation and one for CI jobs.
if [ -f /usr/local/python/bin/activate ]; then
    source /usr/local/python/bin/activate
fi
