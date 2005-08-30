# Orca
#
# Copyright 2004-2005 Sun Microsystems Inc.
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

"""The Default Script for presenting information to the user using
both speech and Braille.

This module also provides a number of presenter functions that display
Accessible object information to the user based upon the object's role."""

import math

import a11y
import braille
import braillegenerator
import core
import debug
import flat_review
import keybindings
#import mag - [[[TODO: WDW - disable until I can figure out how to
#             resolve the GNOME reference in mag.py.]]]
import orca
import rolenames
import settings
import speech
import speechgenerator

from input_event import InputEventHandler
from orca_i18n import _                          # for gettext support
from script import Script


########################################################################
#                                                                      #
# The factory method for this module.  All Scripts are expected to     #
# have this method, and it is the sole way that instances of scripts   #
# should be created.                                                   #
#                                                                      #
########################################################################

def getScript(app):
    """Factory method to create a new Default script for the given
    application.  This method should be used for creating all
    instances of this script class.

    Arguments:
    - app: the application to create a script for
    """
    
    return Default(app)


########################################################################
#                                                                      #
# The Default script class.                                            #
#                                                                      #
########################################################################

class Default(Script):
    
    def __init__(self, app):
        """Creates a new script for the given application.  Callers
        should use the getScript factory method instead of calling
        this constructor directly.
        
        Arguments:
        - app: the application to create a script for.
        """
        
        Script.__init__(self, app)

        self.keybindings.add(
            keybindings.KeyBinding(
                "F9", \
                1 << orca.MODIFIER_ORCA, \
                1 << orca.MODIFIER_ORCA,
                InputEventHandler(\
                    sayAgain,
                    _("Repeats last utterance sent to speech."))))

        self.keybindings.add(
            keybindings.KeyBinding(
                "KP_Add", \
                0, \
                0, \
                InputEventHandler(\
                    sayAll,
                    _("Speaks entire document."))))

        self.keybindings.add(
            keybindings.KeyBinding(
                "KP_Enter", \
                0, \
                0, \
                InputEventHandler(\
                    self.whereAmI,
                    _("Performs the where am I operation."))))

        self.keybindings.add(
            keybindings.KeyBinding(
                "Num_Lock", \
                1 << orca.MODIFIER_ORCA, \
                1 << orca.MODIFIER_ORCA, \
                InputEventHandler(\
                    self.showZones,
                    _("Paints and prints the visible zones in the active window."))))

        self.listeners["focus:"]                                 = \
            self.onFocus
        
        #self.listeners["keyboard:modifiers"]                     = \
        #    self.noOp
        
        self.listeners["object:property-change:accessible-name"] = \
            self.onNameChanged 

        self.listeners["object:text-caret-moved"]                = \
            self.onCaretMoved
        self.listeners["object:text-changed:delete"]             = \
            self.onTextDeleted
        self.listeners["object:text-changed:insert"]             = \
            self.onTextInserted 
        self.listeners["object:text-selection-changed"]          = \
            self.noOp

        self.listeners["object:active-descendant-changed"]       = \
            self.onActiveDescendantChanged
        self.listeners["object:children-changed:"]               = \
            self.noOp
        self.listeners["object:link-selected"]                   = \
            self.onLinkSelected
        self.listeners["object:state-changed:"]                  = \
            self.onStateChanged
        self.listeners["object:selection-changed"]               = \
            self.onSelectionChanged
        self.listeners["object:property-change:accessible-value"] = \
            self.onValueChanged
        self.listeners["object:property-change"] = \
            self.noOp

        self.listeners["object:value-changed:"]                  = \
            self.onValueChanged
        self.listeners["object:visible-changed"]                 = \
            self.noOp

        self.listeners["window:activate"]                        = \
            self.onWindowActivated
        self.listeners["window:create"]                          = \
            self.noOp
        self.listeners["window:deactivated"]                     = \
            self.noOp
        self.listeners["window:destroy"]                         = \
            self.noOp
        self.listeners["window:maximize"]                        = \
            self.noOp
        self.listeners["window:minimize"]                        = \
            self.noOp
        self.listeners["window:rename"]                          = \
            self.noOp
        self.listeners["window:restore"]                         = \
            self.noOp
        self.listeners["window:switch"]                          = \
            self.noOp
        self.listeners["window:titlelize"]                       = \
            self.noOp

        self.brailleGenerator = self.getBrailleGenerator()
        self.speechGenerator = self.getSpeechGenerator()


    def processObjectEvent(self, event):
        """Processes all object events of interest to this script.  Note
        that this script may be passed events it doesn't care about, so
        it needs to react accordingly.

        Arguments:
        - event: the Event
        """

        # [[[TODO: WDW - HACK to set Orca's locusOfFocus if we've somehow
        # gotten out of whack.  This typically happens when going into an
        # application and we only get a window activated event for it, even
        # if one of its children has focus.  Since we're doing this, we'll
        # tell Orca to not propagate this event to us.]]]
        #
        # [[[TODO: WDW - additional info - this really isn't necessary because
        # we typically only run into this problem when Orca is started after
        # the desktop applications are running.  In real life, this will
        # most likely not be the case, and a simple "make the world right"
        # user action can be to just Alt+Tab to force the apps to give us
        # the events we care about.]]]
        #
        #if (event.type.find("focus") == -1) \
        #   and (event.type.find("state-changed:selected") == -1) \
        #   and (event.type.find("object:selection-changed") == -1) \
        #   and (event.type.find("active-descendant") == -1) \
        #   and event.source.state.count(core.Accessibility.STATE_FOCUSED):
        #    orca.setLocusOfFocus(event, event.source, False)

        Script.processObjectEvent(self, event)

        
    def getBrailleGenerator(self):
        """Returns the braille generator for this script.
        """

        return braillegenerator.BrailleGenerator()

    
    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """

        return speechgenerator.SpeechGenerator()


    def whereAmI(self, inputEvent):
        self.updateBraille(orca.locusOfFocus)

        verbosity = settings.getSetting("speechVerbosityLevel",
                                        settings.VERBOSITY_LEVEL_VERBOSE)
    
        utterances = []
            
        utterances.extend(
            self.speechGenerator.getSpeechContext(orca.locusOfFocus))

        # Now, we'll treat table row and column headers as context
        # as well.  This requires special handling because we're
        # making headers seem hierarchical in the context, but they
        # are not hierarchical in the containment hierarchicy.
        # We also only want to speak the one that changed.  If both
        # changed, first speak the row header, then the column header.
        #
        # We also keep track of tree level depth and only announce
        # that if it changes.
        #
        if orca.locusOfFocus.role == rolenames.ROLE_TABLE_CELL:
            parent = orca.locusOfFocus.parent
            if parent and parent.table:
                table = parent.table
                row = table.getRowAtIndex(orca.locusOfFocus.index)
                col = table.getColumnAtIndex(orca.locusOfFocus.index)

                desc = parent.table.getRowDescription(row)
                if desc and len(desc):
                    text = desc
                    if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
                        text += " " \
                                + rolenames.rolenames[\
                                        rolenames.ROLE_ROW_HEADER].speech
                        utterances.append(text)

                desc = newParent.table.getColumnDescription(newCol)
                if desc and len(desc):
                    text = desc
                    if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
                        text += " " \
                                + rolenames.rolenames[\
                                        rolenames.ROLE_COLUMN_HEADER].speech
                        utterances.append(text)

        # Get the text for the object itself.
        #
        utterances.extend(
            self.speechGenerator.getSpeech(orca.locusOfFocus, False))

        # Now speak the tree node level.
        #
        level = a11y.getNodeLevel(orca.locusOfFocus)
        if level >= 0:
            utterances.append(_("tree level %d") % (level + 1))

        if orca.locusOfFocus.state.count(\
                    core.Accessibility.STATE_SENSITIVE) == 0:
            message = _("Nothing has focus")
            utterances.extend(message)
            
        speech.sayUtterances("default", utterances)

        return True


    def findCommonAncestor(self, a, b):
        """Finds the common ancestor between Accessible a and Accessible b.

        Arguments:
        - a: Accessible
        - b: Accessible
        """

        if (a is None) or (b is None):
            return None

        if a == b:
            return a
        
        aParents = [a]
        try:
            parent = a.parent
            while parent and (parent.parent != parent):
                aParents.append(parent)
                parent = parent.parent
            aParents.reverse()
        except:
            pass
        
        bParents = [b]
        try:
            parent = b.parent
            while parent and (parent.parent != parent):
                bParents.append(parent)
                parent = parent.parent
            bParents.reverse()
        except:
            pass
        
        commonAncestor = None
        
        maxSearch = min(len(aParents), len(bParents))
        i = 0
        while i < maxSearch:
            if aParents[i] == bParents[i]:
                commonAncestor = aParents[i]
                i += 1
            else:
                break

        return commonAncestor


    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """
        
        # [[[TODO: WDW - HACK because parents that manage their descendants
        # can give us a different object each time we ask for the same
        # exact child.  So...we do a check here to see if the old object
        # and new object have the same index in the parent and if they
        # have the same name.  If so, then they are likely to be the same
        # object.  The reason we check for the name here is a small sanity
        # check.  This whole algorithm could fail because one might be
        # deleting/adding identical elements from/to a list or table, thus
        # the objects really could be different even though they seem the
        # same.]]]
        #
        if oldLocusOfFocus:
            oldParent = oldLocusOfFocus.parent
        else:
            oldParent = None
            
        if newLocusOfFocus:
            newParent = newLocusOfFocus.parent
        else:
            newParent = None

        if newParent and (oldParent == newParent):
            state = newParent.state
            if state.count(core.Accessibility.STATE_MANAGES_DESCENDANTS) \
                and (oldLocusOfFocus.index == newLocusOfFocus.index) \
                and (oldLocusOfFocus.name == newLocusOfFocus.name):
                    return

        # Well...now that we got that behind us, let's do what we're supposed
        # to do.
        #
        if newLocusOfFocus:
            self.updateBraille(newLocusOfFocus)

            verbosity = settings.getSetting("speechVerbosityLevel",
                                            settings.VERBOSITY_LEVEL_VERBOSE)
    
            utterances = []
            
            # Now figure out how of the container context changed and
            # speech just what is different.
            #
            commonAncestor = self.findCommonAncestor(oldLocusOfFocus,
                                                     newLocusOfFocus)
            if commonAncestor:
                utterances.extend(
                    self.speechGenerator.getSpeechContext(newLocusOfFocus,
                                                          commonAncestor))

            # Now, we'll treat table row and column headers as context
            # as well.  This requires special handling because we're
            # making headers seem hierarchical in the context, but they
            # are not hierarchical in the containment hierarchicy.
            # We also only want to speak the one that changed.  If both
            # changed, first speak the row header, then the column header.
            #
            # We also keep track of tree level depth and only announce
            # that if it changes.
            #
            oldNodeLevel = -1
            newNodeLevel = -1
            if newLocusOfFocus.role == rolenames.ROLE_TABLE_CELL:
                if oldParent and oldParent.table:
                    table = oldParent.table
                    oldRow = table.getRowAtIndex(oldLocusOfFocus.index)
                    oldCol = table.getColumnAtIndex(oldLocusOfFocus.index)
                else:
                    oldRow = -1
                    oldCol = -1

                if newParent and newParent.table:
                    table = newParent.table
                    newRow = table.getRowAtIndex(newLocusOfFocus.index)
                    newCol = table.getColumnAtIndex(newLocusOfFocus.index)

                    if newRow != oldRow:
                        desc = newParent.table.getRowDescription(newRow)
                        if desc and len(desc):
                            text = desc
                            if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
                                text += " " \
                                        + rolenames.rolenames[\
                                        rolenames.ROLE_ROW_HEADER].speech
                            utterances.append(text)
                    if newCol != oldCol:
                        desc = newParent.table.getColumnDescription(newCol)
                        if desc and len(desc):
                            text = desc
                            if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
                                text += " " \
                                        + rolenames.rolenames[\
                                        rolenames.ROLE_COLUMN_HEADER].speech
                            utterances.append(text)

                oldNodeLevel = a11y.getNodeLevel(oldLocusOfFocus)
                newNodeLevel = a11y.getNodeLevel(newLocusOfFocus)

            # Get the text for the object itself.
            #
            utterances.extend(
                self.speechGenerator.getSpeech(newLocusOfFocus, False))

            # Now speak the new tree node level if it has changed.
            #
            if (oldNodeLevel != newNodeLevel) \
               and (newNodeLevel >= 0):
                utterances.append(_("tree level %d") % (newNodeLevel + 1))

            speech.sayUtterances("default", utterances)
        else:
            message = _("Nothing has focus")
            braille.displayMessage(message)
            speech.say("default", message)


    def visualAppearanceChanged(self, event, obj):
        """Called when the visual appearance of an object changes.  This
        method should not be called for objects whose visual appearance
        changes solely because of focus -- setLocusOfFocus is used for that.
        Instead, it is intended mostly for objects whose notional 'value' has
        changed, such as a checkbox changing state, a progress bar advancing,
        a slider moving, text inserted, caret moved, etc.

        Arguments:
        - event: if not None, the Event that caused this to happen
        - obj: the Accessible whose visual appearance changed.
        """

        # We care if panels are suddenly showing.  The reason for this
        # is that some applications, such as Evolution, will bring up
        # a wizard dialog that uses "Forward" and "Backward" buttons
        # that change the contents of the dialog.  We only discover
        # this through showing events. [[[TODO: WDW - perhaps what we
        # really want is to speak unbound labels that are suddenly
        # showing?  event.detail == 1 means object is showing.]]]
        #
        if (obj.role == rolenames.ROLE_PANEL) \
               and (event.detail1 == 1) \
               and orca.isInActiveApp(obj):

            # It's only showing if its parent is showing. [[[TODO: WDW -
            # HACK we stop at the application level because applications
            # never seem to have their showing state set.]]]
            #
            reallyShowing = True
            parent = obj.parent
            while reallyShowing \
                      and parent \
                      and (parent != parent.parent) \
                      and (parent.role != rolenames.ROLE_APPLICATION):
                reallyShowing = parent.state.count(\
                    core.Accessibility.STATE_SHOWING)
                parent = parent.parent

            # Find all the unrelated labels in the dialog and speak them.
            #
            if reallyShowing:
                utterances = []
                labels = a11y.findUnrelatedLabels(obj)
                for label in labels:
                    utterances.append(label.name)

                # [[[TODO: WDW - HACK to account for the way applications
                # such as Evolution handle their wizards.  They will set
                # the "Forward" and "Back" buttons insensitive as appropriate,
                # which has the side effect of nothing having focus.  So,
                # we let users know this via speech and braille.  For now,
                # this awful hack is isolated to when a panel starts showing
                # in the active application, which is the situation where
                # these types of poor application behavior has been found
                # to exist.]]]
                #
                if orca.locusOfFocus \
                   and (orca.locusOfFocus.state.count(\
                    core.Accessibility.STATE_SENSITIVE) == 0):
                    message = _("Nothing has focus")
                    utterances.append(message)
                    self.updateBraille(orca.locusOfFocus.parent,
                                       braille.Region(" " + message))
                    
                speech.sayUtterances("default", utterances)
                    
                return

        if obj != orca.locusOfFocus:
            return

        self.updateBraille(obj)
        speech.sayUtterances(
            "default",
            self.speechGenerator.getSpeech(event.source, True))

            
    def getVisualParent(self, obj):
        """Returns the logical visual container for the given object or None
        if no such object exists.  The logical visual container differs from
        the component hierarchy in that it eliminates non-visual layout
        elements (e.g., panels without names or borders) from the hierarchy.
        """

        visualParent = None
        while obj.parent:
            if len(obj.parent.label) > 0:
                visualParent = obj.parent
            obj = obj.parent

        return visualParent
    
        
    def updateBraille(self, obj, extraRegion=None):
        """Updates the braille display to show the give object.

        Arguments:
        - obj: the Accessible
        - extra: extra Region to add to the end
        """

        braille.clear()

        line = braille.Line()
        
        line.addRegions(self.brailleGenerator.getBrailleContext(obj))
        
        result = self.brailleGenerator.getBrailleRegions(obj)
        line.addRegions(result[0])

        if extraRegion:
            line.addRegion(extraRegion)
            
        braille.addLine(line)

        if extraRegion:
            braille.setFocus(extraRegion)
        else:
            braille.setFocus(result[1])

        braille.refresh(True)    
    
        
    ########################################################################
    #                                                                      #
    # AT-SPI OBJECT EVENT HANDLERS                                         #
    #                                                                      #
    ########################################################################

    def onFocus(self, event):
        """Called whenever an object gets focus.
        
        Arguments:
        - event: the Event
        """

        # [[[TODO: WDW - HACK to deal with quirky GTK+ menu behavior.
        # The problem is that when moving to submenus in a menu, the
        # menu gets focus first and then the submenu gets focus all
        # with a single keystroke.  So...focus in menus really means
        # that the object has focus *and* it is selected.  Now, this
        # assumes the selected state will be set before focus is given,
        # which appears to be the case from empirical analysis of the
        # event stream.  But of course, all menu items and menus in
        # the complete menu path will have their selected state set,
        # so, we really only care about the leaf menu or menu item
        # that it selected.]]]
        #
        role = event.source.role
        if (role == rolenames.ROLE_MENU) \
           or (role == rolenames.ROLE_MENU_ITEM) \
           or (role == rolenames.ROLE_CHECK_MENU_ITEM) \
           or (role == rolenames.ROLE_RADIO_MENU_ITEM):
            selection = event.source.selection
            if selection and selection.nSelectedChildren > 0:
                return

        # [[[TODO: WDW - HACK to deal with the fact that active cells
        # may or may not get focus.  Their parents, however, do tend to
        # get focus, but when the parent gets focus, it really means
        # that the selected child in it has focus.  Of course, this all
        # breaks when more than one child is selected.  Then, we really
        # need to depend upon the model where focus really works.]]]
        #
        newFocus = event.source
        
        if (event.source.role == rolenames.ROLE_LAYERED_PANE) \
            or (event.source.role == rolenames.ROLE_TABLE) \
            or (event.source.role == rolenames.ROLE_TREE_TABLE) \
            or (event.source.role == rolenames.ROLE_TREE):
            if event.source.childCount:
                selection = event.source.selection
                if selection and selection.nSelectedChildren > 0:
                    child = selection.getSelectedChild(0)
                    if child:
                        newFocus = a11y.makeAccessible(child)
                        
        orca.setLocusOfFocus(event, newFocus)
        

    def onNameChanged(self, event):
        """Called whenever a property on an object changes.

        Arguments:
        - event: the Event
        """
        
        # [[[TODO: WDW - HACK because gnome-terminal issues a name changed
        # event for the edit preferences dialog even though the name really
        # didn't change.  I'm guessing this is going to be a vagary in all
        # of GTK+.]]]
        #
        if event.source and (event.source.role == rolenames.ROLE_DIALOG) \
           and (event.source == orca.locusOfFocus):
            return
        
        orca.visualAppearanceChanged(event, event.source)


    def onCaretMoved(self, event):
        """Called whenever the caret moves.

        Arguments:
        - event: the Event
        """

        # Ignore text deletions from non-focused objects, unless the
        # currently focused object is the parent of the object from which
        # text was deleted
        #
        if (event.source != orca.locusOfFocus) \
               and (event.source.parent != orca.locusOfFocus):
            return

        # Magnify the object.  [[[TODO: WDW - this is a hack for now.]]]
        #
        #mag.magnifyAccessible(event.source)

        # Update the Braille display - if we can just reposition
        # the cursor, then go for it.
        #
        brailleNeedsRepainting = True
        line = braille.getShowingLine()
        for region in line.regions:
            if isinstance(region, braille.Text) \
               and (region.accessible == event.source):
                if region.repositionCursor():
                    braille.refresh(True)
                    brailleNeedsRepainting = False
                break

        if brailleNeedsRepainting:
            self.updateBraille(event.source)

        if orca.lastKeyboardEvent is None:
            return

        # Guess why the caret moved and say something appropriate.
        # [[[TODO: WDW - this motion assumes traditional GUI
        # navigation gestures.  In an editor such as vi, line up and
        # down is done via other actions such as "i" or "j".  We may
        # need to think about this a little harder.]]]
        #
        string = orca.lastKeyboardEvent.event_string
        mods = orca.lastKeyboardEvent.modifiers
        controlMask = 1 << core.Accessibility.MODIFIER_CONTROL

        if (string == "Up") or (string == "Down"):
            sayLine(event.source)
        elif (string == "Left") or (string == "Right"):
            if (mods & controlMask):
                sayWord(event.source)
            else:
                sayCharacter(event.source)
        elif string == "Page_Up":
            if (mods & controlMask):
                sayCharacter(event.source)
            else:
                sayLine(event.source)
        elif string == "Page_Down":
            sayLine(event.source)
        elif (string == "Home") or (string == "End"):
            if (mods & controlMask):
                sayLine(event.source)
            else:
                sayCharacter(event.source)


    def onTextDeleted(self, event):
        """Called whenever text is deleted from an object.

        Arguments:
        - event: the Event
        """
    
        # Ignore text deletions from non-focused objects, unless the
        # currently focused object is the parent of the object from which
        # text was deleted
        #
        if (event.source != orca.locusOfFocus) \
               and (event.source.parent != orca.locusOfFocus):
            return

        text = event.source.text
        #print "onTextDeleted, LENGTH=%d, text='%s'" % (text.characterCount, \
        #                                               event.any_data)

        self.updateBraille(event.source)

        # The any_data member of the event object has the deleted text in
        # it - If the last key pressed was a backspace or delete key,
        # speak the deleted text.  [[[TODO: WDW - again, need to think
        # about the ramifications of this when it comes to editors such
        # as vi or emacs.
        #
        if orca.lastKeyboardEvent is None:
            return
        
        string = orca.lastKeyboardEvent.event_string
        text = event.any_data
        if (string == "BackSpace") or (string == "Delete"):
            if text.isupper():
                speech.say("uppercase", text)
            else:
                speech.say("default", text)


    def onTextInserted(self, event):
        """Called whenever text is inserted into an object.

        Arguments:
        - event: the Event
        """

        # Ignore text deletions from non-focused objects, unless the
        # currently focused object is the parent of the object from which
        # text was deleted
        #
        if (event.source != orca.locusOfFocus) \
               and (event.source.parent != orca.locusOfFocus):
            return

        text = event.source.text
        #print "onTextInserted, LENGTH=%d, text='%s'" % (text.characterCount, \
        #                                                event.any_data)
        
        self.updateBraille(event.source)
        text = event.any_data
        if text.isupper():
            speech.say("uppercase", text)
        else:
            speech.say("default", text)


    def onActiveDescendantChanged(self, event):
        """Called when an object who manages its own descendants detects a
        change in one of its children.
        
        Arguments:
        - event: the Event
        """

        try:
            child = a11y.makeAccessible(event.any_data)

            if child.childCount:
                orca.setLocusOfFocus(event, child.child(1))
            else:
                orca.setLocusOfFocus(event, child)
        except:
            debug.printException(debug.LEVEL_SEVERE)
            

    def onLinkSelected(self, event):
        """Called when a hyperlink is selected in a text area.
        
        Arguments:
        - event: the Event
        """

        try:
            
            # [[[TODO: WDW - HACK one might think we could expect an
            # application to keep its name, but it appears as though
            # yelp has an identity problem and likes to start calling
            # itself "yelp," but then changes its name to "Mozilla"
            # on Fedora Core 4 after the user selects a link.  So, we'll
            # just assume that link-selected events always come from the
            # application with focus.]]]
            #
            #if orca.locusOfFocus \
            #   and (orca.locusOfFocus.app == event.source.app):
            #    orca.setLocusOfFocus(event, event.source)
            orca.setLocusOfFocus(event, event.source)
        except:
            debug.printException(debug.LEVEL_SEVERE)
            

    def onStateChanged(self, event):
        """Called whenever an object's state changes.  Currently, the
        state changes for non-focused objects are ignored.

        Arguments:
        - event: the Event
        """
    
        global state_change_notifiers

        # Do we care?
        #
        if state_change_notifiers.has_key(event.source.role):
            notifiers = state_change_notifiers[event.source.role]
            found = False
            for state in notifiers:
                if state and event.type.endswith(state):
                    found = True
                    break
            if found:
                orca.visualAppearanceChanged(event, event.source)

        # [[[TODO: WDW - HACK we'll handle this in the visual appearance
        # changed handler.]]]
        #
        # The object with focus might become insensitive, so we need to
        # flag that.  This typically occurs in wizard dialogs such as
        # the account setup assistant in Evolution.
        #
        #if event.type.endswith("sensitive") \
        #   and (event.detail1 == 0) \
        #   and event.source == orca.locusOfFocus:
        #    print "FOO INSENSITIVE"
        #    #orca.setLocusOfFocus(event, None)
           
        
    def onSelectionChanged(self, event):
        """Called when an object's selection changes.

        Arguments:
        - event: the Event
        """

        try:
            # [[[TODO: WDW - HACK layered panes are nutty in that they
            # will change the selection and tell the selected child it is
            # focused, but the child will not issue a focus changed event.]]]
            # 
            if event.source \
               and (event.source.role == rolenames.ROLE_LAYERED_PANE):
