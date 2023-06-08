#!/bin/sh

set -eux -o pipefail

git clone --depth 1 https://gitlab.gnome.org/GNOME/pyatspi2.git
cd pyatspi2
mkdir _build
cd _build

../autogen.sh --prefix=/usr
make
make install
