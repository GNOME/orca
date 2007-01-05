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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2006 Sun Microsystems Inc."
__license__   = "LGPL"

try:
    # This can fail due to gtk not being available.  We want to
    # be able to recover from that if possible.  The main driver
    # for this is to allow "orca --text-setup" to work even if
    # the desktop is not running.
    #
    import gtk
except:
    pass

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

# Embedded object character used to indicate that an object is
# embedded in a string.
#
EMBEDDED_OBJECT_CHARACTER = u'\ufffc'

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
        [displayedText, caretOffset, startOffset] = getTextLineAtCaret(textObj)
        #print "TEXTOBJ", displayedText
    else:
        selectedItem = None
        comboSelection = combo.selection
        if comboSelection and comboSelection.nSelectedChildren > 0:
            try:
                selectedItem = atspi.Accessible.makeAccessible(
                    comboSelection.getSelectedChild(0))
            except:
                pass
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
            [displayedText, caretOffset, startOffset] = \
                getTextLineAtCaret(combo)
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

def getTextLineAtCaret(obj):
    """Gets the line of text where the caret is.

    Argument:
    - obj: an Accessible object that implements the AccessibleText
           interface

    Returns the [string, caretOffset, startOffset] for the line of text
    where the caret is.
    """

    # Get the the AccessibleText interrface
    #
    text = obj.text
    if not text:
        return ["", 0, 0]

    if text.caretOffset == text.characterCount:
        caretOffset = max(0, text.caretOffset - 1)
    else:
        caretOffset = text.caretOffset

    # Get the line containing the caret
    #
    [string, startOffset, endOffset] = text.getTextAtOffset(
        caretOffset, atspi.Accessibility.TEXT_BOUNDARY_LINE_START)

    # Sometimes we get the trailing line-feed-- remove it
    #
    content = string.decode("UTF-8")
    if content[-1:] == "\n":
        content = content[:-1]

    return [content.encode("UTF-8"), text.caretOffset, startOffset]

def getNodeLevel(obj):
    """Determines the node level of this object if it is in a tree
    relation, with 0 being the top level node.  If this object is
    not in a tree relation, then -1 will be returned.

    Arguments:
    -obj: the Accessible object
    """

    if not obj:
        return -1

    nodes = []
    node = obj
    done = False
    while not done:
        relations = node.relations
        node = None
        for relation in relations:
            if relation.getRelationType() \
                   == atspi.Accessibility.RELATION_NODE_CHILD_OF:
                node = atspi.Accessible.makeAccessible(relation.getTarget(0))
                break

        # We want to avoid situations where something gives us an
        # infinite cycle of nodes.  Bon Echo has been seen to do
        # this (see bug 351847).
        #
        if (len(nodes) > 100) or nodes.count(node):
            debug.println(debug.LEVEL_WARNING,
                          "util.getNodeLevel detected a cycle!!!")
            done = True
        elif node:
            nodes.append(node)
            debug.println(debug.LEVEL_FINEST,
                          "util.getNodeLevel %d" % len(nodes))
        else:
            done = True

    return len(nodes) - 1

def getAcceleratorAndShortcut(obj):
    """Gets the accelerator string (and possibly shortcut) for the given
    object.

    Arguments:
    - obj: the Accessible object

    A list containing the accelerator and shortcut for the given object,
    where the first element is the accelerator and the second element is
    the shortcut.
    """

    action = obj.action

    if not action:
        return ["", ""]

    # [[[TODO: WDW - assumes the first keybinding is all that we care about.
    # Logged as bugzilla bug 319741.]]]
    #
    bindingStrings = action.getKeyBinding(0).split(';')

    # [[[TODO: WDW - assumes menu items have three bindings.  Logged as
    # bugzilla bug 319741.]]]
    #
    if len(bindingStrings) == 3:
        #mnemonic       = bindingStrings[0]
        fullShortcut   = bindingStrings[1]
        accelerator    = bindingStrings[2]
    elif len(bindingStrings) > 0:
        fullShortcut   = bindingStrings[0]
        accelerator    = ""
    else:
        fullShortcut   = ""
        accelerator    = ""

    fullShortcut = fullShortcut.replace("<","")
    fullShortcut = fullShortcut.replace(">"," ")
    fullShortcut = fullShortcut.replace(":"," ")

    # If the accelerator string includes a Space, make sure we speak it.
    #
    if accelerator.endswith(" "):
        accelerator += "space"
    accelerator  = accelerator.replace("<","")
    accelerator  = accelerator.replace(">"," ")

    return [accelerator, fullShortcut]

