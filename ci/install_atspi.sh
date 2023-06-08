#!/bin/sh

set -eux -o pipefail

git clone --depth 1 https://gitlab.gnome.org/GNOME/at-spi2-core.git
cd at-spi2-core
mkdir _build

meson setup --buildtype=debug --prefix=/usr _build .
meson compile -C _build
meson install -C _build