#                    or (event.source.role == rolenames.ROLE_TABLE) \
#                    or (event.source.role == rolenames.ROLE_TREE_TABLE) \
#                    or (event.source.role == rolenames.ROLE_TREE)):
                if event.source.childCount:
                    selection = event.source.selection
                    if selection and selection.nSelectedChildren > 0:
                        child = selection.getSelectedChild(0)
                        if child:
                            orca.setLocusOfFocus(event,
                                                 a11y.makeAccessible(child))
        except:
            debug.printException(debug.LEVEL_SEVERE)

        return


    def onValueChanged(self, event):
        """Called whenever an object's value changes.  Currently, the
        value changes for non-focused objects are ignored.

        Arguments:
        - event: the Event
        """
    
        orca.visualAppearanceChanged(event, event.source)
            

    def onWindowActivated(self, event):
        """Called whenever a toplevel window is activated.
        
        Arguments:
        - event: the Event
        """

        orca.setLocusOfFocus(event, event.source)
            

    def noOp(self, event):
        """Just here to capture events.

        Arguments:
        - event: the Event
        """
        pass


    ########################################################################
    #                                                                      #
    # Flat review mode support.  [[[TODO: WDW - still under development,   #
    # but the idea is that a script should be able to provide custom       #
    # information about layout as well.]]]                                 #
    #                                                                      #
    ########################################################################

    def getShowingZones(self):
        """Returns a list of all interesting, non-intersecting,
        regions that are drawn in the currently active window.  Each
        element of the list is the Accessible object associated with a
        given region.  The term 'zone' here is inherited from OCR
        algorithms and techniques.
    
        The objects are returned in no particular order.

        Arguments:
        - root: the Accessible object to traverse

        Returns: a list of all objects under the specified object
        """
        if (not orca.locusOfFocus) or (orca.locusOfFocus.app != self.app):
            return []

        obj = orca.locusOfFocus
        while obj \
                  and obj.parent \
                  and (obj.parent.role != rolenames.ROLE_APPLICATION) \
                  and (obj != obj.parent):
            obj = obj.parent

        if obj \
               and obj.parent \
               and (obj.parent.role == rolenames.ROLE_APPLICATION):
            return flat_review.getShowingZones(obj)
        else:
            return []


    def clusterZonesByLine(self, zones):
        """Given a list of interesting accessible objects (the zones),
        returns a list of lines in order from the top to bottom, where
        each line is a list of accessible objects in order from left
        to right.  """

        return flat_review.clusterZonesByLine(zones)

    
    def showZones(self, inputEvent):
        """Debug routine to paint rectangles around the discrete
        interesting (e.g., text)  zones in the active window for
        this application.
        """
        
        lines = self.clusterZonesByLine(self.getShowingZones())
        print "Number of lines:", len(lines)
        for line in lines:
            string = ""
            for zone in line:
                string += " '%s' [%s]" % (zone.string, zone.accessible.role)
                orca.drawOutline(zone.x, zone.y, zone.width, zone.height)
            debug.println(debug.LEVEL_OFF, string)
            
        
