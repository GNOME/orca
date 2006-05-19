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

import string

import atspi
import debug
import rolenames
import speech
import speechserver

from orca_i18n import _ # for gettext support

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
        
def getDisplayedLabel(object):
    """If there is an object labelling the given object, return the
    text being displayed for the object labelling this object.
    Otherwise, return None.

    Argument:
    - object: the object in question

    Returns the string of the object labelling this object, or None
    if there is nothing of interest here.
    """
    label = None
    relations = object.relations
    
    # For some reason, some objects are labelled by the same thing
    # more than once.  Go figure, but we need to check for this.
    #
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
    return label

def __getDisplayedTextInComboBox(combo):
    
    """Returns the text being displayed in a combo box.  If nothing is
    displayed, then None is returned.

    Arguments:
    - combo: the combo box

    Returns the text in the combo box or an empty string if nothing is
    displayed.
    """

    displayedText = None
    
    # Find the text displayed in the combo box.  This is either:
    #
    # 1) The last text object that's a child of the combo box
    # 2) The selected child of the combo box.
    # 3) The contents of the text of the combo box itself when
    #    treated as a text object.
    #
    # Preference is given to #1, if it exists.
    #
    # If the label of the combo box is the same as the utterance for
    # the child object, then this utterance is only displayed once.
    #
    # [[[TODO: WDW - Combo boxes are complex beasts.  This algorithm
    # needs serious work.  Logged as bugzilla bug 319745.]]]
    #
    textObj = None
    for i in range(0, combo.childCount):
        child = combo.child(i)
        if child.role == rolenames.ROLE_TEXT:
            textObj = child

    if textObj:
        [displayedText, startOffset, endOffset] = \
            atspi.getTextLineAtCaret(textObj)
        #print "TEXTOBJ", displayedText
    else:
        selectedItem = None
        comboSelection = combo.selection
        if comboSelection and comboSelection.nSelectedChildren > 0:
            selectedItem = atspi.Accessible.makeAccessible(
                comboSelection.getSelectedChild(0))
        if selectedItem:
            displayedText = getDisplayedText(selectedItem)
            #print "SELECTEDITEM", displayedText
        elif combo.name and len(combo.name):
            # We give preference to the name over the text because
            # the text for combo boxes seems to never change in
            # some cases.  The main one where we see this is in
            # the gaim "Join Chat" window.
            #
            displayedText = combo.name
            #print "NAME", displayedText
        elif combo.text:
            [displayedText, startOffset, endOffset] = \
                atspi.getTextLineAtCaret(combo)
            #print "TEXT", displayedText

    return displayedText

def getDisplayedText(obj):
    """Returns the text being displayed for an object.

    Arguments:
    - obj: the object

    Returns the text being displayed for an object or None if there isn't
    any text being shown.
    """

    displayedText = None

    if obj.role == rolenames.ROLE_COMBO_BOX:
        return __getDisplayedTextInComboBox(obj)

    # The accessible text of an object is used to represent what is
    # drawn on the screen.
    #
    if obj.text:
        displayedText = obj.text.getText(0, -1)

    if (not displayedText) or (len(displayedText) == 0):
        displayedText = obj.name

    # [[[WDW - HACK because push buttons can have labels as their
    # children.  An example of this is the Font: button on the General
    # tab in the Editing Profile dialog in gnome-terminal.
    #
    if ((not displayedText) or (len(displayedText) == 0)) \
       and obj.role == rolenames.ROLE_PUSH_BUTTON:
        for i in range(0, obj.childCount):
            child = obj.child(i)
            if child.role == rolenames.ROLE_LABEL:
                childText = getDisplayedText(child)
                if childText and len(childText):
                    displayedText = appendString(displayedText, childText)
 
    return displayedText

def getRealActiveDescendant(obj):
    """Given an object that should be a child of an object that
    manages its descendants, return the child that is the real
    active descendant carrying useful information.

    Arguments:
    - obj: an object that should be a child of an object that
    manages its descendants.
    """

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

def isWordDelimiter(character):
    """Returns True if the given character is a word delimiter.

    Arguments:
    - character: the character in question

    Returns True if the given character is a word delimiter.
    """

    return (character in string.whitespace) \
           or (character in string.punctuation)