def getKnownApplications():
    """Retrieves the list of currently running apps for the desktop
    as a list of Accessible objects.
    """

    debug.println(debug.LEVEL_FINEST,
                  "util.getKnownApplications...")

    apps = []
    registry = atspi.Registry()
    for i in range(0, registry.desktop.childCount):
        try:
            acc = registry.desktop.getChildAtIndex(i)
            app = atspi.Accessible.makeAccessible(acc)
            if app:
                apps.insert(0, app)
        except:
            debug.printException(debug.LEVEL_FINEST)

    debug.println(debug.LEVEL_FINEST,
                  "...util.getKnownApplications")

    return apps

def getObjects(root, onlyShowing=True):
    """Returns a list of all objects under the given root.  Objects
    are returned in no particular order - this function does a simple
    tree traversal, ignoring the children of objects which report the
    MANAGES_DESCENDANTS state.

    Arguments:
    - root:        the Accessible object to traverse
    - onlyShowing: examine only those objects that are SHOWING

    Returns: a list of all objects under the specified object
    """

    # The list of object we'll return
    #
    objlist = []

    # Start at the first child of the given object
    #
    if root.childCount <= 0:
        return objlist

    for i in range(0, root.childCount):
        debug.println(debug.LEVEL_FINEST,
                      "util.getObjects looking at child %d" % i)
        child = root.child(i)
        if child \
           and ((not onlyShowing) \
                or (onlyShowing \
                    and (child.state.count(atspi.Accessibility.STATE_SHOWING)))):
            objlist.append(child)
            if (child.state.count(atspi.Accessibility.STATE_MANAGES_DESCENDANTS) \
                == 0) \
                and (child.childCount > 0):
                objlist.extend(getObjects(child))

    return objlist

def findByRole(root, role, onlyShowing=True):
    """Returns a list of all objects of a specific role beneath the
    given root.  [[[TODO: MM - This is very inefficient - this should
    do it's own traversal and not add objects to the list that aren't
    of the specified role.  Instead it uses the traversal from
    getObjects and then deletes objects from the list that aren't of
    the specified role.  Logged as bugzilla bug 319740.]]]

    Arguments:
    - root the Accessible object to traverse
    - role the string describing the Accessible role of the object
    - onlyShowing: examine only those objects that are SHOWING

    Returns a list of descendants of the root that are of the given role.
    """

    objlist = []
    allobjs = getObjects(root, onlyShowing)
    for o in allobjs:
        if o.role == role:
            objlist.append(o)
    return objlist

def findUnrelatedLabels(root):
    """Returns a list containing all the unrelated (i.e., have no
    relations to anything and are not a fundamental element of a
    more atomic component like a combo box) labels under the given
    root.  Note that the labels must also be showing on the display.

    Arguments:
    - root the Accessible object to traverse

    Returns a list of unrelated labels under the given root.
    """

    # Find all the labels in the dialog
    #
    allLabels = findByRole(root, rolenames.ROLE_LABEL)

    # add the names of only those labels which are not associated with
    # other objects (i.e., empty relation sets).
    #
    # [[[WDW - HACK: In addition, do not grab free labels whose
    # parents are push buttons because push buttons can have labels as
    # children.]]]
    #
    # [[[WDW - HACK: panels with labelled borders will have a child
    # label that does not have its relation set.  So...we check to see
    # if the panel's name is the same as the label's name.  If so, we
    # ignore the label.]]]
    #
    unrelatedLabels = []

    for label in allLabels:
        relations = label.relations
        if len(relations) == 0:
            parent = label.parent
            if parent and (parent.role == rolenames.ROLE_PUSH_BUTTON):
                pass
            elif parent and (parent.role == rolenames.ROLE_PANEL) \
               and (parent.name == label.name):
                pass
            elif label.state.count(atspi.Accessibility.STATE_SHOWING):
                unrelatedLabels.append(label)

    # Now sort the labels based on their geographic position, top to
    # bottom, left to right.  This is a very inefficient sort, but the
    # assumption here is that there will not be a lot of labels to
    # worry about.
    #
    sortedLabels = []
    for label in unrelatedLabels:
        index = 0
        for sortedLabel in sortedLabels:
            if (label.extents.y > sortedLabel.extents.y) \
               or ((label.extents.y == sortedLabel.extents.y) \
                   and (label.extents.x > sortedLabel.extents.x)):
                index += 1
            else:
                break
        sortedLabels.insert(index, label)

    return sortedLabels

