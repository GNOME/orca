# Orca
#
# Copyright 2014 Igalia, S.L.
#
# Author: Joanmarie Diggs <jdiggs@igalia.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

# pylint: disable=too-many-locals

"""Provides localized color names."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2014 Igalia, S.L."
__license__   = "LGPL"

import re

from .orca_i18n import C_ # pylint: disable=import-error

css_names = {}

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#f0f8ff"] = C_("color name", "alice blue")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#faebd7"] = C_("color name", "antique white")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#7fffd4"] = C_("color name", "aquamarine")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#f0ffff"] = C_("color name", "azure")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#f5f5dc"] = C_("color name", "beige")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#ffe4c4"] = C_("color name", "bisque")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#000000"] = C_("color name", "black")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#ffebcd"] = C_("color name", "blanched almond")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#0000ff"] = C_("color name", "blue")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#8a2be2"] = C_("color name", "blue violet")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#a52a2a"] = C_("color name", "brown")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#deb887"] = C_("color name", "burlywood")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#5f9ea0"] = C_("color name", "cadet blue")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#7fff00"] = C_("color name", "chartreuse")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#d2691e"] = C_("color name", "chocolate")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#ff7f50"] = C_("color name", "coral")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#6495ed"] = C_("color name", "cornflower blue")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#fff8dc"] = C_("color name", "cornsilk")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#dc143c"] = C_("color name", "crimson")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#00ffff"] = C_("color name", "cyan")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#00008b"] = C_("color name", "dark blue")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#008b8b"] = C_("color name", "dark cyan")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#b8860b"] = C_("color name", "dark goldenrod")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#a9a9a9"] = C_("color name", "dark gray")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#006400"] = C_("color name", "dark green")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#bdb76b"] = C_("color name", "dark khaki")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#8b008b"] = C_("color name", "dark magenta")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#556b2f"] = C_("color name", "dark olive green")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#ff8c00"] = C_("color name", "dark orange")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#9932cc"] = C_("color name", "dark orchid")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#8b0000"] = C_("color name", "dark red")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#e9967a"] = C_("color name", "dark salmon")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#8fbc8f"] = C_("color name", "dark sea green")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#483d8b"] = C_("color name", "dark slate blue")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#2f4f4f"] = C_("color name", "dark slate gray")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#00ced1"] = C_("color name", "dark turquoise")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#9400d3"] = C_("color name", "dark violet")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#ff1493"] = C_("color name", "deep pink")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#00bfff"] = C_("color name", "deep sky blue")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#696969"] = C_("color name", "dim gray")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#1e90ff"] = C_("color name", "dodger blue")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#b22222"] = C_("color name", "fire brick")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#fffaf0"] = C_("color name", "floral white")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#228b22"] = C_("color name", "forest green")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#ff00ff"] = C_("color name", "fuchsia")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#dcdcdc"] = C_("color name", "gainsboro")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#HTML_color_names.
css_names["#f8f8ff"] = C_("color name", "ghost white")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#ffd700"] = C_("color name", "gold")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#daa520"] = C_("color name", "goldenrod")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#808080"] = C_("color name", "gray")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#008000"] = C_("color name", "green")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#adff2f"] = C_("color name", "green yellow")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#f0fff0"] = C_("color name", "honeydew")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#ff69b4"] = C_("color name", "hot pink")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#cd5c5c"] = C_("color name", "indian red")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#4b0082"] = C_("color name", "indigo")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#fffff0"] = C_("color name", "ivory")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#f0e68c"] = C_("color name", "khaki")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#e6e6fa"] = C_("color name", "lavender")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#fff0f5"] = C_("color name", "lavender blush")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#7cfc00"] = C_("color name", "lawn green")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#fffacd"] = C_("color name", "lemon chiffon")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#add8e6"] = C_("color name", "light blue")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#f08080"] = C_("color name", "light coral")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#e0ffff"] = C_("color name", "light cyan")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#fafad2"] = C_("color name", "light goldenrod yellow")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#d3d3d3"] = C_("color name", "light gray")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#90ee90"] = C_("color name", "light green")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#ffb6c1"] = C_("color name", "light pink")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#ffa07a"] = C_("color name", "light salmon")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#20b2aa"] = C_("color name", "light sea green")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#87cefa"] = C_("color name", "light sky blue")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#778899"] = C_("color name", "light slate gray")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#b0c4de"] = C_("color name", "light steel blue")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#ffffe0"] = C_("color name", "light yellow")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#00ff00"] = C_("color name", "lime")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#32cd32"] = C_("color name", "lime green")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#faf0e6"] = C_("color name", "linen")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#ff00ff"] = C_("color name", "magenta")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#800000"] = C_("color name", "maroon")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#66cdaa"] = C_("color name", "medium aquamarine")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#0000cd"] = C_("color name", "medium blue")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#ba55d3"] = C_("color name", "medium orchid")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#9370d8"] = C_("color name", "medium purple")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#3cb371"] = C_("color name", "medium sea green")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#7b68ee"] = C_("color name", "medium slate blue")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#00fa9a"] = C_("color name", "medium spring green")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#48d1cc"] = C_("color name", "medium turquoise")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#c71585"] = C_("color name", "medium violet red")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#191970"] = C_("color name", "midnight blue")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#f5fffa"] = C_("color name", "mint cream")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#ffe4e1"] = C_("color name", "misty rose")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#ffe4b5"] = C_("color name", "moccasin")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#ffdead"] = C_("color name", "navajo white")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#000080"] = C_("color name", "navy")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#fdf5e6"] = C_("color name", "old lace")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#808000"] = C_("color name", "olive")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#6b8e23"] = C_("color name", "olive drab")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#ffa500"] = C_("color name", "orange")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#ff4500"] = C_("color name", "orange red")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#da70d6"] = C_("color name", "orchid")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#eee8aa"] = C_("color name", "pale goldenrod")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#98fb98"] = C_("color name", "pale green")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#afeeee"] = C_("color name", "pale turquoise")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#d87093"] = C_("color name", "pale violet red")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#ffefd5"] = C_("color name", "papaya whip")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#ffdab9"] = C_("color name", "peach puff")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#cd853f"] = C_("color name", "peru")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#ffc0cb"] = C_("color name", "pink")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#dda0dd"] = C_("color name", "plum")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#b0e0e6"] = C_("color name", "powder blue")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#800080"] = C_("color name", "purple")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#ff0000"] = C_("color name", "red")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#bc8f8f"] = C_("color name", "rosy brown")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#4169e1"] = C_("color name", "royal blue")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#8b4513"] = C_("color name", "saddle brown")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#fa8072"] = C_("color name", "salmon")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#f4a460"] = C_("color name", "sandy brown")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#2e8b57"] = C_("color name", "sea green")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#fff5ee"] = C_("color name", "seashell")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#a0522d"] = C_("color name", "sienna")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#c0c0c0"] = C_("color name", "silver")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#87ceeb"] = C_("color name", "sky blue")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#6a5acd"] = C_("color name", "slate blue")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#708090"] = C_("color name", "slate gray")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#fffafa"] = C_("color name", "snow")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#00ff7f"] = C_("color name", "spring green")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#4682b4"] = C_("color name", "steel blue")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#d2b48c"] = C_("color name", "tan")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#008080"] = C_("color name", "teal")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#d8bfd8"] = C_("color name", "thistle")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#ff6347"] = C_("color name", "tomato")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#40e0d0"] = C_("color name", "turquoise")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#ee82ee"] = C_("color name", "violet")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#f5deb3"] = C_("color name", "wheat")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#ffffff"] = C_("color name", "white")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#f5f5f5"] = C_("color name", "white smoke")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#ffff00"] = C_("color name", "yellow")

# Translators: This refers to a CSS color name. The name, hex value, and color
# can be found at http://www.w3schools.com/cssref/css_colornames.asp and at
# http://en.wikipedia.org/wiki/Web_colors#X11_color_names.
css_names["#9acd32"] = C_("color name", "yellow green")

def _rgb_from_string(rgb_string):
    try:
        regex = re.compile(r"rgb|[^\w,]", re.IGNORECASE)
        string = re.sub(regex, "", rgb_string)
        red, green, blue = map(int, string.split(","))
        if red > 255 or green > 255 or blue > 255:
            red, green, blue = red >> 8, green >> 8, blue >> 8
    except (ValueError, AttributeError, TypeError):
        return -1, -1, -1
    return red, green, blue

def _rgb_to_name(red, green, blue):
    """Returns the localized name for the RGB value."""

    hex_string = f'#{red:02x}{green:02x}{blue:02x}'
    css_name = css_names.get(hex_string)
    if css_name:
        return css_name

    # Find the closest match.
    colors = {}
    for key, _value in css_names.items():
        r, g, b = [int(s, 16) for s in (key[1:3], key[3:5], key[5:7])]
        rd = abs(r - red) ** 2
        gd = abs(g - green) ** 2
        bd = abs(b - blue) ** 2
        colors[(rd + gd + bd)] = key

    # Hold black and white to higher standards than the other close colors.
    d1 = min(colors.keys())
    match = colors.pop(d1)
    if match not in ["#000000", "#ffffff"]:
        return css_names.get(match)

    d2 = min(colors.keys())
    if d2 - d1 < d1:
        match = colors.pop(d2)

    return css_names.get(match)

def rgb_string_to_color_name(rgb_string):
    """Returns the localized color name for the RGB string."""

    red, green, blue = _rgb_from_string(rgb_string)
    if red < 0 or green < 0 or blue < 0:
        return ""
    return _rgb_to_name(red, green, blue)

def normalize_rgb_string(rgb_string):
    """Returns a normalized RGB string so end users always get the same thing."""

    red, green, blue = _rgb_from_string(rgb_string)
    if red < 0 or green < 0 or blue < 0:
        return ""
    return f"{red} {green} {blue}"

def get_presentable_color_name(value):
    """Returns a presentable color name based on the user's settings."""

    from . import speech_and_verbosity_manager # pylint: disable=import-outside-toplevel
    if speech_and_verbosity_manager.get_manager().get_use_color_names():
        return rgb_string_to_color_name(value)
    return normalize_rgb_string(value)