########################################################################
#                                                                      #
# ACCESSIBLE TEXT OUTPUT FUNCTIONS                                     #
#                                                                      #
# Functions for handling output of AccessibleText objects to speech.   #
#                                                                      #
########################################################################

def sayLine(obj):
    """Speaks the line of an AccessibleText object that contains the
    caret. [[[TODO: WDW - what if the line is empty?]]]

    Arguments:
    - obj: an Accessible object that implements the AccessibleText
           interface
    """
    
    # Get the AccessibleText interface of the provided object
    #
    result = a11y.getTextLineAtCaret(obj)
    speech.say("default", result[0])
    

def sayWord(obj):
    """Speaks the word at the caret.  [[[TODO: WDW - what if there is no
    word at the caret?]]]

    Arguments:
    - obj: an Accessible object that implements the AccessibleText
           interface
    """
    
    text = obj.text
    offset = text.caretOffset
    word = text.getTextAtOffset(offset,
                                core.Accessibility.TEXT_BOUNDARY_WORD_START)
    speech.say("default", word[0])
    

def sayCharacter(obj):
    """Speak the character under the caret.  [[[TODO: WDW - isn't the
    caret between characters?]]]

    Arguments:
    - obj: an Accessible object that implements the AccessibleText
           interface
    """
    
    text = obj.text
    offset = text.caretOffset
    character = text.getText(offset, offset+1)
    if character.isupper():
        speech.say("uppercase", character)
    else:
        speech.say("default", character)