def phoneticSpellCurrentItem(string):
    """Phonetically spell the current flat review word or line.

    Arguments:
    - string: the string to phonetically spell.
    """

    for (index, character) in enumerate(string.decode("UTF-8")):
        if character.isupper():
            voice = settings.voices[settings.UPPERCASE_VOICE]
            character = character.lower()
        else:
            voice =  settings.voices[settings.DEFAULT_VOICE]
        string = phonnames.getPhoneticName(character)
        speech.speak(string, voice)

def printAncestry(child):
   """Prints a hierarchical view of a child's ancestry."""

   if not child:
       return

   ancestorList = [child]
   parent = child.parent
   while parent and (parent.parent != parent):
      ancestorList.insert(0, parent)
      parent = parent.parent

   indent = ""
   for ancestor in ancestorList:
      print ancestor.toString(indent + "+-", False)
      indent += "  "

def printHierarchy(root, ooi, indent="", onlyShowing=True, omitManaged=True):
    """Prints the accessible hierarchy of all children

    Arguments:
    -indent:      Indentation string
    -root:        Accessible where to start
    -ooi:         Accessible object of interest
    -onlyShowing: If True, only show children painted on the screen
    -omitManaged: If True, omit children that are managed descendants
    """

    if not root:
        return

    if root == ooi:
       print root.toString(indent + "(*)", False)
    else:
       print root.toString(indent + "+-", False)

    rootManagesDescendants = root.state.count(\
        atspi.Accessibility.STATE_MANAGES_DESCENDANTS)

    for i in range(0, root.childCount):
        child = root.child(i)
        if child == root:
            print indent + "  " + "WARNING CHILD == PARENT!!!"
        elif not child:
            print indent + "  " + "WARNING CHILD IS NONE!!!"
        elif child.parent != root:
            print indent + "  " + "WARNING CHILD.PARENT != PARENT!!!"
        else:
            paint = (not onlyShowing) \
                    or \
                    (onlyShowing \
                     and child.state.count(atspi.Accessibility.STATE_SHOWING))
            paint = paint \
                    and ((not omitManaged) \
                         or (omitManaged and not rootManagesDescendants))

            if paint:
               printHierarchy(child,
                              ooi,
                              indent + "  ",
                              onlyShowing,
                              omitManaged)

def printApps():
    """Prints a list of all applications to stdout."""

    level = debug.LEVEL_OFF

    apps = getKnownApplications()
    debug.println(level, "There are %d Accessible applications" % len(apps))
    for app in apps:
        debug.printDetails(level, "  App: ", app, False)
        for i in range(0, app.childCount):
            child = app.child(i)
            debug.printDetails(level, "    Window: ", child, False)
            if child.parent != app:
                debug.println(level,
                              "      WARNING: child's parent is not app!!!")

    return True

def printActiveApp():
    """Prints the active application."""

    level = debug.LEVEL_OFF

    window = findActiveWindow()
    if not window:
        debug.println(level, "Active application: None")
    else:
        app = window.app
        if not app:
            debug.println(level, "Active application: None")
        else:
            debug.println(level, "Active application: %s" % app.name)

def isInActiveApp(obj):
    """Returns True if the given object is from the same application that
    currently has keyboard focus.

    Arguments:
    - obj: an Accessible object
    """

    if not obj:
        return False
    else:
        return orca_state.locusOfFocus \
               and (orca_state.locusOfFocus.app == obj.app)

def findActiveWindow():
    """Traverses the list of known apps looking for one who has an
    immediate child (i.e., a window) whose state includes the active state.

    Returns the Python Accessible of the window that's active or None if
    no windows are active.
    """

    window = None
    apps = getKnownApplications()
    for app in apps:
        for i in range(0, app.childCount):
            try:
                state = app.child(i).state
                if state.count(atspi.Accessibility.STATE_ACTIVE) > 0:
                    window = app.child(i)
                    break
            except:
                debug.printException(debug.LEVEL_FINEST)

    return window

