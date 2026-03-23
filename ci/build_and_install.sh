#!/bin/sh

set -eux -o pipefail

meson setup -D prefix=/usr -D mathcat=false _build
meson compile -C _build
meson install -C _build