########################################################################
#                                                                      #
# SAYALL SUPPORT                                                       #    
#                                                                      #
# The following functions related to the sayAll system.  This system   #
# is designed to be pluggable such that sayAll commands could be       #
# implemented for various types of objects.  The current               #
# implementation only works for reading the text of single text        #
# objects.  This implementation will need to be extended to support    #
# reading of more complex documents such as web pages in Yelp/Mozilla, #
# and documents within StarOffice.                                     #
#                                                                      #
# [[[TODO: WDW - need to think about updating magnifier roi.]]]        #
#                                                                      #
########################################################################

def sayAgain(inputEvent):
    """Tells speech to repeat what was last spoken.
        
    Arguments:
    - inputEvent: the InputEvent instance that caused this to be called.

    Returns True indicating the event should be consumed.
    """
    
    speech.sayAgain()
    
    return True
    
    
def sayAll(inputEvent):
    """Initiates sayAll mode and attempts to say all the text of the
    currently focused Accessible text object.  [[[TODO: WDW - the entire
    sayAll mechanism is likely to be severely broken.]]]
    
    Arguments:
    - inputEvent: the InputEvent instance that caused this to be called.

    Returns True indicating the event should be consumed.
    """
    
    global sayAllText
    global sayAllPosition

    # If the focused object isn't text, we don't know how to read it
    #
    txt = None
    try:
        txt = orca.locusOfFocus.text
    except:
        pass
    
    if txt is None:
        speech.say("default", _("Not a document."))
        return True
    
    sayAllText = txt
    sayAllPosition = txt.caretOffset

    # Initialize sayAll mode with the speech subsystem - providing the
    # sayAllGetChunk and sayAllStopped callbacks.  Once we call sayLine,
    # the sayAll mode will begin executing when it receives the associated
    # speech callback.
    #
    speech.startSayAll("default", sayAllGetChunk, sayAllStopped)
    sayLine(orca.locusOfFocus)

    return True


