# Orca
#
# Copyright 2005-2006 Sun Microsystems Inc.
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

import atspi
import debug
import speech
import speechserver

from orca_i18n import _ # for gettext support

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
    of a text object, starting at the caret offset.  One can do something
    like the following to access the lines:

    for line in atspi.textLines(orca.locusOfFocus.text):
        <<<do something with the line>>>

    Arguments:
    - obj: an Accessible that has a text specialization

    Returns a tuple: [SayAllContext, acss], where SayAllContext has the
    text to be spoken and acss is an ACSS instance for speaking the text.
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
    lastEndOffset = -1
    while offset < length:
        [string, startOffset, endOffset] = text.getTextAtOffset(
            offset,
            atspi.Accessibility.TEXT_BOUNDARY_LINE_START)

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

        # Strip trailing new lines
        #
        #if string[-1:] == "\n":
        #    string = string[0][:-1]

        yield [speechserver.SayAllContext(obj, string, startOffset, endOffset),
               None]

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