def saveOldAppSettings():
    """Save a copy of all the existing application specific settings
    (as specified by the settings.userCustomizableSettings dictionary)."""

    return orca_prefs.readPreferences()

def restoreOldAppSettings(prefsDict):
    """Restore a copy of all the previous saved application settings.

    Arguments:
    - prefsDict: the dictionary containing the old application settings.
    """

    for key in settings.userCustomizableSettings:
        if prefsDict.has_key(key):
            settings.__dict__[key] = prefsDict[key]

########################################################################
#                                                                      #
# METHODS FOR DRAWING RECTANGLES AROUND OBJECTS ON THE SCREEN          #
#                                                                      #
########################################################################

_display = None
_visibleRectangle = None

def drawOutline(x, y, width, height, erasePrevious=True):
    """Draws a rectangular outline around the accessible, erasing the
    last drawn rectangle in the process."""

    global _display
    global _visibleRectangle

    if not _display:
        try:
            _display = gtk.gdk.display_get_default()
        except:
            debug.printException(debug.LEVEL_FINEST)
            _display = gtk.gdk.display(":0")

        if not _display:
            debug.println(debug.LEVEL_SEVERE,
                          "util.drawOutline could not open display.")
            return

    screen = _display.get_default_screen()
    root_window = screen.get_root_window()
    graphics_context = root_window.new_gc()
    graphics_context.set_subwindow(gtk.gdk.INCLUDE_INFERIORS)
    graphics_context.set_function(gtk.gdk.INVERT)
    graphics_context.set_line_attributes(3,                  # width
                                         gtk.gdk.LINE_SOLID, # style
                                         gtk.gdk.CAP_BUTT,   # end style
                                         gtk.gdk.JOIN_MITER) # join style

    # Erase the old rectangle.
    #
    if _visibleRectangle and erasePrevious:
        drawOutline(_visibleRectangle[0], _visibleRectangle[1],
                    _visibleRectangle[2], _visibleRectangle[3], False)
        _visibleRectangle = None

    # We'll use an invalid x value to indicate nothing should be
    # drawn.
    #
    if x < 0:
        _visibleRectangle = None
        return

    # The +1 and -2 stuff here is an attempt to stay within the
    # bounding box of the object.
    #
    root_window.draw_rectangle(graphics_context,
                               False, # Fill
                               x + 1,
                               y + 1,
                               max(1, width - 2),
                               max(1, height - 2))

    _visibleRectangle = [x, y, width, height]

def outlineAccessible(accessible, erasePrevious=True):
    """Draws a rectangular outline around the accessible, erasing the
    last drawn rectangle in the process."""

    if accessible:
        component = accessible.component
        if component:
            visibleRectangle = component.getExtents(0) # coord type = screen
            drawOutline(visibleRectangle.x, visibleRectangle.y,
                        visibleRectangle.width, visibleRectangle.height,
                        erasePrevious)
    else:
        drawOutline(-1, 0, 0, 0, erasePrevious)

def isTextSelected(obj, startOffset, endOffset):
    """Returns an indication of whether the text is selected by
    comparing the text offset with the various selected regions of
    text for this accessible object.

    Arguments:
    - obj: the Accessible object.
    - startOffset: text start offset.
    - endOffset: text end offset.

    Returns an indication of whether the text is selected.
    """

    if not obj or not obj.text:
        return False

    text = obj.text
    for i in range(0, text.getNSelections()):
        [startSelOffset, endSelOffset] = text.getSelection(i)
        if (startOffset >= startSelOffset) \
           and (endOffset <= endSelOffset):
            return True

    return False