# sayAllText contains the AccessibleText object of the document
# currently being read
#
sayAllText = None

# sayAllPosition is the current position within sayAllText
#
sayAllPosition = 0

def sayAllGetChunk():
    """Speaks the next chunk of text.

    Returns True if there is still more text to be spoken.
    """
    
    global sayAllText
    global sayAllPosition

    # Get the next line of text to read
    #
    line = sayAllText.getTextAfterOffset(
        sayAllPosition,
        core.Accessibility.TEXT_BOUNDARY_LINE_START)

    # If the line is empty (which only happens at the end of the
    # document [[[TODO: WDW - is this true?]]]), quit.  Note that
    # blank lines are returned as lines of length 1 character which is
    # the newline character
    #
    if line[1] == line[2]:
        return False

    # Speak the line
    #
    speech.say("default", line[0])

    # Set the say all position to the beginning of the line being read
    #
    sayAllPosition = line[1]

    # Return true to continue reading

    return True


def sayAllStopped(position):
    """Called when sayAll mode is interrupted.

    Arguments:
    - position: the position within the current chunk where speech
                was interrupted.
    """
    
    global sayAllText
    global sayAllPosition

    sayAllText.setCaretOffset(sayAllPosition + position)


# Dictionary that defines the state changes we care about for various
# objects.  The key represents the role and the value represents a list
# of states that we care about.
#
state_change_notifiers = {}

state_change_notifiers[rolenames.ROLE_CHECK_BOX]     = ("checked",
                                                        None)
state_change_notifiers[rolenames.ROLE_PANEL]         = ("showing",
                                                        None)
state_change_notifiers[rolenames.ROLE_LABEL]         = ("showing",
                                                        None)
state_change_notifiers[rolenames.ROLE_TOGGLE_BUTTON] = ("checked",
                                                        None)
state_change_notifiers[rolenames.ROLE_TABLE_CELL]    = ("checked",
                                                        "expanded",
                                                        None)

