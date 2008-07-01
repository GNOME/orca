# Orca
#
# Copyright 2006-2008 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Provides getTextAttributeName method that maps each text attribute
into its localized equivalent."""

__id__        = "$Id:$"
__version__   = "$Revision:$"
__date__      = "$Date:$"
__copyright__ = "Copyright (c) 2008 Sun Microsystems Inc."
__license__   = "LGPL"

from orca_i18n import Q_        # to provide qualified translatable strings

# Translators: this is a structure to assist in the generation of
# localized strings for the various text attributes. 
#
# Information can be found in the Atk documentation at:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
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
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["bg-color"] = Q_("textattr|background color")

# Translators: this attribute specifies whether to make the background
# color for each character the height of the highest font used on the
# current line, or the height of the font used for the current character.
# It will be a "true" or "false" value.
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["bg-full-height"] = Q_("textattr|background full height")

# Translators: this attribute specifies whether a GdkBitmap is set for 
# stippling the background color. It will be a "true" or "false" value.
# See
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["bg-stipple"] = Q_("textattr|background stipple")

# Translators: this attribute specifies the direction of the text.
# Values are "none", "ltr" or "rtl".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["direction"] = Q_("textattr|direction")

# Translators: this attribute specifies whether the text is editable.
# It will be a "true" or "false" value.
# See
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["editable"] = Q_("textattr|editable")

# Translators: this attribute specifies the font family name of the text.
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["family-name"] = Q_("textattr|family name")

# Translators: this attribute specifies the foreground color of the text.
# The value is an RGB value of the format "u,u,u".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["fg-color"] = Q_("textattr|foreground color")

# Translators: this attribute specifies whether a GdkBitmap is set for
# stippling the foreground color. It will be a "true" or "false" value.
# See
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["fg-stipple"] = Q_("textattr|foreground stipple")

# Translators: this attribute specifies the effect applied to the font 
# used by the text.
# See:
# http://www.w3.org/TR/2002/WD-css3-fonts-20020802/#font-effect
#
_textAttributeTable["font-effect"] = Q_("textattr|font effect")

# Translators: this attribute specifies the indentation of the text
# (in pixels).
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["indent"] = Q_("textattr|indent")

# Translators: this attribute specifies whether the text is invisible.
# It will be a "true" or "false" value.
# See
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["invisible"] = Q_("textattr|invisible")

# Translators: this attribute specifies how the justification of the text.
# Values are "left", "right", "center" or "fill".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["justification"] = Q_("textattr|justification")

# Translators: this attribute specifies the language that the text is
# written in.
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["language"] = Q_("textattr|language")

# Translators: this attribute specifies the pixel width of the left margin.
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["left-margin"] = Q_("textattr|left margin")

# Translators: this attribute specifies the height of the line of text.
# See:
# http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-line-height
#
_textAttributeTable["line-height"] = Q_("textattr|line height")

# Translators: this attribute refers to the named style which is associated
# with the entire paragraph and which controls the default formatting 
# (font, text size, alignment, etc.) of that paragraph. Examples of 
# paragraph styles include "Heading 1", "Heading 2", "Caption", "Footnote",
# "Text Body", "Title", and "Subtitle".
#
_textAttributeTable["paragraph-style"] = Q_("textattr|paragraph style")

# Translators: this attribute specifies the pixels of blank space to 
# leave above each newline-terminated line.
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["pixels-above-lines"] = Q_("textattr|pixels above lines")

# Translators: this attribute specifies the pixels of blank space to
# leave below each newline-terminated line.
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["pixels-below-lines"] = Q_("textattr|pixels below lines")

# Translators: this attribute specifies the pixels of blank space to
# leave between wrapped lines inside the same newline-terminated line
# (paragraph).
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["pixels-inside-wrap"] = Q_("textattr|pixels inside wrap")

# Translators: this attribute specifies the pixel width of the right margin.
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["right-margin"] = Q_("textattr|right margin")

# Translators: this attribute specifies the number of pixels that the 
# text characters are risen above the baseline.
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["rise"] = Q_("textattr|rise")

# Translators: this attribute specifies the scale of the characters. The
# value is a string representation of a double.
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["scale"] = Q_("textattr|scale")

# Translators: this attribute specifies the size of the text.
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["size"] = Q_("textattr|size")

# Translators: this attribute specifies the stretch of he text, if set.
# Values are "ultra_condensed", "extra_condensed", "condensed",
# "semi_condensed", "normal", "semi_expanded", "expanded",
# "extra_expanded" or "ultra_expanded".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["stretch"] = Q_("textattr|stretch")

# Translators: this attribute specifies whether the text is strike though
# (in other words, whether there is a line drawn through it). Values are
# "true" or "false".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["strikethrough"] = Q_("textattr|strike through")

# Translators: this attribute specifies the slant style of the text,
# if set. Values are "normal", "oblique" or "italic".
# See: 
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["style"] = Q_("textattr|style")

# Translators: this attribute specifies the decoration of the text.
# See:
# http://www.w3.org/TR/1998/REC-CSS2-19980512/text.html#propdef-text-decoration
#
_textAttributeTable["text-decoration"] = Q_("textattr|text decoration")

# Translators: this attribute specifies the angle at which the text is
# displayed (i.e. rotated from the norm) and is represented in degrees 
# of rotation.
# See:
# http://www.w3.org/TR/2003/CR-css3-text-20030514/#glyph-orientation-horizontal
#
_textAttributeTable["text-rotation"] = Q_("textattr|text rotation")

# Translators: this attribute specifies the shadow effects applied to the text.
# See:
# http://www.w3.org/TR/1998/REC-CSS2-19980512/text.html#propdef-text-shadow
#
_textAttributeTable["text-shadow"] = Q_("textattr|text shadow")

# Translators: this attributes specifies whether the text is underlined.
# Values are "none", "single", "double" or "low".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["underline"] = Q_("textattr|underline")

# Translators: this attribute specifies the capitalization variant of
# the text, if set. Values are "normal" or "small_caps".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["variant"] = Q_("textattr|variant")

# Translators: this attributes specifies what vertical alignment property
# has been applied to the text.
# See:
#http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-vertical-align
#
_textAttributeTable["vertical-align"] = Q_("textattr|vertical align")

# Translators: this attribute specifies the weight of the text.
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
# http://www.w3.org/TR/1998/REC-CSS2-19980512/fonts.html#propdef-font-weight
#
_textAttributeTable["weight"] = Q_("textattr|weight")

# Translators: this attribute specifies the wrap mode of the text, if any.
# Values are "none", "char" or "word".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["wrap-mode"] = Q_("textattr|wrap mode")

# Translators: this attribute specifies the way the text is written.
# Whether the text is from left to right or right to left and whether it
# is from top to bottom or bottom to top.
#
_textAttributeTable["writing-mode"] = Q_("textattr|writing mode")


# The following are the known values of some of these text attributes.
# These values were found in the Atk documentation at:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
# No doubt there will be more, and as they are found, they can be added
# to this table so they can be translated.
#

# Translators: this is one of the text attribute values for the following
# text attributes: "invisible", "editable", bg-full-height", "strikethrough",
# "bg-stipple" and "fg-stipple".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["true"] = Q_("textattr|true")

# Translators: this is one of the text attribute values for the following
# text attributes: "invisible", "editable", bg-full-height", "strikethrough",
# "bg-stipple" and "fg-stipple".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["false"] = Q_("textattr|false")

# Translators: this is one of the text attribute values for the following
# text attributes: "underline", "wrap mode" and "direction".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["none"] = Q_("textattr|none")

# Translators: this is one of the text attribute values for the following
# text attributes: "underline".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["single"] = Q_("textattr|single")

# Translators: this is one of the text attribute values for the following
# text attributes: "underline".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["double"] = Q_("textattr|double")

# Translators: this is one of the text attribute values for the following
# text attributes: "underline".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["low"] = Q_("textattr|low")

# Translators: this is one of the text attribute values for the following
# text attributes: "wrap mode".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["char"] = Q_("textattr|char")

# Translators: this is one of the text attribute values for the following
# text attributes: "wrap mode".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["word"] = Q_("textattr|word")

# Translators: this is one of the text attribute values for the following
# text attributes: "direction".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["ltr"] = Q_("textattr|ltr")

# Translators: this is one of the text attribute values for the following
# text attributes: "direction".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["rtl"] = Q_("textattr|rtl")

# Translators: this is one of the text attribute values for the following
# text attributes: "justification".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["left"] = Q_("textattr|left")

# Translators: this is one of the text attribute values for the following
# text attributes: "justification".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["right"] = Q_("textattr|right")

# Translators: this is one of the text attribute values for the following
# text attributes: "justification".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["center"] = Q_("textattr|center")

# Translators: this is one of the text attribute values for the following
# text attributes: "justification".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["fill"] = Q_("textattr|fill")

# Translators: this is one of the text attribute values for the following
# text attributes: "stretch".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["ultra_condensed"] = Q_("textattr|ultra condensed")

# Translators: this is one of the text attribute values for the following
# text attributes: "stretch".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["extra_condensed"] = Q_("textattr|extra condensed")

# Translators: this is one of the text attribute values for the following
# text attributes: "stretch".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["condensed"] = Q_("textattr|condensed")

# Translators: this is one of the text attribute values for the following
# text attributes: "stretch".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["semi_condensed"] = Q_("textattr|semi condensed")

# Translators: this is one of the text attribute values for the following
# text attributes: "stretch" and "variant".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["normal"] = Q_("textattr|normal")

# Translators: this is one of the text attribute values for the following
# text attributes: "stretch".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["semi_expanded"] = Q_("textattr|semi expanded")

# Translators: this is one of the text attribute values for the following
# text attributes: "stretch".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["expanded"] = Q_("textattr|expanded")

# Translators: this is one of the text attribute values for the following
# text attributes: "stretch".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["extra_expanded"] = Q_("textattr|extra expanded")

# Translators: this is one of the text attribute values for the following
# text attributes: "stretch".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["ultra_expanded"] = Q_("textattr|ultra expanded")

# Translators: this is one of the text attribute values for the following
# text attributes: "variant".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["small_caps"] = Q_("textattr|small caps")

# Translators: this is one of the text attribute values for the following
# text attributes: "style".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["oblique"] = Q_("textattr|oblique")

# Translators: this is one of the text attribute values for the following
# text attributes: "style".
# See:
# http://library.gnome.org/devel/atk/1.22/AtkText.html#AtkTextAttribute
#
_textAttributeTable["italic"] = Q_("textattr|italic")

# Translators: this is one of the text attribute values for the following
# text attributes: "paragraph".
#
_textAttributeTable["Default"] = Q_("textattr|Default")

# Translators: this is one of the text attribute values for the following
# text attributes: "vertical-align".
# See:
#http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-vertical-align
#
_textAttributeTable["baseline"] = Q_("textattr|baseline")

# Translators: this is one of the text attribute values for the following
# text attributes: "vertical-align".
# See:
#http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-vertical-align
#
_textAttributeTable["sub"] = Q_("textattr|sub")

# Translators: this is one of the text attribute values for the following
# text attributes: "vertical-align".
# See:
#http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-vertical-align
#
_textAttributeTable["super"] = Q_("textattr|super")

# Translators: this is one of the text attribute values for the following
# text attributes: "vertical-align".
# See:
#http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-vertical-align
#
_textAttributeTable["top"] = Q_("textattr|top")

# Translators: this is one of the text attribute values for the following
# text attributes: "vertical-align".
# See:
#http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-vertical-align
#
_textAttributeTable["text-top"] = Q_("textattr|text-top")

# Translators: this is one of the text attribute values for the following
# text attributes: "vertical-align".
# See:
#http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-vertical-align
#
_textAttributeTable["middle"] = Q_("textattr|middle")

# Translators: this is one of the text attribute values for the following
# text attributes: "vertical-align".
# See:
#http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-vertical-align
#
_textAttributeTable["bottom"] = Q_("textattr|bottom")

# Translators: this is one of the text attribute values for the following
# text attributes: "vertical-align".
# See:
#http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-vertical-align
#
_textAttributeTable["text-bottom"] = Q_("textattr|text-bottom")

# Translators: this is one of the text attribute values for the following
# text attributes: "vertical-align".
# See:
#http://www.w3.org/TR/1998/REC-CSS2-19980512/visudet.html#propdef-vertical-align
#
_textAttributeTable["inherit"] = Q_("textattr|inherit")

# Translators: this is one of the text attribute values for the following
# text attributes: "writing-mode". It indicates that text is displayed
# from left to right and top to bottom on the screen.
#
_textAttributeTable["lr-tb"] = Q_("textattr|lr-tb")

# Translators: this is one of the text attribute values for the following
# text attributes: "writing-mode". It indicates that text is displayed 
# from right to left and top to bottom on the screen.
#
_textAttributeTable["rl-tb"] = Q_("textattr|rl-tb")

def getTextAttributeKey(localizedTextAttr):
    """Given a localized text attribute, return the original text 
    attribute, (i.e. the key value).

    Arguments:
    - localizedTextAttr: the localized text attribute.

    Returns a string representing the original text attribute key for the
    localized text attribute.
    """

    if isinstance(localizedTextAttr, unicode):
        localizedTextAttr = localizedTextAttr.encode("UTF-8")

    for key, value in _textAttributeTable.items():
        if value == localizedTextAttr:
            return key

    return localizedTextAttr

def getTextAttributeName(textAttr):
    """Given a text attribute, returns its localized equivalent.

    Arguments:
    - textAttr: the text attribute to get the localized equivalent of.

    Returns a string representing the localized equivalent for the text
    attribute.
    """

    if isinstance(textAttr, unicode):
        textAttr = textAttr.encode("UTF-8")

    try:
        return _textAttributeTable[textAttr]
    except:
        return textAttr

