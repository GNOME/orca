# Orca
#
# Copyright 2005-2007 Sun Microsystems Inc.
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
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

"""Provides various utility functions for Orca."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2007 Sun Microsystems Inc."
__license__   = "LGPL"

import string

import atspi
import chnames
import debug
import input_event
import orca_prefs
import orca_state
import phonnames
import punctuation_settings
import pronunciation_dict
import rolenames
import settings
import speech
import speechserver

from orca_i18n import _ # for gettext support

# Unicode currency symbols (populated by the getUnicodeCurrencySymbols()
# routine).
#
_unicodeCurrencySymbols = []

def isSameObject(obj1, obj2):
    if (obj1 == obj2):
        return True
    elif (not obj1) or (not obj2):
        return False

    try:
        if obj1.name != obj2.name:
            return False

        # When we're looking at children of objects that manage
        # their descendants, we will often get different objects
        # that point to the same logical child.  We want to be able
        # to determine if two objects are in fact pointing to the same child.
        # If we cannot do so easily (i.e., object equivalence), we examine
        # the hierarchy and the object index at each level.
        #
        parent1 = obj1
        parent2 = obj2
        while (parent1 and parent2 and \
                parent1.state.count(atspi.Accessibility.STATE_TRANSIENT) and \
                parent2.state.count(atspi.Accessibility.STATE_TRANSIENT)):
            if parent1.index != parent2.index:
                return False
            parent1 = parent1.parent
            parent2 = parent2.parent
        if parent1 and parent2 and parent1 == parent2:
            return True
    except:
        pass

    # In java applications, TRANSIENT state is missing for tree items
    # (fix for bug #352250)
    #
    try:
        parent1 = obj1
        parent2 = obj2
        while parent1 and parent2 and \
                parent1.role == rolenames.ROLE_LABEL and \
                parent2.role == rolenames.ROLE_LABEL:
            if parent1.index != parent2.index:
                return False
            parent1 = parent1.parent
            parent2 = parent2.parent
        if parent1 and parent2 and parent1 == parent2:
            return True
    except:
        pass

    return False

def appendString(text, newText, delimiter=" "):
    """Appends the newText to the given text with the delimiter in between
    and returns the new string.  Edge cases, such as no initial text or
    no newText, are handled gracefully."""

    if (not newText) or (len(newText) == 0):
        return text
    elif text and len(text):
        return text + delimiter + newText
    else:
        return newText

def __hasLabelForRelation(label):
    """Check if label has a LABEL_FOR relation

    Arguments:
    - label: the label in question

    Returns TRUE if label has a LABEL_FOR relation.
    """
    if (not label) or (label.role != rolenames.ROLE_LABEL):
        return False

    relations = label.relations

    for relation in relations:
        if relation.getRelationType() \
               == atspi.Accessibility.RELATION_LABEL_FOR:
            return True

    return False


def __isLabeling(label, object):
    """Check if label is connected via  LABEL_FOR relation with object

    Arguments:
    - object: the object in question
    - labeled: the label in question

    Returns TRUE if label has a relation LABEL_FOR for object.
    """

    if (not object) \
       or (not label) \
       or (label.role != rolenames.ROLE_LABEL):
        return False

    relations = label.relations
    if not relations:
        return False

    for relation in relations:
        if relation.getRelationType() \
               == atspi.Accessibility.RELATION_LABEL_FOR:

            for i in range(0, relation.getNTargets()):
                target = atspi.Accessible.makeAccessible(relation.getTarget(i))
                if target == object:
                    return True

    return False

def getUnicodeCurrencySymbols():
    """Return a list of the unicode currency symbols, populating the list
    if this is the first time that this routine has been called.

    Returns a list of unicode currency symbols.
    """

    global _unicodeCurrencySymbols

    if not _unicodeCurrencySymbols:
        _unicodeCurrencySymbols = [ \
            u'\u0024',     # dollar sign
            u'\u00A2',     # cent sign
            u'\u00A3',     # pound sign
            u'\u00A4',     # currency sign
            u'\u00A5',     # yen sign
            u'\u0192',     # latin small letter f with hook
            u'\u060B',     # afghani sign
            u'\u09F2',     # bengali rupee mark
            u'\u09F3',     # bengali rupee sign
            u'\u0AF1',     # gujarati rupee sign
            u'\u0BF9',     # tamil rupee sign
            u'\u0E3F',     # thai currency symbol baht
            u'\u17DB',     # khmer currency symbol riel
            u'\u2133',     # script capital m
            u'\u5143',     # cjk unified ideograph-5143
            u'\u5186',     # cjk unified ideograph-5186
            u'\u5706',     # cjk unified ideograph-5706
            u'\u5713',     # cjk unified ideograph-5713
            u'\uFDFC',     # rial sign
        ]

        # Add 20A0 (EURO-CURRENCY SIGN) to 20B5 (CEDI SIGN)
        #
        for ordChar in range(ord(u'\u20A0'), ord(u'\u20B5') + 1):
            _unicodeCurrencySymbols.append(unichr(ordChar))

    return _unicodeCurrencySymbols

def getDisplayedLabel(object):
    """If there is an object labelling the given object, return the
    text being displayed for the object labelling this object.
    Otherwise, return None.

    Argument:
    - object: the object in question

    Returns the string of the object labelling this object, or None
    if there is nothing of interest here.
    """

    # For some reason, some objects are labelled by the same thing
    # more than once.  Go figure, but we need to check for this.
    #
    label = None
    relations = object.relations
    allTargets = []

    for relation in relations:
        if relation.getRelationType() \
               == atspi.Accessibility.RELATION_LABELLED_BY:

            # The object can be labelled by more than one thing, so we just
            # get all the labels (from unique objects) and append them
            # together.  An example of such objects live in the "Basic"
            # page of the gnome-accessibility-keyboard-properties app.
            # The "Delay" and "Speed" objects are labelled both by
            # their names and units.
            #
            for i in range(0, relation.getNTargets()):
                target = atspi.Accessible.makeAccessible(relation.getTarget(i))
                if not target in allTargets:
                    allTargets.append(target)
                    label = appendString(label, getDisplayedText(target))

    # [[[TODO: HACK - we've discovered oddness in hierarchies such as
    # the gedit Edit->Preferences dialog.  In this dialog, we have
    # labeled groupings of objects.  The grouping is done via a FILLER
    # with two children - one child is the overall label, and the
    # other is the container for the grouped objects.  When we detect
    # this, we add the label to the overall context.
    #
    # We are also looking for objects which have a PANEL or a FILLER as
    # parent, and its parent has more children. Through these children,
    # a potential label with LABEL_FOR relation may exists. We want to
    # present this label.
    # This case can be seen in FileChooserDemo application, in Open dialog
    # window, the line with "Look In" label, a combobox and some presentation
    # buttons.]]]
    #
    if not label:

        potentialLabel = None
        useLabel = False
        if ((object.role == rolenames.ROLE_FILLER) \
                or (object.role == rolenames.ROLE_PANEL)) \
            and (object.childCount == 2):

            potentialLabel = object.child(0)
            secondChild = object.child(1)
            useLabel = potentialLabel.role == rolenames.ROLE_LABEL \
                    and ((secondChild.role == rolenames.ROLE_FILLER) \
                            or (secondChild.role == rolenames.ROLE_PANEL)) \
                    and not __hasLabelForRelation(potentialLabel)
        else:
            parent = object.parent
            if parent and \
                ((parent.role == rolenames.ROLE_FILLER) \
                        or (parent.role == rolenames.ROLE_PANEL)):
                for i in range (0, parent.childCount):
                    try:
                        potentialLabel = parent.child(i)
                        useLabel = __isLabeling(potentialLabel, object)
                        if useLabel:
                            break
                    except:
                        pass

        if useLabel and potentialLabel:
            label = potentialLabel.name

    return label

def getRealActiveDescendant(obj):
    """Given an object that should be a child of an object that
    manages its descendants, return the child that is the real
    active descendant carrying useful information.

    Arguments:
    - obj: an object that should be a child of an object that
    manages its descendants.
    """

    # If obj is a table cell and all of it's children are table cells
    # (probably cell renderers), then return the first child which has
    # a non zero length text string. If no such object is found, just
    # fall through and use the default approach below. See bug #376791
    # for more details.
    #
    if obj.role == rolenames.ROLE_TABLE_CELL and obj.childCount:
        nonTableCellFound = False
        for i in range (0, obj.childCount):
            if obj.child(i).role != rolenames.ROLE_TABLE_CELL:
                nonTableCellFound = True
        if not nonTableCellFound:
            for i in range (0, obj.childCount):
                if obj.child(i).text:
                    text = obj.child(i).text.getText(0, -1)
                    if len(text) != 0:
                        return obj.child(i)

    # [[[TODO: WDW - this is an odd hacky thing I've somewhat drawn
    # from Gnopernicus.  The notion here is that we get an active
    # descendant changed event, but that object tends to have children
    # itself and we need to decide what to do.  Well...the idea here
    # is that the last child (Gnopernicus chooses child(1)), tends to
    # be the child with information.  The previous children tend to
    # be non-text or just there for spacing or something.  You will
    # see this in the various table demos of gtk-demo and you will
    # also see this in the Contact Source Selector in Evolution.
    #
    # Just note that this is most likely not a really good solution
    # for the general case.  That needs more thought.  But, this
    # comment is here to remind us this is being done in poor taste
    # and we need to eventually clean up our act.]]]
    #
    if obj and obj.childCount:
        return obj.child(obj.childCount - 1)
    else:
        return obj

def findFocusedObject(root):
    """Returns the accessible that has focus under or including the
    given root.

    TODO: This will currently traverse all children, whether they are
    visible or not and/or whether they are children of parents that
    manage their descendants.  At some point, this method should be
    optimized to take such things into account.

    Arguments:
    - root: the root object where to start searching

    Returns the object with the FOCUSED state or None if no object with
    the FOCUSED state can be found.
    """

    if root.state.count(atspi.Accessibility.STATE_FOCUSED):
        return root

    for i in range(0, root.childCount):
        try:
            candidate = findFocusedObject(root.child(i))
            if candidate:
                return candidate
        except:
            pass

    return None

def getClickCount(lastInputEvent, inputEvent):
    """Return the count of the number of clicks a user has made to one of the
    keys on the keyboard.

    Arguments:
    - lastInputEvent: the last input event.
    - inputEvent: the current input event.
    """

    if not isinstance(lastInputEvent, input_event.KeyboardEvent) or \
       not isinstance(inputEvent, input_event.KeyboardEvent):
        orca_state.clickCount = 0
        return orca_state.clickCount

    if (lastInputEvent.hw_code != inputEvent.hw_code) or \
       (lastInputEvent.modifiers != inputEvent.modifiers):
        orca_state.clickCount = 1
        return orca_state.clickCount

    if (inputEvent.time - lastInputEvent.time) < settings.doubleClickTimeout:
        orca_state.clickCount += 1
    else:
        orca_state.clickCount = 0
    return orca_state.clickCount+1

def isDesiredFocusedItem(obj, rolesList):
    """Called to determine if the given object and it's hierarchy of
       parent objects, each have the desired roles.

    Arguments:
    - obj: the accessible object to check.
    - rolesList: the list of desired roles for the components and the
      hierarchy of its parents.

    Returns True if all roles match.
    """

    current = obj
    for i in range(0, len(rolesList)):
        if (current == None) or (current.role != rolesList[i]):
            return False
        current = current.parent

    return True

def speakMisspeltWord(allTokens, badWord):
    """Called by various spell checking routine to speak the misspelt word,
       plus the context that it is being used in.

    Arguments:
    - allTokens: a list of all the words.
    - badWord: the misspelt word.
    """

    # Create an utterance to speak consisting of the misspelt
    # word plus the context where it is used (upto five words
    # to either side of it).
    #
    for i in range(0, len(allTokens)):
        if allTokens[i].startswith(badWord):
            min = i - 5
            if min < 0:
                min = 0
            max = i + 5
            if max > (len(allTokens) - 1):
                max = len(allTokens) - 1

            utterances = [_("Misspelled word: "), badWord, \
                          _(" Context is ")] + allTokens[min:max+1]

            # Turn the list of utterances into a string.
            text = " ".join(utterances)
            speech.speak(text)

def textLines(obj):
    """Creates a generator that can be used to iterate over each line
    of a text object, starting at the caret offset.

    Arguments:
    - obj: an Accessible that has a text specialization

    Returns an iterator that produces elements of the form:
    [SayAllContext, acss], where SayAllContext has the text to be
    spoken and acss is an ACSS instance for speaking the text.
    """
    if not obj:
        return

    text = obj.text
    if not text:
        return

    length = text.characterCount
    offset = text.caretOffset

    # Get the next line of text to read
    #
    done = False
    while not done:
        lastEndOffset = -1
        while offset < length:
            [string, startOffset, endOffset] = text.getTextAtOffset(
                offset,
                atspi.Accessibility.TEXT_BOUNDARY_LINE_START)

            # [[[WDW - HACK: well...gnome-terminal sometimes wants to
            # give us outrageous values back from getTextAtOffset
            # (see http://bugzilla.gnome.org/show_bug.cgi?id=343133),
            # so we try to handle it.]]]
            #
            if startOffset < 0:
                break

            # [[[WDW - HACK: this is here because getTextAtOffset
            # tends not to be implemented consistently across toolkits.
            # Sometimes it behaves properly (i.e., giving us an endOffset
            # that is the beginning of the next line), sometimes it
            # doesn't (e.g., giving us an endOffset that is the end of
            # the current line).  So...we hack.  The whole 'max' deal
            # is to account for lines that might be a brazillion lines
            # long.]]]
            #
            if endOffset == lastEndOffset:
                offset = max(offset + 1, lastEndOffset + 1)
                lastEndOffset = endOffset
                continue

            lastEndOffset = endOffset
            offset = endOffset

            string = adjustForRepeats(string)
            if string.isupper():
                voice = settings.voices[settings.UPPERCASE_VOICE]
            else:
                voice = settings.voices[settings.DEFAULT_VOICE]

            yield [speechserver.SayAllContext(obj, string,
                                              startOffset, endOffset),
                   voice]

        moreLines = False
        relations = obj.relations
        for relation in relations:
            if relation.getRelationType()  \
                   == atspi.Accessibility.RELATION_FLOWS_TO:
                obj = atspi.Accessible.makeAccessible(relation.getTarget(0))

                text = obj.text
                if not text:
                    return

                length = text.characterCount
                offset = 0
                moreLines = True
                break
        if not moreLines:
            done = True

def _addRepeatSegment(segment, line, respectPunctuation=True):
    """Add in the latest line segment, adjusting for repeat characters
    and punctuation.

    Arguments:
    - segment: the segment of repeated characters.
    - line: the current built-up line to characters to speak.
    - respectPunctuation: if False, ignore punctuation level.

    Returns: the current built-up line plus the new segment, after
    adjusting for repeat character counts and punctuation.
    """

    style = settings.verbalizePunctuationStyle
    isPunctChar = True
    try:
        level, action = punctuation_settings.getPunctuationInfo(segment[0])
    except:
        isPunctChar = False
    count = len(segment)
    if (count >= settings.repeatCharacterLimit) \
       and (not segment[0] in string.whitespace):
        if (not respectPunctuation) \
           or (isPunctChar and (style <= level)):
            repeatChar = chnames.getCharacterName(segment[0])
            line += _(" %d %s characters ") % (count, repeatChar)
        else:
            line += segment
    else:
        line += segment

    return line

def adjustForRepeats(line):
    """Adjust line to include repeat character counts.
    As some people will want this and others might not,
    there is a setting in settings.py that determines
    whether this functionality is enabled.

    repeatCharacterLimit = <n>

    If <n> is 0, then there would be no repeat characters.
    Otherwise <n> would be the number of same characters (or more)
    in a row that cause the repeat character count output.
    If the value is set to 1, 2 or 3 then it's treated as if it was
    zero. In other words, no repeat character count is given.

    Arguments:
    - line: the string to adjust for repeat character counts.

    Returns: a new line adjusted for repeat character counts (if enabled).
    """

    line = line.decode("UTF-8")

    if (len(line) < 4) or (settings.repeatCharacterLimit < 4):
        return line.encode("UTF-8")

    newLine = u''
    segment = lastChar = line[0]

    multipleChars = False
    for i in range(1, len(line)):
        if line[i] == lastChar:
            segment += line[i]
        else:
            multipleChars = True
            newLine = _addRepeatSegment(segment, newLine)
            segment = line[i]

        lastChar = line[i]

    newLine = _addRepeatSegment(segment, newLine, multipleChars)

    return newLine.encode("UTF-8")

def adjustForPronunciation(line):
    """Adjust the line to replace words in the pronunciation dictionary,
    with what those words actually sound like.

    Arguments:
    - line: the string to adjust for words in the pronunciation dictionary.

    Returns: a new line adjusted for words found in the pronunciation
    dictionary.
    """

    line = line.decode("UTF-8")
    newLine = segment = u''

    for i in range(0, len(line)):
        if isWordDelimiter(line[i]):
            if len(segment) != 0:
                newLine = newLine + pronunciation_dict.getPronunciation(segment)
            newLine = newLine + line[i]
            segment = u''
        else:
            segment += line[i]

    if len(segment) != 0:
        newLine = newLine + pronunciation_dict.getPronunciation(segment)

    return newLine.encode("UTF-8")

def getLinkIndex(obj, characterIndex):
    """A brute force method to see if an offset is a link.  This
    is provided because not all Accessible Hypertext implementations
    properly support the getLinkIndex method.  Returns an index of
    0 or greater of the characterIndex is on a hyperlink.

    Arguments:
    -obj: the Accessible object with the Accessible Hypertext specialization
    -characterIndex: the text position to check
    """

    if not obj:
        return -1

    text = obj.text
    if not text:
        return -1

    hypertext = obj.hypertext
    if not hypertext:
        return -1

    for i in range(0, hypertext.getNLinks()):
        link = hypertext.getLink(i)
        if (characterIndex >= link.startIndex) \
           and (characterIndex <= link.endIndex):
            return i

    return -1

def isWordDelimiter(character):
    """Returns True if the given character is a word delimiter.

    Arguments:
    - character: the character in question

    Returns True if the given character is a word delimiter.
    """

    if isinstance(character, unicode):
        character = character.encode("UTF-8")

    return (character in string.whitespace) \
           or (character in '!*+,-./:;<=>?@[\]^_{|}')

def getFrame(obj):
    """Returns the frame containing this object, or None if this object
    is not inside a frame.

    Arguments:
    - obj: the Accessible object
    """

    debug.println(debug.LEVEL_FINEST,
                  "Finding frame for source.name="
                  + obj.accessibleNameToString())

    while obj \
          and (obj != obj.parent) \
          and (obj.role != rolenames.ROLE_FRAME):
        obj = obj.parent
        debug.println(debug.LEVEL_FINEST, "--> obj.name="
                      + obj.accessibleNameToString())

    if obj and (obj.role == rolenames.ROLE_FRAME):
        pass
    else:
        obj = None

    return obj

def getTopLevel(obj):
    """Returns the top-level object (frame, dialog ...) containing this
    object, or None if this object is not inside a top-level object.

    Arguments:
    - obj: the Accessible object
    """

    debug.println(debug.LEVEL_FINEST,
                  "Finding top-level object for source.name="
                  + obj.accessibleNameToString())

    while obj \
          and obj.parent \
          and (obj != obj.parent) \
          and (obj.parent.role != rolenames.ROLE_APPLICATION):
        obj = obj.parent
        debug.println(debug.LEVEL_FINEST, "--> obj.name="
                      + obj.accessibleNameToString())

    if obj and obj.parent and (obj.parent.role == rolenames.ROLE_APPLICATION):
        pass
    else:
        obj = None

    return obj

def getTopLevelName(obj):
    """ Returns the name of the top-level object. See getTopLevel.
    """
    top = getTopLevel(obj)
    if (not top) or (not top.name):
        return ""
    else:
        return top.name
