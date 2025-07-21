# Orca
#
# Copyright 2006-2008 Sun Microsystems Inc.
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

"""Dictionaries of localized text attribute names and values."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 Sun Microsystems Inc."
__license__   = "LGPL"

from .orca_i18n import C_ # pylint: disable=import-error

attribute_names = {}

# Translators: this attribute specifies the background color of the text.
# The value is an RGB value of the format "u,u,u".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_names["bg-color"] = C_("textattr", "background color")

# Translators: this attribute specifies whether to make the background
# color for each character the height of the highest font used on the
# current line, or the height of the font used for the current character.
# It will be a "true" or "false" value.
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_names["bg-full-height"] = C_("textattr", "background full height")

# Translators: this attribute specifies whether a GdkBitmap is set for
# stippling the background color. It will be a "true" or "false" value.
# See
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_names["bg-stipple"] = C_("textattr", "background stipple")

# Translators: this attribute specifies the direction of the text.
# Values are "none", "ltr" or "rtl".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_names["direction"] = C_("textattr", "direction")

# Translators: this attribute specifies whether the text is editable.
# It will be a "true" or "false" value.
# See
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_names["editable"] = C_("textattr", "editable")

# Translators: this attribute specifies the font family name of the text.
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_names["family-name"] = C_("textattr", "family name")

# Translators: this attribute specifies the foreground color of the text.
# The value is an RGB value of the format "u,u,u".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_names["fg-color"] = C_("textattr", "foreground color")

# Translators: this attribute specifies whether a GdkBitmap is set for
# stippling the foreground color. It will be a "true" or "false" value.
# See
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_names["fg-stipple"] = C_("textattr", "foreground stipple")

# Translators: this attribute specifies the effect applied to the font
# used by the text.
# See:
# http://www.w3.org/TR/2002/WD-css3-fonts-20020802/#font-effect
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
attribute_names["font-effect"] = C_("textattr", "font effect")

# Translators: this attribute specifies the indentation of the text
# (in pixels).
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_names["indent"] = C_("textattr", "indent")

# Translators: this attribute specifies there is something "wrong" with
# the text, such as it being a misspelled word. See:
# https://developer.mozilla.org/en/Accessibility/AT-APIs/Gecko/TextAttrs
#
attribute_names["invalid"] = C_("textattr", "mistake")
# Translators: this attribute specifies there is something "wrong" with
# the text, such as it being a misspelled word. See:
# https://developer.mozilla.org/en/Accessibility/AT-APIs/Gecko/TextAttrs
#

# Translators: this attribute specifies whether the text is invisible.
# It will be a "true" or "false" value.
# See
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_names["invisible"] = C_("textattr", "invisible")

# Translators: this attribute specifies how the justification of the text.
# Values are "left", "right", "center" or "fill".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_names["justification"] = C_("textattr", "justification")

# Translators: this attribute specifies the language that the text is
# written in.
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_names["language"] = C_("textattr", "language")

# Translators: this attribute specifies the pixel width of the left margin.
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_names["left-margin"] = C_("textattr", "left margin")

# Translators: this attribute specifies the height of the line of text.
# See:
# http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-line-height
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
attribute_names["line-height"] = C_("textattr", "line height")

# Translators: this attribute refers to the named style which is associated
# with the entire paragraph and which controls the default formatting
# (font, text size, alignment, etc.) of that paragraph. Examples of
# paragraph styles include "Heading 1", "Heading 2", "Caption", "Footnote",
# "Text Body", "Title", and "Subtitle".
# See:
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
attribute_names["paragraph-style"] = C_("textattr", "paragraph style")

# Translators: this attribute specifies the pixels of blank space to
# leave above each newline-terminated line.
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_names["pixels-above-lines"] = C_("textattr", "pixels above lines")

# Translators: this attribute specifies the pixels of blank space to
# leave below each newline-terminated line.
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_names["pixels-below-lines"] = C_("textattr", "pixels below lines")

# Translators: this attribute specifies the pixels of blank space to
# leave between wrapped lines inside the same newline-terminated line
# (paragraph).
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_names["pixels-inside-wrap"] = C_("textattr", "pixels inside wrap")

# Translators: this attribute specifies the pixel width of the right margin.
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_names["right-margin"] = C_("textattr", "right margin")

# Translators: this attribute specifies the number of pixels that the
# text characters are risen above the baseline.
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_names["rise"] = C_("textattr", "rise")

# Translators: this attribute specifies the scale of the characters. The
# value is a string representation of a double.
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_names["scale"] = C_("textattr", "scale")

# Translators: this attribute specifies the size of the text.
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_names["size"] = C_("textattr", "size")

# Translators: this attribute specifies the stretch of he text, if set.
# Values are "ultra_condensed", "extra_condensed", "condensed",
# "semi_condensed", "normal", "semi_expanded", "expanded",
# "extra_expanded" or "ultra_expanded".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_names["stretch"] = C_("textattr", "stretch")

# Translators: this attribute specifies whether the text is strike though
# (in other words, whether there is a line drawn through it). Values are
# "true" or "false".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_names["strikethrough"] = C_("textattr", "strike through")

# Translators: this attribute specifies the slant style of the text,
# if set. Values are "normal", "oblique" or "italic".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_names["style"] = C_("textattr", "style")

# Translators: this attribute specifies the decoration of the text.
# See:
# http://www.w3.org/TR/1998/REC-CSS2-19980512/text.html#propdef-text-decoration
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
attribute_names["text-decoration"] = C_("textattr", "text decoration")

# Translators: this attribute specifies the angle at which the text is
# displayed (i.e. rotated from the norm) and is represented in degrees
# of rotation.
# See:
# http://www.w3.org/TR/2003/CR-css3-text-20030514/#glyph-orientation-horizontal
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
attribute_names["text-rotation"] = C_("textattr", "text rotation")

# Translators: this attribute specifies the shadow effects applied to the text.
# See:
# http://www.w3.org/TR/1998/REC-CSS2-19980512/text.html#propdef-text-shadow
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
attribute_names["text-shadow"] = C_("textattr", "text shadow")

# Translators: this attributes specifies whether the text is underlined.
# Values are "none", "single", "double" or "low".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_names["underline"] = C_("textattr", "underline")

# Translators: this attribute specifies the capitalization variant of
# the text, if set. Values are "normal" or "small_caps".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_names["variant"] = C_("textattr", "variant")

# Translators: this attributes specifies what vertical alignment property
# has been applied to the text.
# See:
#http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-vertical-align
#
attribute_names["vertical-align"] = C_("textattr", "vertical align")

# Translators: this attribute specifies the weight of the text.
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
# http://www.w3.org/TR/1998/REC-CSS2-19980512/fonts.html#propdef-font-weight
#
attribute_names["weight"] = C_("textattr", "weight")

# Translators: this attribute specifies the wrap mode of the text, if any.
# Values are "none", "char" or "word".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_names["wrap-mode"] = C_("textattr", "wrap mode")

# Translators: this attribute specifies the way the text is written.
# Values are "lr-tb", "rl-tb", "tb-rl", "tb-lr", "bt-rl", "bt-lr", "lr",
# "rl" and "tb".
# See:
# http://www.w3.org/TR/2001/WD-css3-text-20010517/#PrimaryTextAdvanceDirection
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
attribute_names["writing-mode"] = C_("textattr", "writing mode")


# The following are the known values of some of these text attributes.
# These values were found in the Atk documentation at:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
# No doubt there will be more, and as they are found, they can be added
# to this table so they can be translated.
#

attribute_values = {}

# Translators: this is one of the text attribute values for the following
# text attributes: "invisible", "editable", bg-full-height", "strikethrough",
# "bg-stipple" and "fg-stipple".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_values["true"] = C_("textattr", "true")

# Translators: this is one of the text attribute values for the following
# text attributes: "invisible", "editable", bg-full-height", "strikethrough",
# "bg-stipple" and "fg-stipple".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_values["false"] = C_("textattr", "false")

# Translators: this is one of the text attribute values for the following
# text attributes: "font-effect", "underline", "text-shadow", "wrap mode"
# and "direction".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
attribute_values["none"] = C_("textattr", "none")

# Translators: this is one of the text attribute values for the following
# text attributes: "font-effect".
# See:
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
attribute_values["engrave"] = C_("textattr", "engrave")

# Translators: this is one of the text attribute values for the following
# text attributes: "font-effect".
# See:
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
attribute_values["emboss"] = C_("textattr", "emboss")

# Translators: this is one of the text attribute values for the following
# text attributes: "font-effect".
# See:
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
attribute_values["outline"] = C_("textattr", "outline")

# Translators: this is one of the text attribute values for the following
# text attributes: "text-decoration".
# See:
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
attribute_values["overline"] = C_("textattr", "overline")

# Translators: this is one of the text attribute values for the following
# text attributes: "text-decoration".
# See:
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
attribute_values["line-through"] = C_("textattr", "line through")

# Translators: this is one of the text attribute values for the following
# text attributes: "text-decoration".
# See:
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
attribute_values["blink"] = C_("textattr", "blink")

# Translators: this is one of the text attribute values for the following
# text attributes: "text-shadow".
# See:
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
attribute_values["black"] = C_("textattr", "black")

# Translators: this is one of the text attribute values for the following
# text attributes: "underline".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_values["single"] = C_("textattr", "single")

# Translators: this is one of the text attribute values for the following
# text attributes: "underline".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_values["double"] = C_("textattr", "double")

# Translators: this is one of the text attribute values for the following
# text attributes: "underline".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_values["low"] = C_("textattr", "low")

# Translators: this is one of the text attribute values for the following
# text attributes: "wrap mode".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_values["char"] = C_("textattr", "char")

# Translators: this is one of the text attribute values for the following
# text attributes: "wrap mode".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_values["word"] = C_("textattr", "word")

# Translators: this is one of the text attribute values for the following
# text attributes: "wrap mode." It corresponds to GTK_WRAP_WORD_CHAR,
# defined in the Gtk documentation as "Wrap text, breaking lines in
# between words, or if that is not enough, also between graphemes."
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
# http://library.gnome.org/devel/gtk/stable/GtkTextTag.html#GtkWrapMode
#
attribute_values["word_char"] = C_("textattr", "word char")

# Translators: this is one of the text attribute values for the following
# text attributes: "direction".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_values["ltr"] = C_("textattr", "ltr")

# Translators: this is one of the text attribute values for the following
# text attributes: "direction".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_values["rtl"] = C_("textattr", "rtl")

# Translators: this is one of the text attribute values for the following
# text attributes: "justification".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_values["left"] = C_("textattr", "left")

# Translators: this is one of the text attribute values for the following
# text attributes: "justification".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_values["right"] = C_("textattr", "right")

# Translators: this is one of the text attribute values for the following
# text attributes: "justification".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_values["center"] = C_("textattr", "center")

# Translators: this is one of the text attribute values for the following
# text attributes: "justification". In Gecko, when no justification has
# be explicitly set, they report a justification of "start".
#
attribute_values["start"] = C_("textattr", "no justification")

# Translators: this is one of the text attribute values for the following
# text attributes: "justification".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_values["fill"] = C_("textattr", "fill")

# Translators: this is one of the text attribute values for the following
# text attributes: "stretch".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_values["ultra_condensed"] = C_("textattr", "ultra condensed")

# Translators: this is one of the text attribute values for the following
# text attributes: "stretch".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_values["extra_condensed"] = C_("textattr", "extra condensed")

# Translators: this is one of the text attribute values for the following
# text attributes: "stretch".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_values["condensed"] = C_("textattr", "condensed")

# Translators: this is one of the text attribute values for the following
# text attributes: "stretch".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_values["semi_condensed"] = C_("textattr", "semi condensed")

# Translators: this is one of the text attribute values for the following
# text attributes: "stretch" and "variant".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_values["normal"] = C_("textattr", "normal")

# Translators: this is one of the text attribute values for the following
# text attributes: "stretch".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_values["semi_expanded"] = C_("textattr", "semi expanded")

# Translators: this is one of the text attribute values for the following
# text attributes: "stretch".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_values["expanded"] = C_("textattr", "expanded")

# Translators: this is one of the text attribute values for the following
# text attributes: "stretch".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_values["extra_expanded"] = C_("textattr", "extra expanded")

# Translators: this is one of the text attribute values for the following
# text attributes: "stretch".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_values["ultra_expanded"] = C_("textattr", "ultra expanded")

# Translators: this is one of the text attribute values for the following
# text attributes: "variant".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_values["small_caps"] = C_("textattr", "small caps")

# Translators: this is one of the text attribute values for the following
# text attributes: "style".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_values["oblique"] = C_("textattr", "oblique")

# Translators: this is one of the text attribute values for the following
# text attributes: "style".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
attribute_values["italic"] = C_("textattr", "italic")

# Translators: this is one of the text attribute values for the following
# text attributes: "paragraph-style".
# See:
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
attribute_values["Default"] = C_("textattr", "Default")

# Translators: this is one of the text attribute values for the following
# text attributes: "paragraph-style".
# See:
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
attribute_values["Text body"] = C_("textattr", "Text body")

# Translators: this is one of the text attribute values for the following
# text attributes: "paragraph-style".
# See:
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
attribute_values["Heading"] = C_("textattr", "Heading")

# Translators: this is one of the text attribute values for the following
# text attributes: "vertical-align".
# See:
#http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-vertical-align
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
attribute_values["baseline"] = C_("textattr", "baseline")

# Translators: this is one of the text attribute values for the following
# text attributes: "vertical-align".
# See:
#http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-vertical-align
#
attribute_values["sub"] = C_("textattr", "sub")

# Translators: this is one of the text attribute values for the following
# text attributes: "vertical-align".
# See:
#http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-vertical-align
#
attribute_values["super"] = C_("textattr", "super")

# Translators: this is one of the text attribute values for the following
# text attributes: "vertical-align".
# See:
#http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-vertical-align
#
attribute_values["top"] = C_("textattr", "top")

# Translators: this is one of the text attribute values for the following
# text attributes: "vertical-align".
# See:
#http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-vertical-align
#
attribute_values["text-top"] = C_("textattr", "text-top")

# Translators: this is one of the text attribute values for the following
# text attributes: "vertical-align".
# See:
#http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-vertical-align
#
attribute_values["middle"] = C_("textattr", "middle")

# Translators: this is one of the text attribute values for the following
# text attributes: "vertical-align".
# See:
#http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-vertical-align
#
attribute_values["bottom"] = C_("textattr", "bottom")

# Translators: this is one of the text attribute values for the following
# text attributes: "vertical-align".
# See:
#http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-vertical-align
#
attribute_values["text-bottom"] = C_("textattr", "text-bottom")

# Translators: this is one of the text attribute values for the following
# text attributes: "vertical-align" and "writing-mode".
# See:
#http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-vertical-align
# http://www.w3.org/TR/2001/WD-css3-text-20010517/#PrimaryTextAdvanceDirection
#
attribute_values["inherit"] = C_("textattr", "inherit")

# Translators: this is one of the text attribute values for the following
# text attributes: "writing-mode".
# See:
# http://www.w3.org/TR/2001/WD-css3-text-20010517/#PrimaryTextAdvanceDirection
#
attribute_values["lr-tb"] = C_("textattr", "lr-tb")

# Translators: this is one of the text attribute values for the following
# text attributes: "writing-mode".
# See:
# http://www.w3.org/TR/2001/WD-css3-text-20010517/#PrimaryTextAdvanceDirection
#
attribute_values["rl-tb"] = C_("textattr", "rl-tb")

# Translators: this is one of the text attribute values for the following
# text attributes: "writing-mode".
# See:
# http://www.w3.org/TR/2001/WD-css3-text-20010517/#PrimaryTextAdvanceDirection
#
attribute_values["tb-rl"] = C_("textattr", "tb-rl")

# Translators: this is one of the text attribute values for the following
# text attributes: "writing-mode".
# See:
# http://www.w3.org/TR/2001/WD-css3-text-20010517/#PrimaryTextAdvanceDirection
#
attribute_values["tb-lr"] = C_("textattr", "tb-lr")

# Translators: this is one of the text attribute values for the following
# text attributes: "writing-mode".
# See:
# http://www.w3.org/TR/2001/WD-css3-text-20010517/#PrimaryTextAdvanceDirection
#
attribute_values["bt-rl"] = C_("textattr", "bt-rl")

# Translators: this is one of the text attribute values for the following
# text attributes: "writing-mode".
# See:
# http://www.w3.org/TR/2001/WD-css3-text-20010517/#PrimaryTextAdvanceDirection
#
attribute_values["bt-lr"] = C_("textattr", "bt-lr")

# Translators: this is one of the text attribute values for the following
# text attributes: "writing-mode".
# See:
# http://www.w3.org/TR/2001/WD-css3-text-20010517/#PrimaryTextAdvanceDirection
#
attribute_values["lr"] = C_("textattr", "lr")

# Translators: this is one of the text attribute values for the following
# text attributes: "writing-mode".
# See:
# http://www.w3.org/TR/2001/WD-css3-text-20010517/#PrimaryTextAdvanceDirection
#
attribute_values["rl"] = C_("textattr", "rl")

# Translators: this is one of the text attribute values for the following
# text attributes: "writing-mode".
# See:
# http://www.w3.org/TR/2001/WD-css3-text-20010517/#PrimaryTextAdvanceDirection
#
attribute_values["tb"] = C_("textattr", "tb")

# Translators: this is one of the text attribute values for the following
# text attributes: "strikethrough." It refers to the line style.
#
attribute_values["solid"] = C_("textattr", "solid")

# Translators: this is one of the text attribute values for the following
# text attributes: "invalid". It is an indication that the text is not
# spelled correctly. See:
# https://developer.mozilla.org/en/Accessibility/AT-APIs/Gecko/TextAttrs
#
attribute_values["spelling"] = C_("textattr", "spelling")

# Translators: This is the text-spelling attribute. See:
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
attribute_values["text-spelling"] = C_("textattr", "spelling")
