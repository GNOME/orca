#!/bin/sh

set -eux -o pipefail

mkdir -p _build
cd _build
../autogen.sh --prefix=/usr
make
make install
