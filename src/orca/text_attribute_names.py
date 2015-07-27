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

"""Provides getTextAttributeName method that maps each text attribute
into its localized equivalent."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 Sun Microsystems Inc."
__license__   = "LGPL"

from .orca_i18n import C_

# Translators: this is a structure to assist in the generation of
# localized strings for the various text attributes. 
#
# Information can be found in the Atk documentation at:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
# The at-spi IDL documentation for Accessibility_Text.idl also provides
# the following information:
#
# Attributes relevant to localization should be provided in accordance
# with the w3c "Internationalization and Localization Markup Requirements",
# http://www.w3.org/TR/2005/WD-itsreq-20051122/
#
# Other text attributes should choose their names and value semantics in
# accordance with relevant standards such as:
#   CSS level 2 (http://www.w3.org/TR/1998/REC-CSS2-19980512),
#   XHTML 1.0   (http://www.w3.org/TR/2002/REC-xhtml1-20020801), and
#   WICD        (http://www.w3.org/TR/2005/WD-WICD-20051121/). 
#
# Where possible, specific URL references will also be given below for
# each text attribute.
#

_textAttributeTable = {}

# Translators: this attribute specifies the background color of the text.
# The value is an RGB value of the format "u,u,u".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["bg-color"] = C_("textattr", "background color")

# Translators: this attribute specifies whether to make the background
# color for each character the height of the highest font used on the
# current line, or the height of the font used for the current character.
# It will be a "true" or "false" value.
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["bg-full-height"] = C_("textattr", "background full height")

# Translators: this attribute specifies whether a GdkBitmap is set for 
# stippling the background color. It will be a "true" or "false" value.
# See
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["bg-stipple"] = C_("textattr", "background stipple")

# Translators: this attribute specifies the direction of the text.
# Values are "none", "ltr" or "rtl".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["direction"] = C_("textattr", "direction")

# Translators: this attribute specifies whether the text is editable.
# It will be a "true" or "false" value.
# See
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["editable"] = C_("textattr", "editable")

# Translators: this attribute specifies the font family name of the text.
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["family-name"] = C_("textattr", "family name")

# Translators: this attribute specifies the foreground color of the text.
# The value is an RGB value of the format "u,u,u".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["fg-color"] = C_("textattr", "foreground color")

# Translators: this attribute specifies whether a GdkBitmap is set for
# stippling the foreground color. It will be a "true" or "false" value.
# See
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["fg-stipple"] = C_("textattr", "foreground stipple")

# Translators: this attribute specifies the effect applied to the font 
# used by the text.
# See:
# http://www.w3.org/TR/2002/WD-css3-fonts-20020802/#font-effect
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
_textAttributeTable["font-effect"] = C_("textattr", "font effect")

# Translators: this attribute specifies the indentation of the text
# (in pixels).
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["indent"] = C_("textattr", "indent")

# Translators: this attribute specifies there is something "wrong" with
# the text, such as it being a misspelled word. See:
# https://developer.mozilla.org/en/Accessibility/AT-APIs/Gecko/TextAttrs
#
_textAttributeTable["invalid"] = C_("textattr", "mistake")
# Translators: this attribute specifies there is something "wrong" with
# the text, such as it being a misspelled word. See:
# https://developer.mozilla.org/en/Accessibility/AT-APIs/Gecko/TextAttrs
#

# Translators: this attribute specifies whether the text is invisible.
# It will be a "true" or "false" value.
# See
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["invisible"] = C_("textattr", "invisible")

# Translators: this attribute specifies how the justification of the text.
# Values are "left", "right", "center" or "fill".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["justification"] = C_("textattr", "justification")

# Translators: this attribute specifies the language that the text is
# written in.
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["language"] = C_("textattr", "language")

# Translators: this attribute specifies the pixel width of the left margin.
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["left-margin"] = C_("textattr", "left margin")

# Translators: this attribute specifies the height of the line of text.
# See:
# http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-line-height
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
_textAttributeTable["line-height"] = C_("textattr", "line height")

# Translators: this attribute refers to the named style which is associated
# with the entire paragraph and which controls the default formatting 
# (font, text size, alignment, etc.) of that paragraph. Examples of 
# paragraph styles include "Heading 1", "Heading 2", "Caption", "Footnote",
# "Text Body", "Title", and "Subtitle".
# See:
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
_textAttributeTable["paragraph-style"] = C_("textattr", "paragraph style")

# Translators: this attribute specifies the pixels of blank space to 
# leave above each newline-terminated line.
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["pixels-above-lines"] = C_("textattr", "pixels above lines")

# Translators: this attribute specifies the pixels of blank space to
# leave below each newline-terminated line.
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["pixels-below-lines"] = C_("textattr", "pixels below lines")

# Translators: this attribute specifies the pixels of blank space to
# leave between wrapped lines inside the same newline-terminated line
# (paragraph).
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["pixels-inside-wrap"] = C_("textattr", "pixels inside wrap")

# Translators: this attribute specifies the pixel width of the right margin.
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["right-margin"] = C_("textattr", "right margin")

# Translators: this attribute specifies the number of pixels that the 
# text characters are risen above the baseline.
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["rise"] = C_("textattr", "rise")

# Translators: this attribute specifies the scale of the characters. The
# value is a string representation of a double.
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["scale"] = C_("textattr", "scale")

# Translators: this attribute specifies the size of the text.
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["size"] = C_("textattr", "size")

# Translators: this attribute specifies the stretch of he text, if set.
# Values are "ultra_condensed", "extra_condensed", "condensed",
# "semi_condensed", "normal", "semi_expanded", "expanded",
# "extra_expanded" or "ultra_expanded".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["stretch"] = C_("textattr", "stretch")

# Translators: this attribute specifies whether the text is strike though
# (in other words, whether there is a line drawn through it). Values are
# "true" or "false".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["strikethrough"] = C_("textattr", "strike through")

# Translators: this attribute specifies the slant style of the text,
# if set. Values are "normal", "oblique" or "italic".
# See: 
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["style"] = C_("textattr", "style")

# Translators: this attribute specifies the decoration of the text.
# See:
# http://www.w3.org/TR/1998/REC-CSS2-19980512/text.html#propdef-text-decoration
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
_textAttributeTable["text-decoration"] = C_("textattr", "text decoration")

# Translators: this attribute specifies the angle at which the text is
# displayed (i.e. rotated from the norm) and is represented in degrees 
# of rotation.
# See:
# http://www.w3.org/TR/2003/CR-css3-text-20030514/#glyph-orientation-horizontal
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
_textAttributeTable["text-rotation"] = C_("textattr", "text rotation")

# Translators: this attribute specifies the shadow effects applied to the text.
# See:
# http://www.w3.org/TR/1998/REC-CSS2-19980512/text.html#propdef-text-shadow
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
_textAttributeTable["text-shadow"] = C_("textattr", "text shadow")

# Translators: this attributes specifies whether the text is underlined.
# Values are "none", "single", "double" or "low".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["underline"] = C_("textattr", "underline")

# Translators: this attribute specifies the capitalization variant of
# the text, if set. Values are "normal" or "small_caps".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["variant"] = C_("textattr", "variant")

# Translators: this attributes specifies what vertical alignment property
# has been applied to the text.
# See:
#http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-vertical-align
#
_textAttributeTable["vertical-align"] = C_("textattr", "vertical align")

# Translators: this attribute specifies the weight of the text.
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
# http://www.w3.org/TR/1998/REC-CSS2-19980512/fonts.html#propdef-font-weight
#
_textAttributeTable["weight"] = C_("textattr", "weight")

# Translators: this attribute specifies the wrap mode of the text, if any.
# Values are "none", "char" or "word".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["wrap-mode"] = C_("textattr", "wrap mode")

# Translators: this attribute specifies the way the text is written.
# Values are "lr-tb", "rl-tb", "tb-rl", "tb-lr", "bt-rl", "bt-lr", "lr",
# "rl" and "tb".
# See:
# http://www.w3.org/TR/2001/WD-css3-text-20010517/#PrimaryTextAdvanceDirection
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
_textAttributeTable["writing-mode"] = C_("textattr", "writing mode")


# The following are the known values of some of these text attributes.
# These values were found in the Atk documentation at:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
# No doubt there will be more, and as they are found, they can be added
# to this table so they can be translated.
#

# Translators: this is one of the text attribute values for the following
# text attributes: "invisible", "editable", bg-full-height", "strikethrough",
# "bg-stipple" and "fg-stipple".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["true"] = C_("textattr", "true")

# Translators: this is one of the text attribute values for the following
# text attributes: "invisible", "editable", bg-full-height", "strikethrough",
# "bg-stipple" and "fg-stipple".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["false"] = C_("textattr", "false")

# Translators: this is one of the text attribute values for the following
# text attributes: "font-effect", "underline", "text-shadow", "wrap mode"
# and "direction".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
_textAttributeTable["none"] = C_("textattr", "none")

# Translators: this is one of the text attribute values for the following
# text attributes: "font-effect".
# See:
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
_textAttributeTable["engrave"] = C_("textattr", "engrave")

# Translators: this is one of the text attribute values for the following
# text attributes: "font-effect".
# See:
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
_textAttributeTable["emboss"] = C_("textattr", "emboss")

# Translators: this is one of the text attribute values for the following
# text attributes: "font-effect".
# See:
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
_textAttributeTable["outline"] = C_("textattr", "outline")

# Translators: this is one of the text attribute values for the following
# text attributes: "text-decoration".
# See:
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
_textAttributeTable["overline"] = C_("textattr", "overline")

# Translators: this is one of the text attribute values for the following
# text attributes: "text-decoration".
# See:
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
_textAttributeTable["line-through"] = C_("textattr", "line through")

# Translators: this is one of the text attribute values for the following
# text attributes: "text-decoration".
# See:
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
_textAttributeTable["blink"] = C_("textattr", "blink")

# Translators: this is one of the text attribute values for the following
# text attributes: "text-shadow".
# See:
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
_textAttributeTable["black"] = C_("textattr", "black")

# Translators: this is one of the text attribute values for the following
# text attributes: "underline".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["single"] = C_("textattr", "single")

# Translators: this is one of the text attribute values for the following
# text attributes: "underline".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["double"] = C_("textattr", "double")

# Translators: this is one of the text attribute values for the following
# text attributes: "underline".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["low"] = C_("textattr", "low")

# Translators: this is one of the text attribute values for the following
# text attributes: "wrap mode".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["char"] = C_("textattr", "char")

# Translators: this is one of the text attribute values for the following
# text attributes: "wrap mode".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["word"] = C_("textattr", "word")

# Translators: this is one of the text attribute values for the following
# text attributes: "wrap mode." It corresponds to GTK_WRAP_WORD_CHAR,
# defined in the Gtk documentation as "Wrap text, breaking lines in
# between words, or if that is not enough, also between graphemes."
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
# http://library.gnome.org/devel/gtk/stable/GtkTextTag.html#GtkWrapMode
#
_textAttributeTable["word_char"] = C_("textattr", "word char")

# Translators: this is one of the text attribute values for the following
# text attributes: "direction".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["ltr"] = C_("textattr", "ltr")

# Translators: this is one of the text attribute values for the following
# text attributes: "direction".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["rtl"] = C_("textattr", "rtl")

# Translators: this is one of the text attribute values for the following
# text attributes: "justification".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["left"] = C_("textattr", "left")

# Translators: this is one of the text attribute values for the following
# text attributes: "justification".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["right"] = C_("textattr", "right")

# Translators: this is one of the text attribute values for the following
# text attributes: "justification".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["center"] = C_("textattr", "center")

# Translators: this is one of the text attribute values for the following
# text attributes: "justification". In Gecko, when no justification has
# be explicitly set, they report a justification of "start".
#
_textAttributeTable["start"] = C_("textattr", "no justification")

# Translators: this is one of the text attribute values for the following
# text attributes: "justification".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["fill"] = C_("textattr", "fill")

# Translators: this is one of the text attribute values for the following
# text attributes: "stretch".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["ultra_condensed"] = C_("textattr", "ultra condensed")

# Translators: this is one of the text attribute values for the following
# text attributes: "stretch".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["extra_condensed"] = C_("textattr", "extra condensed")

# Translators: this is one of the text attribute values for the following
# text attributes: "stretch".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["condensed"] = C_("textattr", "condensed")

# Translators: this is one of the text attribute values for the following
# text attributes: "stretch".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["semi_condensed"] = C_("textattr", "semi condensed")

# Translators: this is one of the text attribute values for the following
# text attributes: "stretch" and "variant".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["normal"] = C_("textattr", "normal")

# Translators: this is one of the text attribute values for the following
# text attributes: "stretch".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["semi_expanded"] = C_("textattr", "semi expanded")

# Translators: this is one of the text attribute values for the following
# text attributes: "stretch".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["expanded"] = C_("textattr", "expanded")

# Translators: this is one of the text attribute values for the following
# text attributes: "stretch".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["extra_expanded"] = C_("textattr", "extra expanded")

# Translators: this is one of the text attribute values for the following
# text attributes: "stretch".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["ultra_expanded"] = C_("textattr", "ultra expanded")

# Translators: this is one of the text attribute values for the following
# text attributes: "variant".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["small_caps"] = C_("textattr", "small caps")

# Translators: this is one of the text attribute values for the following
# text attributes: "style".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["oblique"] = C_("textattr", "oblique")

# Translators: this is one of the text attribute values for the following
# text attributes: "style".
# See:
# http://developer.gnome.org/atk/stable/AtkText.html#AtkTextAttribute
#
_textAttributeTable["italic"] = C_("textattr", "italic")

# Translators: this is one of the text attribute values for the following
# text attributes: "paragraph-style".
# See:
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
_textAttributeTable["Default"] = C_("textattr", "Default")

# Translators: this is one of the text attribute values for the following
# text attributes: "paragraph-style".
# See:
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
_textAttributeTable["Text body"] = C_("textattr", "Text body")

# Translators: this is one of the text attribute values for the following
# text attributes: "paragraph-style".
# See:
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
_textAttributeTable["Heading"] = C_("textattr", "Heading")

# Translators: this is one of the text attribute values for the following
# text attributes: "vertical-align".
# See:
#http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-vertical-align
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
_textAttributeTable["baseline"] = C_("textattr", "baseline")

# Translators: this is one of the text attribute values for the following
# text attributes: "vertical-align".
# See:
#http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-vertical-align
#
_textAttributeTable["sub"] = C_("textattr", "sub")

# Translators: this is one of the text attribute values for the following
# text attributes: "vertical-align".
# See:
#http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-vertical-align
#
_textAttributeTable["super"] = C_("textattr", "super")

# Translators: this is one of the text attribute values for the following
# text attributes: "vertical-align".
# See:
#http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-vertical-align
#
_textAttributeTable["top"] = C_("textattr", "top")

# Translators: this is one of the text attribute values for the following
# text attributes: "vertical-align".
# See:
#http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-vertical-align
#
_textAttributeTable["text-top"] = C_("textattr", "text-top")

# Translators: this is one of the text attribute values for the following
# text attributes: "vertical-align".
# See:
#http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-vertical-align
#
_textAttributeTable["middle"] = C_("textattr", "middle")

# Translators: this is one of the text attribute values for the following
# text attributes: "vertical-align".
# See:
#http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-vertical-align
#
_textAttributeTable["bottom"] = C_("textattr", "bottom")

# Translators: this is one of the text attribute values for the following
# text attributes: "vertical-align".
# See:
#http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-vertical-align
#
_textAttributeTable["text-bottom"] = C_("textattr", "text-bottom")

# Translators: this is one of the text attribute values for the following
# text attributes: "vertical-align" and "writing-mode".
# See:
#http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-vertical-align
# http://www.w3.org/TR/2001/WD-css3-text-20010517/#PrimaryTextAdvanceDirection
#
_textAttributeTable["inherit"] = C_("textattr", "inherit")

# Translators: this is one of the text attribute values for the following
# text attributes: "writing-mode".
# See:
# http://www.w3.org/TR/2001/WD-css3-text-20010517/#PrimaryTextAdvanceDirection
#
_textAttributeTable["lr-tb"] = C_("textattr", "lr-tb")

# Translators: this is one of the text attribute values for the following
# text attributes: "writing-mode".
# See:
# http://www.w3.org/TR/2001/WD-css3-text-20010517/#PrimaryTextAdvanceDirection
#
_textAttributeTable["rl-tb"] = C_("textattr", "rl-tb")

# Translators: this is one of the text attribute values for the following
# text attributes: "writing-mode".
# See:
# http://www.w3.org/TR/2001/WD-css3-text-20010517/#PrimaryTextAdvanceDirection
#
_textAttributeTable["tb-rl"] = C_("textattr", "tb-rl")

# Translators: this is one of the text attribute values for the following
# text attributes: "writing-mode".
# See:
# http://www.w3.org/TR/2001/WD-css3-text-20010517/#PrimaryTextAdvanceDirection
#
_textAttributeTable["tb-lr"] = C_("textattr", "tb-lr")

# Translators: this is one of the text attribute values for the following
# text attributes: "writing-mode".
# See:
# http://www.w3.org/TR/2001/WD-css3-text-20010517/#PrimaryTextAdvanceDirection
#
_textAttributeTable["bt-rl"] = C_("textattr", "bt-rl")

# Translators: this is one of the text attribute values for the following
# text attributes: "writing-mode".
# See:
# http://www.w3.org/TR/2001/WD-css3-text-20010517/#PrimaryTextAdvanceDirection
#
_textAttributeTable["bt-lr"] = C_("textattr", "bt-lr")

# Translators: this is one of the text attribute values for the following
# text attributes: "writing-mode".
# See:
# http://www.w3.org/TR/2001/WD-css3-text-20010517/#PrimaryTextAdvanceDirection
#
_textAttributeTable["lr"] = C_("textattr", "lr")

# Translators: this is one of the text attribute values for the following
# text attributes: "writing-mode".
# See:
# http://www.w3.org/TR/2001/WD-css3-text-20010517/#PrimaryTextAdvanceDirection
#
_textAttributeTable["rl"] = C_("textattr", "rl")

# Translators: this is one of the text attribute values for the following
# text attributes: "writing-mode".
# See:
# http://www.w3.org/TR/2001/WD-css3-text-20010517/#PrimaryTextAdvanceDirection
#
_textAttributeTable["tb"] = C_("textattr", "tb")

# Translators: this is one of the text attribute values for the following
# text attributes: "strikethrough." It refers to the line style.
#
_textAttributeTable["solid"] = C_("textattr", "solid")

# Translators: this is one of the text attribute values for the following
# text attributes: "invalid". It is an indication that the text is not
# spelled correctly. See:
# https://developer.mozilla.org/en/Accessibility/AT-APIs/Gecko/TextAttrs
#
_textAttributeTable["spelling"] = C_("textattr", "spelling")

# Translators: This is the text-spelling attribute. See:
# http://wiki.services.openoffice.org/wiki/Accessibility/TextAttributes
#
_textAttributeTable["text-spelling"] = C_("textattr", "spelling")

def getTextAttributeKey(localizedTextAttr):
    """Given a localized text attribute, return the original text 
    attribute, (i.e. the key value).

    Arguments:
    - localizedTextAttr: the localized text attribute.

    Returns a string representing the original text attribute key for the
    localized text attribute.
    """

    for key, value in list(_textAttributeTable.items()):
        if value == localizedTextAttr:
            return key

    return localizedTextAttr

def getTextAttributeName(textAttr, script=None):
    """Given a text attribute, returns its localized equivalent.

    Arguments:
    - textAttr: the text attribute to get the localized equivalent of.

    Returns a string representing the localized equivalent for the text
    attribute.
    """

    # Normalize the name to an Atk name before attempting to look it up.
    #
    if script:
        textAttr = script.utilities.getAtkNameForAttribute(textAttr)

    return _textAttributeTable.get(textAttr, textAttr)