def speakTextSelectionState(obj, startOffset, endOffset):
    """Speak "selected" if the text was just selected, "unselected" if
    it was just unselected.

    Arguments:
    - obj: the Accessible object.
    - startOffset: text start offset.
    - endOffset: text end offset.
    """

    if not obj or not obj.text:
        return

    # Handle special cases.
    #
    # Shift-Page-Down:    speak "page selected from cursor position".
    # Shift-Page-Up:      speak "page selected to cursor position".
    #
    # Control-Shift-Down: speak "line selected down from cursor position".
    # Control-Shift-Up:   speak "line selected up from cursor position".
    #
    # Control-Shift-Home: speak "document selected to cursor position".
    # Control-Shift-End:  speak "document selected from cursor position".
    #
    if isinstance(orca_state.lastInputEvent, input_event.KeyboardEvent):
        eventStr = orca_state.lastInputEvent.event_string
        mods = orca_state.lastInputEvent.modifiers
    else:
        eventStr = None
        mods = 0

    isControlKey = mods & (1 << atspi.Accessibility.MODIFIER_CONTROL)
    isShiftKey = mods & (1 << atspi.Accessibility.MODIFIER_SHIFT)

    specialCaseFound = False
    if (eventStr == "Page_Down") and isShiftKey and not isControlKey:
        specialCaseFound = True
        line = _("page selected from cursor position")

    elif (eventStr == "Page_Up") and isShiftKey and not isControlKey:
        specialCaseFound = True
        line = _("page selected to cursor position")

    elif (eventStr == "Down") and isShiftKey and isControlKey:
        specialCaseFound = True
        line = _("line selected down from cursor position")

    elif (eventStr == "Up") and isShiftKey and isControlKey:
        specialCaseFound = True
        line = _("line selected up from cursor position")

    elif (eventStr == "Home") and isShiftKey and isControlKey:
        specialCaseFound = True
        line = _("document selected to cursor position")

    elif (eventStr == "End") and isShiftKey and isControlKey:
        specialCaseFound = True
        line = _("document selected from cursor position")

    if specialCaseFound:
        speech.speak(line, None, False)
        return

    try:
        # If we are selecting by word, then there possibly will be whitespace
        # characters on either end of the text. We adjust the startOffset and
        # endOffset to exclude them.
        #
        try:
            str = obj.text.getText(startOffset, endOffset).decode("UTF-8")
        except:
            str = u''
        n = len(str)

        # Don't strip whitespace if string length is one (might be a space).
        #
        if n > 1:
            while endOffset > startOffset:
                if isWordDelimiter(str[n-1]):
                    n -= 1
                    endOffset -= 1
                else:
                    break
            n = 0
            while startOffset < endOffset:
                if isWordDelimiter(str[n]):
                    n += 1
                    startOffset += 1
                else:
                    break
    except:
        debug.printException(debug.LEVEL_FINEST)

    if isTextSelected(obj, startOffset, endOffset):
        speech.speak(_("selected"), None, False)
    else:
        if obj.__dict__.has_key("lastSelections"):
            for i in range(0, len(obj.lastSelections)):
                startSelOffset = obj.lastSelections[0][0]
                endSelOffset = obj.lastSelections[0][1]
                if (startOffset >= startSelOffset) \
                    and (endOffset <= endSelOffset):
                    speech.speak(_("unselected"), None, False)
                    break

    # Save away the current text cursor position and list of text
    # selections for next time.
    #
    obj.lastCursorPosition = obj.text.caretOffset
    obj.lastSelections = []
    for i in range(0, obj.text.getNSelections()):
        obj.lastSelections.append(obj.text.getSelection(i))

# The following code has been borrowed from the following URL:
#
# http://www.dalkescientific.com/writings/diary/archive/2005/04/20/tracing_python_code.html
#
import linecache

def traceit(frame, event, arg):
    """Line tracing utility to output all lines as they are executed by
    the interpreter.  This is to be used by sys.settrace and is for
    debugging purposes.

    Arguments:
    - frame: is the current stack frame
    - event: 'call', 'line', 'return', 'exception', 'c_call', 'c_return',
             or 'c_exception'
    - arg:   depends on the event type (see docs for sys.settrace)
    """

    if event == "line":
        lineno = frame.f_lineno
        filename = frame.f_globals["__file__"]
        if (filename.endswith(".pyc") or
            filename.endswith(".pyo")):
            filename = filename[:-1]
        name = frame.f_globals["__name__"]
        if name == "gettext" \
           or name == "locale" \
           or name == "posixpath" \
           or name == "UserDict":
            return traceit
        line = linecache.getline(filename, lineno)
        debug.println(debug.LEVEL_ALL,
                      "TRACE %s:%s: %s" % (name, lineno, line.rstrip()))
    return traceit
