# Orca
#
# Copyright 2011 Consorcio Fernando de los Rios.
# Author: J. Ignacio Alvarez <jialvarez@emergya.es>
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

"""Plugin that implements Orca magnifier"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2011 Consorcio Fernando de los Rios."
__license__   = "LGPL"

from orca.pluglib.interfaces import IPluginManager, IPlugin, ICommand, \
    IPresenter, IConfigurable, IDependenciesChecker, PluginManagerError

from orca.orca_i18n import _         # for gettext support
from orca.orca_i18n import ngettext  # for ngettext support
from orca.orca_i18n import C_        # to provide qualified translatable strings

import orca.input_event
import orca.keybindings

try:
    # This can fail due to gtk not being available.  We want to
    # be able to recover from that if possible.  The main driver
    # for this is to allow "orca --text-setup" to work even if
    # the desktop is not running.
    #
    import gtk
except:
    pass

import time

try:
    global bonobo
    global ORBit

    import bonobo as bonobo
    import ORBit as ORBit
    ORBit.load_typelib('GNOME_Magnifier')
    import GNOME.Magnifier
except ImportError, v:
    print "Exception importing GNOME Magnifier: " + str(v)
    GNOME.Magnifier = None
    pass

class magPlugin(IPlugin, IPresenter, ICommand):
    name = 'Orca magnifier'
    description = 'Magnify the screen' 
    version = '0.9'
    authors = ['J. Ignacio Alvarez <jialvarez@emergya.es>']
    website = 'http://www.emergya.es'
    icon = 'gtk-missing-image'

    def __init__(self):
        pass

    def enable(self):

        global pyatspi
        global debug
        global eventsynthesizer
        global settings
        global orca
        global orca_state
        global _
        
        import pyatspi
        import orca.debug as debug
        import orca.eventsynthesizer as eventsynthesizer
        import orca.settings as settings
        import orca.orca as orca
        import orca.orca_state as orca_state
        
        from orca.orca_i18n import _  # for gettext support
        
        self._magnifierAvailable = False
        global _settingsManager
        _settingsManager = getattr(orca, '_settingsManager')

        if GNOME.Magnifier:
            self._magnifierAvailable = True
        
        # If True, this module has been initialized.
        #
        self._initialized = False
        
        # The Magnifier and its property bag
        #
        self._magnifier = None
        self._magnifierPBag = None
        
        # The width and height, in unzoomed system coordinates of the rectangle that,
        # when magnified, will fill the viewport of the magnifier - this needs to be
        # sync'd with the magnification factors of the zoom area.
        #
        self._roiWidth = 0
        self._roiHeight = 0
        
        # Minimum/maximum values for the center of the ROI
        # in source screen coordinates.
        #
        self._minROIX = 0
        self._maxROIX = 0
        self._minROIY = 0
        self._maxROIY = 0
        
        # The current region of interest.
        #
        # A GNOME.Magnifier.RectBounds object which consists of x1, y1, x2, y2 values
        # that are in source screen coordinates.
        #
        self._roi = None
        
        # The area of the source display that is not covered by the magnifier.
        #
        # A GNOME.Magnifier.RectBounds object which consists of x1, y1, x2, y2 values
        # that are in source screen coordinates.  If the COMPOSITE support is enabled
        # in gnome-mag, then this typically becomes the entire source screen.  If it
        # it not enabled, however, and the target and source displays are the same,
        # this ends up becoming the portion of the screen that is not covered by the
        # magnifier.
        #
        self._sourceDisplayBounds = None
        
        # The area on the target display where we are placing the magnifier.
        #
        # A GNOME.Magnifier.RectBounds object which consists of x1, y1, x2, y2 values
        # that are in target screen coordinates.
        #
        self._targetDisplayBounds = None
        
        # The ZoomRegion we care about and its property bag.  We only use one
        # ZoomRegion and we make it occupy the whole magnifier.
        #
        self._zoomer = None
        self._zoomerPBag = None
        
        # The time of the last mouse event.
        #
        self._lastMouseEventTime = time.time()
        
        # Whether or not the last mouse event was the result of our routing the
        # pointer.
        #
        self._lastMouseEventWasRoute = False
        
        # If True, we're using gnome-mag >= 0.13.1 that allows us to control
        # where to draw the cursor and crosswires.
        #
        self._pollMouseDisabled = False
        
        # Whether or not composite is being used.
        #
        self._fullScreenCapable = True
        
        # Whether or not we're in the process of making "live update" changes
        # to the location of the magnifier.
        #
        self._liveUpdatingMagnifier = False
        
        # The original source display bounds.
        #
        self._originalSourceDisplayBounds = None
        
        # The current modes of tracking, for use with "live update" changes.
        #
        self._mouseTracking = None
        self._controlTracking = None
        self._textTracking = None
        self._edgeMargin = None
        self._pointerFollowsZoomer = None
        self._pointerFollowsFocus = None

        _settingsManager = getattr(orca, '_settingsManager')

        plugins = _settingsManager.getPlugins(_settingsManager.getSetting('activeProfile')[1])
        print 'estoy en el enable del mag y plugins = ', plugins

        self.isActive = plugins['mag']['active']

        settings.enableMagnifier = True
        self.shutdown()
        self.init()
        
    def __setROI(self, rect):
        """Sets the region of interest.
    
        Arguments:
        - rect: A GNOME.Magnifier.RectBounds object.
        """
    
        debug.println(debug.LEVEL_ALL, "mag.py:__setROI: (%d, %d), (%d, %d)" \
                      % (rect.x1, rect.y1, rect.x2, rect.y2))
    
        self._roi = rect
    
        self._zoomer.setROI(self._roi)
        self._zoomer.markDirty(self._roi)  # [[[TODO: WDW - for some reason, this seems
                                 # necessary.]]]
    def __setROICenter(self, x, y):
        """Centers the region of interest around the given point.
    
        Arguments:
        - x: integer in unzoomed system coordinates representing x component
        - y: integer in unzoomed system coordinates representing y component
        """
    
        if not self._initialized:
            return
    
        if x < self._minROIX:
            x = self._minROIX
        elif x > self._maxROIX:
            x = self._maxROIX
    
        if y < self._minROIY:
            y = self._minROIY
        elif y > self._maxROIY:
            y = self._maxROIY
    
        x1 = x - (self._roiWidth / 2)
        y1 = y - (self._roiHeight / 2)
    
        x2 = x1 + self._roiWidth
        y2 = y1 + self._roiHeight
    
        self.__setROI(GNOME.Magnifier.RectBounds(x1, y1, x2, y2))
    
    def __setROIPush(self, x, y):
        """Nudges the ROI if the pointer bumps into the edge of it.  The point
        given is assumed to be the point where the mouse pointer is.
    
        Arguments:
        - x: integer in unzoomed system coordinates representing x component
        - y: integer in unzoomed system coordinates representing y component
        """
    
        #needNewROI = False
        newROI = GNOME.Magnifier.RectBounds(self._roi.x1, self._roi.y1, self._roi.x2, self._roi.y2)
        if x < self._roi.x1:
            #needNewROI = True
            newROI.x1 = x
            newROI.x2 = x + self._roiWidth
        elif x > self._roi.x2:
            #needNewROI = True
            newROI.x2 = x
            newROI.x1 = x - self._roiWidth
        if y < self._roi.y1:
            #needNewROI = True
            newROI.y1 = y
            newROI.y2 = y + self._roiHeight
        elif y > self._roi.y2:
            #needNewROI = True
            newROI.y2 = y
            newROI.y1 = y - self._roiHeight
    
        # Well...we'll always update the ROI so the new gnome-mag API
        # will redraw the crosswires for us.
        #
        #if needNewROI:
        if True:
            self.__setROI(newROI)
    
    def __setROICursorPush(self, x, y, width, height, edgeMargin = 0):
        """Nudges the ROI if the caret or control is not visible.
    
        Arguments:
        - x: integer in unzoomed system coordinates representing x component
        - y: integer in unzoomed system coordinates representing y component
        - width: integer in unzoomed system coordinates representing the width
        - height: integer in unzoomed system coordinates representing the height
        - edgeMargin: a percentage representing how close to the edge we can get
                      before we need to push
        """
    
        # The edge margin should not exceed 50%. (50% is a centered alignment).
        #
        edgeMargin = min(edgeMargin, 50)/100.00
        magZoomFactor = _settingsManager.getSetting('magZoomFactor')
        edgeMarginX = edgeMargin * self._sourceDisplayBounds.x2/magZoomFactor
        edgeMarginY = edgeMargin * self._sourceDisplayBounds.y2/magZoomFactor
    
        # Determine if the accessible is partially to the left, right,
        # above, or below the current region of interest (ROI).
        #
        leftOfROI = (x - edgeMarginX) <= self._roi.x1
        rightOfROI = (x + width + edgeMarginX) >= self._roi.x2
        aboveROI = (y - edgeMarginY)  <= self._roi.y1
        belowROI = (y + height + edgeMarginY) >= self._roi.y2
    
        # If it is already completely showing, do nothing.
        #
        visibleX = not(leftOfROI or rightOfROI)
        visibleY = not(aboveROI or belowROI)
        if visibleX and visibleY:
            self._zoomer.markDirty(self._roi)
    
        # The algorithm is devised to move the ROI as little as possible, yet
        # favor the top left side of the object [[[TODO: WDW - the left/right
        # top/bottom favoring should probably depend upon the locale.  Also,
        # I had the notion of including a floating point snap factor between
        # 0.0 and 1.0 that would determine how to position the object in the
        # window relative to the ROI edges.  A snap factor of -1 would mean to
        # snap to the closest edge.  A snap factor of 0.0 would snap to the
        # left most or top most edge, a snap factor of 1.0 would snap to the
        # right most or bottom most edge.  Any number in between would divide
        # the two.]]]
        #
        x1 = self._roi.x1
        x2 = self._roi.x2
        y1 = self._roi.y1
        y2 = self._roi.y2
    
        if leftOfROI:
            x1 = max(self._sourceDisplayBounds.x1, x - edgeMarginX)
            x2 = x1 + self._roiWidth
        elif rightOfROI:
            x = min(self._sourceDisplayBounds.x2, x + edgeMarginX)
            if width > self._roiWidth:
                x1 = x
                x2 = x1 + self._roiWidth
            else:
                x2 = x + width
                x1 = x2 - self._roiWidth
    
        if aboveROI:
            y1 = max(self._sourceDisplayBounds.y1, y - edgeMarginY)
            y2 = y1 + self._roiHeight
        elif belowROI:
            y = min(self._sourceDisplayBounds.y2, y + edgeMarginY)
            if height > self._roiHeight:
                y1 = y
                y2 = y1 + self._roiHeight
            else:
                y2 = y + height
                y1 = y2 - self._roiHeight
    
        self.__setROI(GNOME.Magnifier.RectBounds(x1, y1, x2, y2))
    
    def __setROIProportional(self, x, y):
        """Positions the ROI proportionally to where the pointer is on the screen.
    
        Arguments:
        - x: integer in unzoomed system coordinates representing x component
        - y: integer in unzoomed system coordinates representing y component
        """
    
        if not self._initialized:
            return
    
        if not self._sourceDisplayBounds:
            self.__setROICenter(x, y)
        else:
            halfScreenWidth  = (self._sourceDisplayBounds.x2 \
                                - self._sourceDisplayBounds.x1) / 2.0
            halfScreenHeight = (self._sourceDisplayBounds.y2 \
                                - self._sourceDisplayBounds.y1) / 2.0
    
            proportionX = (halfScreenWidth  - x) / halfScreenWidth
            proportionY = (halfScreenHeight - y) / halfScreenHeight
    
            centerX = x + int(proportionX * self._roiWidth  / 2.0)
            centerY = y + int(proportionY * self._roiHeight / 2.0)
    
            self.__setROICenter(centerX, centerY)
    
    # Used for tracking the pointer.
    #
    def __onMouseEvent(self, e):
        """
        Arguments:
        - e: at-spi event from the at-api registry
        """
    
        isNewMouseMovement = (time.time() - self._lastMouseEventTime > 1)
        self._lastMouseEventTime = time.time()
    
        [x, y] = [e.detail1, e.detail2]
    
        if self._pointerFollowsZoomer and isNewMouseMovement \
           and not self._lastMouseEventWasRoute:
            mouseIsVisible = (self._roi.x1 < x < self._roi.x2) and (self._roi.y1 < y < self._roi.y2)
            if not mouseIsVisible and orca_state.locusOfFocus:
                if self._mouseTracking == settings.MAG_TRACKING_MODE_CENTERED:
                    x = (self._roi.x1 + self._roi.x2) / 2
                    y = (self._roi.y1 + self._roi.y2) / 2
                elif self._mouseTracking != settings.MAG_TRACKING_MODE_NONE:
                    try:
                        extents = \
                            orca_state.locusOfFocus.queryComponent().getExtents(0)
                    except:
                        extents = None
                    if extents:
                        x = extents.x
                        y = extents.y + extents.height - 1
    
                eventsynthesizer.generateMouseEvent(x, y, "abs")
                self._lastMouseEventWasRoute = True
    
        # If True, we're using gnome-mag >= 0.13.1 that allows us to
        # control where to draw the cursor and crosswires.
        #
        if self._pollMouseDisabled:
            self._zoomer.setPointerPos(x, y)
    
        if self._lastMouseEventWasRoute:
            # If we just moved the mouse pointer to the menu item or control
            # with focus, we don't want to do anything.
            #
            self._lastMouseEventWasRoute = False
            self._zoomer.markDirty(self._roi)
            return
    
        if self._mouseTracking == settings.MAG_TRACKING_MODE_PUSH:
            self.__setROIPush(x, y)
        elif self._mouseTracking == settings.MAG_TRACKING_MODE_PROPORTIONAL:
            self.__setROIProportional(x, y)
        elif self._mouseTracking == settings.MAG_TRACKING_MODE_CENTERED:
            self.__setROICenter(x, y)
    
    def __getValueText(self, slot, value):
        valueText = ""
        if slot == "cursor-hotspot":
            valueText = "(%d, %d)" % (value.x, value.y)
        elif slot == "source-display-bounds":
            valueText = "(%d, %d),(%d, %d)" \
                        % (value.x1, value.y1, value.x2, value.y2)
        elif slot == "target-display-bounds":
            valueText = "(%d, %d),(%d, %d)" \
                        % (value.x1, value.y1, value.x2, value.y2)
        elif slot == "viewport":
            valueText = "(%d, %d),(%d, %d)" \
                        % (value.x1, value.y1, value.x2, value.y2)
        return valueText
    
    def __dumpPropertyBag(self, obj):
        pbag = obj.getProperties()
        slots = pbag.getKeys("")
        print "  Available slots: ", pbag.getKeys("")
        for slot in slots:
            # These crash the magnifier since it doesn't know how to marshall
            # them to us.
            #
            if slot in ["cursor-set", "smoothing-type"]:
                continue
            print "    About '%s':" % slot
            print "    Doc Title:", pbag.getDocTitle(slot)
            print "    Type:", pbag.getType(slot)
            value = pbag.getDefault(slot).value()
            print "    Default value:", value, self.__getValueText(slot, value)
            value = pbag.getValue(slot).value()
            print "    Current value:", value, self.__getValueText(slot, value)
            print
    
    def __setupMagnifier(self, position, left=None, top=None, right=None, bottom=None,
                         restore=None):
        """Creates the magnifier in the position specified.
    
        Arguments:
        - position: the position/type of zoomer (full, left half, etc.)
        - left:     the left edge of the zoomer (only applicable for custom)
        - top:      the top edge of the zoomer (only applicable for custom)
        - right:    the right edge of the zoomer (only applicable for custom)
        - bottom:   the top edge of the zoomer (only applicable for custom)
        - restore:  a dictionary of all of the settings which should be restored
        """
    
        self._magnifier.clearAllZoomRegions()
    
        if not restore:
            restore = {}
    
        # Define where the magnifier will live.
        #
        try:
            self._magnifier.TargetDisplay = \
                _settingsManager.getSetting('magTargetDisplay')
        except:
            pass
    
        # Define what will be magnified.
        #
        try:
            self._magnifier.SourceDisplay = \
                _settingsManager.getSetting('magSourceDisplay')
        except:
            pass
    
        # Find out if we're using composite.
        #
        try:
            self._fullScreenCapable = self._magnifier.fullScreenCapable()
        except:
            debug.printException(debug.LEVEL_WARNING)
    
        # If we are running in full screen mode, try to hide the original cursor
        # (assuming the user wants to). See bug #533095 for more details.
        # Depends upon new functionality in gnome-mag, so just catch the 
        # exception if this functionality isn't there.
        #
        hideCursor = restore.get('magHideCursor',
                                 _settingsManager.getSetting('magHideCursor'))
        if hideCursor \
           and self._fullScreenCapable \
           and self._magnifier.SourceDisplay == self._magnifier.TargetDisplay \
           and position == settings.MAG_ZOOMER_TYPE_FULL_SCREEN:
            self.hideSystemPointer(True)
        else:
            self.hideSystemPointer(False)
    
        self._magnifierPBag = self._magnifier.getProperties()
        sdb = self._magnifierPBag.getValue("source-display-bounds").value()
        if not self._originalSourceDisplayBounds:
            self._originalSourceDisplayBounds = sdb
        elif self._liveUpdatingMagnifier:
            sdb = self._originalSourceDisplayBounds
    
        # Find out where the user wants to place the target display.
        #
        if self._fullScreenCapable and \
           position == settings.MAG_ZOOMER_TYPE_FULL_SCREEN:
            prefLeft = 0
            prefTop = 0
            prefRight = sdb.x2
            prefBottom = sdb.y2
        elif position == settings.MAG_ZOOMER_TYPE_TOP_HALF:
            prefLeft = 0
            prefTop = 0
            prefRight = sdb.x2
            prefBottom = sdb.y2 / 2
        elif position == settings.MAG_ZOOMER_TYPE_BOTTOM_HALF:
            prefLeft = 0
            prefTop = sdb.y2 / 2
            prefRight = sdb.x2
            prefBottom = sdb.y2
        elif position == settings.MAG_ZOOMER_TYPE_LEFT_HALF:
            prefLeft = 0
            prefTop = 0
            prefRight = sdb.x2 / 2
            prefBottom = sdb.y2
        elif position == settings.MAG_ZOOMER_TYPE_RIGHT_HALF:
            prefLeft = sdb.x2 / 2
            prefTop = 0
            prefRight = sdb.x2
            prefBottom = sdb.y2
        else:
            prefLeft   = left or _settingsManager.getSetting('magZoomerLeft')
            prefTop    = top or _settingsManager.getSetting('magZoomerTop')
            prefRight  = right or _settingsManager.getSetting('magZoomerRight')
            prefBottom = bottom or _settingsManager.getSetting('magZoomerBottom')
        orca_state.zoomerType = position
        updateTarget = True
    
        # If we're not using composite, bad things will happen if we allow the
        # target display to occupy more than 50% of the full screen.  Also, if
        # it occupies the same space as something that should be magnified (e.g.
        # the Applications menu), that item will not be magnified. Therefore,
        # we're going to prefer the right half of the screen for the target
        # display -- unless gnome-mag is already running and not in "full screen"
        # mode.
        #
        if not self._fullScreenCapable \
           and self._magnifier.SourceDisplay == self._magnifier.TargetDisplay:
            # At this point, the target display bounds have not been set. if they
            # are all 0, then we know that gnome-mag isn't already running.
            #
            magAlreadyRunning = False
            tdb = self._magnifierPBag.getValue("target-display-bounds").value()
            if tdb.x1 or tdb.x2 or tdb.y1 or tdb.y2:
                magAlreadyRunning = True
    
            # At this point, because we haven't set the target display bounds,
            # gnome-mag has not modified the source display bounds. Therefore,
            # we can use the current source display bounds to get the
            # dimensions of the full screen -- assuming gnome-mag has not
            # already been launched with a split screen. Comparing the values
            # of the source and target display bounds lets us know if gnome-mag
            # has been started in "full screen" mode.
            #
            magFullScreen = magAlreadyRunning \
                            and (tdb.x1 == sdb.x1) and (tdb.x2 == sdb.x2) \
                            and (tdb.y1 == sdb.y1) and (tdb.y2 == sdb.y2)
    
            sourceArea = (sdb.x2 - sdb.x1) * (sdb.y2 - sdb.y1)
            prefArea = (prefRight - prefLeft) * (prefBottom - prefTop)
            if prefArea > sourceArea/2:
                debug.println(
                    debug.LEVEL_WARNING,
                    "Composite is not being used. The preferred target area is\n"\
                    "greater than 50% of the source area.  These settings can\n"\
                    "render the contents of the screen inaccessible.")
                if not magAlreadyRunning or magFullScreen:
                    debug.println(
                        debug.LEVEL_WARNING,
                        "Setting the target display to the screen's right half.")
                    prefRight  = sdb.x2
                    prefLeft   = sdb.x2/2
                    prefTop    = sdb.y1
                    prefBottom = sdb.y2
                elif sdb.y2 > 0:
                    updateTarget = False
                    debug.println(
                        debug.LEVEL_WARNING,
                        "Gnome-mag is already running.  Using those settings.")
    
        # Now, tell the magnifier where we want it to live on the target display.
        # The coordinates are in screen coordinates of the target display.
        # This will have the side effect of setting up other stuff for us, such
        # as source-display-bouinds.
        #
        if updateTarget:
            tdb = self._magnifierPBag.getValue("target-display-bounds").value()
            self._magnifierPBag.setValue(
                "target-display-bounds",
                ORBit.CORBA.Any(
                    ORBit.CORBA.TypeCode(
                        tdb.__typecode__.repo_id),
                    GNOME.Magnifier.RectBounds(prefLeft,
                                               prefTop,
                                               prefRight,
                                               prefBottom)))
    
        bonobo.pbclient_set_string(self._magnifierPBag, "cursor-set", "default")
    
        enableCursor = restore.get(
            'enableMagCursor', _settingsManager.getSetting('enableMagCursor'))
        explicitSize = restore.get(
            'enableMagCursorExplicitSize',
            _settingsManager.getSetting('enableMagCursorExplicitSize'))
        size = restore.get(
            'magCursorSize', _settingsManager.getSetting('magCursorSize'))
        self.setMagnifierCursor(enableCursor, explicitSize, size, False)
    
        value = restore.get(
            'magCursorColor', _settingsManager.getSetting('magCursorColor'))
        self.setMagnifierObjectColor("cursor-color", value, False)
    
        value = restore.get(
            'magCrossHairColor', _settingsManager.getSetting('magCrossHairColor'))
        self.setMagnifierObjectColor("crosswire-color", value, False)
    
        enableCrossHair = restore.get(
            'enableMagCrossHair', _settingsManager.getSetting('enableMagCrossHair'))
        self.setMagnifierCrossHair(enableCrossHair, False)
    
        value = restore.get(
            'enableMagCrossHairClip', 
            _settingsManager.getSetting('enableMagCrossHairClip'))
        self.setMagnifierCrossHairClip(value, False)
    
        orca_state.mouseEnhancementsEnabled = enableCursor or enableCrossHair
    
    def __setupZoomer(self, restore=None):
        """Creates a zoomer in the magnifier
        Arguments:
        - restore:  a dictionary of all of the settings which should be restored
        """
    
        if not restore:
            restore = {}
    
        self._targetDisplayBounds = self._magnifierPBag.getValue(
            "target-display-bounds").value()
    
        debug.println(debug.LEVEL_ALL,
                      "Magnifier target bounds preferences: (%d, %d), (%d, %d)" \
                      % (_settingsManager.getSetting('magZoomerLeft'),
                         _settingsManager.getSetting('magZoomerTop'),
                         _settingsManager.getSetting('magZoomerRight'),
                         _settingsManager.getSetting('magZoomerBottom')))
    
        debug.println(debug.LEVEL_ALL,
                      "Magnifier target bounds actual: (%d, %d), (%d, %d)" \
                      % (self._targetDisplayBounds.x1, self._targetDisplayBounds.y1, \
                         self._targetDisplayBounds.x2, self._targetDisplayBounds.y2))
    
        # If the COMPOSITE support is not enabled in gnome-mag, then the
        # source-display-bounds will be adjusted to accomodate portion of the
        # display not being covered by the magnifier (assuming there is only
        # one display).  Otherwise, the source-display-bounds will be the
        # entire source screen.
        #
        self._sourceDisplayBounds = self._magnifierPBag.getValue(
            "source-display-bounds").value()
    
        debug.println(debug.LEVEL_ALL,
                      "Magnifier source bounds actual: (%d, %d), (%d, %d)" \
                      % (self._sourceDisplayBounds.x1, self._sourceDisplayBounds.y1, \
                         self._sourceDisplayBounds.x2, self._sourceDisplayBounds.y2))
    
        # If there is nothing we can possibly magnify, switch to the right half.
        #
        if ((self._sourceDisplayBounds.x2 - self._sourceDisplayBounds.x1) == 0) \
            or ((self._sourceDisplayBounds.y2 - self._sourceDisplayBounds.y1) == 0):
            debug.println(
                debug.LEVEL_SEVERE,
                "There is nothing to magnify.  This is usually caused\n" \
                "by a preferences setting that tries to take up the\n" \
                "full screen for magnification, but the underlying\n"
                "system does not support full screen magnification.\n"
                "The causes of that are generally that COMPOSITE\n" \
                "support has not been enabled in gnome-mag or the\n" \
                "X Window System Server.  As a result of this issue,\n" \
                "defaulting to the right half of the screen.\n")
            self._fullScreenCapable = False
            self.__setupMagnifier(settings.MAG_ZOOMER_TYPE_CUSTOM,
                             self._targetDisplayBounds.x1/2,
                             self._targetDisplayBounds.y1,
                             self._targetDisplayBounds.x2,
                             self._targetDisplayBounds.y2)
            self._sourceDisplayBounds = self._magnifierPBag.getValue(
                "source-display-bounds").value()
            self._targetDisplayBounds = self._magnifierPBag.getValue(
                "target-display-bounds").value()
    
        # Now, we create a zoom region to occupy the whole magnifier (i.e.,
        # the viewport is in target region coordinates and we make the
        # viewport be the whole target region).  Note, since we're starting
        # at (0, 0), the viewportWidth and viewportHeight are the same as
        # the x2, y2 values for a rectangular region.
        #
        viewportWidth = self._targetDisplayBounds.x2 - self._targetDisplayBounds.x1
        viewportHeight = self._targetDisplayBounds.y2 - self._targetDisplayBounds.y1
    
        debug.println(debug.LEVEL_ALL,
                      "Magnifier zoomer viewport desired: (0, 0), (%d, %d)" \
                      % (viewportWidth, viewportHeight))
    
        # Now, let's see what the ROI looks like.
        #
        zoomFactor = _settingsManager.getSetting('magZoomFactor')
        debug.println(debug.LEVEL_ALL,
                     "Magnifier source width: %d (viewport can show %d)" \
                      % (self._sourceDisplayBounds.x2 - self._sourceDisplayBounds.x1,
                      viewportWidth / zoomFactor))
        debug.println(debug.LEVEL_ALL,
                      "Magnifier source height: %d (viewport can show %d)" \
                      % (self._sourceDisplayBounds.y2 - self._sourceDisplayBounds.y1,
                       viewportHeight / zoomFactor))
    
        # Adjust the ROI in the event the source window is too small for the
        # target window.  This usually happens when someone expects COMPOSITE
        # to be enabled, but it isn't.  As a result, they usually have a very
        # big grey magnifier on their screen.
        #
        self._roiWidth  = min(self._sourceDisplayBounds.x2 - self._sourceDisplayBounds.x1,
                         viewportWidth / zoomFactor)
        self._roiHeight = min(self._sourceDisplayBounds.y2 - self._sourceDisplayBounds.y1,
                         viewportHeight / zoomFactor)
    
        debug.println(debug.LEVEL_ALL,
                      "Magnifier zoomer ROI size desired: width=%d, height=%d)" \
                      % (self._roiWidth, self._roiHeight))
    
        # Create the zoomer with a magnification factor, an initial ROI, and
        # where in magnifier we want it to be (we want it to be in the whole
        # magnifier). Initially set the viewport so that it does not appear.
        # After we set all of the color properties, reset the viewport to
        # the correct position.  This will prevent the user from seeing the
        # individual property changes (e.g. brightness, contrast) upon load.
        #
        self._zoomer = self._magnifier.createZoomRegion(
            zoomFactor, zoomFactor,
            GNOME.Magnifier.RectBounds(0, 0, self._roiWidth, self._roiHeight),
            GNOME.Magnifier.RectBounds(0, 0, 1, 1))
    
        self._zoomerPBag = self._zoomer.getProperties()
        bonobo.pbclient_set_boolean(self._zoomerPBag, "is-managed", True)
    
        value = restore.get('magZoomFactor', zoomFactor)
        self.setZoomerMagFactor(value, value, False)
    
        value = restore.get(
            'enableMagZoomerColorInversion',
            _settingsManager.getSetting('enableMagZoomerColorInversion'))
        self.setZoomerColorInversion(value, False)
    
        brightness = restore.get(
            'magBrightnessLevel', _settingsManager.getSetting('magBrightnessLevel'))
        r = brightness + \
            restore.get('magBrightnessLevelRed',
                        _settingsManager.getSetting('magBrightnessLevelRed'))
        g = brightness + \
            restore.get('magBrightnessLevelGreen',
                        _settingsManager.getSetting('magBrightnessLevelGreen'))
        b = brightness + \
            restore.get('magBrightnessLevelBlue',
                        _settingsManager.getSetting('magBrightnessLevelBlue'))
        self.setZoomerBrightness(r, g, b, False)
    
        contrast = restore.get(
            'magContrastLevel', _settingsManager.getSetting('magContrastLevel'))
        r = contrast + \
            restore.get('magContrastLevelRed',
                        _settingsManager.getSetting('magContrastLevelRed'))
        g = contrast + \
            restore.get('magContrastLevelGreen',
                        _settingsManager.getSetting('magContrastLevelGreen'))
        b = contrast + \
            restore.get('magContrastLevelBlue',
                        _settingsManager.getSetting('magContrastLevelBlue'))
        self.setZoomerContrast(r, g, b, False)
    
        value = restore.get('magColorFilteringMode',
                            _settingsManager.getSetting('magColorFilteringMode'))
        self.setZoomerColorFilter(value, False)
    
        value = restore.get(
            'magZoomerType', _settingsManager.getSetting('magZoomerType'))
        if value == settings.MAG_ZOOMER_TYPE_FULL_SCREEN:
            size = 0
        else:
            size = restore.get('magZoomerBorderSize',
                               _settingsManager.getSetting('magZoomerBorderSize'))
        color = restore.get('magZoomerBorderColor',
                            _settingsManager.getSetting('magZoomerBorderColor'))
        self.setZoomerObjectSize("border-size", size, False)
        self.setZoomerObjectColor("border-color", color, False)
    
        value = restore.get('magSmoothingMode',
                            _settingsManager.getSetting('magSmoothingMode'))
        self.setZoomerSmoothingType(value, False)
    
        # Now it's safe to display the viewport.
        #
        bounds = GNOME.Magnifier.RectBounds(0, 0, viewportWidth, viewportHeight)
        self._zoomer.moveResize(bounds)
    
        # Try to use gnome-mag >= 0.13.1 to allow us to control where to
        # draw the cursor and crosswires.
        #
        try:
            bonobo.pbclient_set_boolean(self._zoomerPBag, "poll-mouse", False)
            self._pollMouseDisabled = True
        except:
            self._pollMouseDisabled = False
    
        self.__updateROIDimensions()
        self._magnifier.addZoomRegion(self._zoomer)
    
    def __updateROIDimensions(self):
        """Updates the ROI width, height, and maximum and minimum values.
        """
    
        viewport = self._zoomerPBag.getValue("viewport").value()
    
        debug.println(debug.LEVEL_ALL,
                      "Magnifier viewport actual: (%d, %d), (%d, %d)" \
                      % (viewport.x1, viewport.y1, viewport.x2, viewport.y2))
    
        magx = self._zoomerPBag.getValue("mag-factor-x").value()
        magy = self._zoomerPBag.getValue("mag-factor-y").value()
    
        self._roiWidth  = min(self._sourceDisplayBounds.x2 - self._sourceDisplayBounds.x1,
                         (viewport.x2 - viewport.x1) / magx)
        self._roiHeight = min(self._sourceDisplayBounds.y2 - self._sourceDisplayBounds.y1,
                         (viewport.y2 - viewport.y1) / magy)
    
        debug.println(debug.LEVEL_ALL,
                      "Magnifier zoomer ROI size actual: width=%d, height=%d)" \
                      % (self._roiWidth, self._roiHeight))
    
        self._minROIX = self._sourceDisplayBounds.x1 + (self._roiWidth / 2)
        self._minROIY = self._sourceDisplayBounds.y1 + (self._roiHeight / 2)
    
        self._maxROIX = self._sourceDisplayBounds.x2 - (self._roiWidth / 2)
        self._maxROIY = self._sourceDisplayBounds.y2 - (self._roiHeight / 2)
    
        debug.println(debug.LEVEL_ALL,
                      "Magnifier ROI min/max center: (%d, %d), (%d, %d)" \
                      % (self._minROIX, self._minROIY, self._maxROIX, self._maxROIY))
    
    def applySettings(self):
        """Looks at the user settings and applies them to the magnifier."""
    
        self.__setupMagnifier(_settingsManager.getSetting('magZoomerType'))
        self.__setupZoomer()
      
        self._mouseTracking = _settingsManager.getSetting('magMouseTrackingMode')
        self._controlTracking = _settingsManager.getSetting('magControlTrackingMode')
        self._textTracking = _settingsManager.getSetting('magTextTrackingMode')
        self._edgeMargin = _settingsManager.getSetting('magEdgeMargin')
        self._pointerFollowsZoomer = \
            _settingsManager.getSetting('magPointerFollowsZoomer')
        self._pointerFollowsFocus = \
            _settingsManager.getSetting('magPointerFollowsFocus')
    
        #print "MAGNIFIER PROPERTIES:", self._magnifier
        #__dumpPropertyBag(self._magnifier)
        #print "ZOOMER PROPERTIES:", self._zoomer
        #__dumpPropertyBag(self._zoomer)
    
    def magnifyAccessible(self, event, obj, extents=None):
        """Sets the region of interest to the upper left of the given
        accessible, if it implements the Component interface.  Otherwise,
        does nothing.
    
        Arguments:
        - event: the Event that caused this to be called
        - obj: the accessible
        """
    
        if not self._initialized:
            return
    
        # Avoid jerking the display around if the mouse is what ended up causing
        # this event.  We guess this by seeing if this request has come in within
        # a close period of time.  [[[TODO: WDW - this is a hack and really
        # doesn't belong here.  Plus, the delta probably should be adjustable.]]]
        #
        currentTime = time.time()
        if (currentTime - self._lastMouseEventTime) < 0.2: # 200 milliseconds
            return
    
        haveSomethingToMagnify = False
    
        if extents:
            [x, y, width, height] = extents
            haveSomethingToMagnify = True
        elif event and event.type.startswith("object:text-caret-moved"):
            try:
                text = obj.queryText()
                if text and (text.caretOffset >= 0):
                    offset = text.caretOffset
                    if offset == text.characterCount:
                        offset -= 1
                    [x, y, width, height] = \
                        text.getCharacterExtents(offset, 0)
                    haveSomethingToMagnify = (width + height > 0)
                        
            except:
                haveSomethingToMagnify = False
    
            if haveSomethingToMagnify:
                if self._textTracking == settings.MAG_TRACKING_MODE_CENTERED:
                    self.__setROICenter(x, y)
                elif self._textTracking == settings.MAG_TRACKING_MODE_PUSH:
                    self.__setROICursorPush(x, y, width, height, self._edgeMargin)
                return
    
        if not haveSomethingToMagnify:
            try:
                extents = obj.queryComponent().getExtents(0)
                [x, y, width, height] = \
                    [extents.x, extents.y, extents.width, extents.height]
                haveSomethingToMagnify = True
            except:
                haveSomethingToMagnify = False
    
        if haveSomethingToMagnify:
            if self._pointerFollowsFocus:
                self._lastMouseEventWasRoute = True
                eventsynthesizer.generateMouseEvent(x, y + height - 1, "abs")
    
            if self._controlTracking == settings.MAG_TRACKING_MODE_CENTERED:
                centerX = x + width/2
                centerY = y + height/2
    
                # Be sure that the upper-left corner of the object will still
                # be visible on the screen.
                #
                if width > self._roiWidth:
                    centerX = x
                if height > self._roiHeight:
                    centerY = y
    
                self.__setROICenter(centerX, centerY)
            elif self._controlTracking == settings.MAG_TRACKING_MODE_PUSH:
                self.__setROICursorPush(x, y, width, height)
    
    def init(self):
        """Initializes the magnifier, bringing the magnifier up on the
        display.
    
        Returns True if the initialization procedure was run or False if this
        module has already been initialized.
        """
    
        if not self._magnifierAvailable or not settings.enableMagnifier or not \
                self.isActive:
            return False

        if self._initialized:
            return False
    
        self._magnifier = bonobo.get_object("OAFIID:GNOME_Magnifier_Magnifier:0.9",
                                       "GNOME/Magnifier/Magnifier")
    
        try:
            self._initialized = True
            self.applySettings()
            pyatspi.Registry.registerEventListener(self.__onMouseEvent, "mouse:abs")
    
            # Zoom to the upper left corner of the display for now.
            #
            self.__setROICenter(0, 0)
    
            return True
        except:
            self._initialized = False
            self._magnifier.dispose()
            raise
    
    def shutdown(self):
        """Shuts down the magnifier module.
        Returns True if the shutdown procedure was run or False if this
        module has not been initialized.
        """
    
        if not self._magnifierAvailable:
            return False
    
        if not self._initialized:
            return False
    
        pyatspi.Registry.deregisterEventListener(self.__onMouseEvent,"mouse:abs")
    
        # Someone might have killed the magnifier on us.  They shouldn't
        # have done so, but we need to be able to recover if they did.
        # See http://bugzilla.gnome.org/show_bug.cgi?id=375396.
        #
        try:
            self.hideSystemPointer(False)
            self._magnifier.clearAllZoomRegions()
            self._magnifier.dispose()
        except:
            debug.printException(debug.LEVEL_WARNING)
    
        self._magnifier = None
    
        self._initialized = False
    
        return True
    
    ######################################################################
    #                                                                    #
    #              Convenience functions for "live" changes              #
    #                                                                    #
    ######################################################################
    
    def setupMagnifier(self, position, left=None, top=None, right=None, bottom=None,
                       restore=None):
        """Creates the magnifier in the position specified.
    
        Arguments:
        - position: the position/type of zoomer (full, left half, etc.)
        - left:     the left edge of the zoomer (only applicable for custom)
        - top:      the top edge of the zoomer (only applicable for custom)
        - right:    the right edge of the zoomer (only applicable for custom)
        - bottom:   the top edge of the zoomer (only applicable for custom)
        - restore:  a dictionary of all of the settings that should be restored
        """
    
        if not self._initialized:
            return
    
        self._liveUpdatingMagnifier = True
        self.__setupMagnifier(position, left, top, right, bottom, restore)
        self.__setupZoomer(restore)
    
    def setMagnifierCursor(self, enabled, customEnabled, size, updateScreen=True):
        """Sets the cursor.
    
        Arguments:
        - enabled:        Whether or not the cursor should be enabled
        - customEnabled:  Whether or not a custom size has been enabled
        - size:           The size it should be set to
        - updateScreen:   Whether or not to update the screen
        """
    
        if not self._initialized:
            return
        try:
            mag = self._zoomerPBag.getValue("mag-factor-x").value()
        except:
            mag = _settingsManager.getSetting('magZoomFactor')
    
        if enabled:
            scale = 1.0 * mag
        else:
            scale = 0.0
    
        if not (enabled and customEnabled):
            size = 0
    
        bonobo.pbclient_set_float(self._magnifierPBag, "cursor-scale-factor", scale)
        bonobo.pbclient_set_long(self._magnifierPBag, "cursor-size", size)
    
        if updateScreen:
            self._zoomer.markDirty(self._roi)
    
    def setMagnifierCrossHair(self, enabled, updateScreen=True):
        """Sets the cross-hair.
    
        Arguments:
        - enabled: Whether or not the cross-hair should be enabled
        - updateScreen:  Whether or not to update the screen
        """
    
        if not self._initialized:
            return
    
        size = 0
        if enabled:
            size = _settingsManager.getSetting('magCrossHairSize')
    
        bonobo.pbclient_set_long(self._magnifierPBag, "crosswire-size", size)
    
        if updateScreen:
            self._zoomer.markDirty(self._roi)
    
    def setMagnifierCrossHairClip(self, enabled, updateScreen=True):
        """Sets the cross-hair clip.
    
        Arguments:
        - enabled: Whether or not the cross-hair clip should be enabled
        - updateScreen:   Whether or not to update the screen
        """
    
        if not self._initialized:
            return
    
        bonobo.pbclient_set_boolean(self._magnifierPBag, "crosswire-clip", enabled)
    
        if updateScreen:
            self._zoomer.markDirty(self._roi)
    
    def setZoomerColorInversion(self, enabled, updateScreen=True):
        """Sets the color inversion.
    
        Arguments:
        - enabled: Whether or not color inversion should be enabled
        - updateScreen:   Whether or not to update the screen
        """
    
        if not self._initialized:
            return
    
        bonobo.pbclient_set_boolean(self._zoomerPBag, "inverse-video", enabled)
    
        if updateScreen:
            self._zoomer.markDirty(self._roi)
    
    def setZoomerBrightness(self, red=0, green=0, blue=0, updateScreen=True):
        """Increases/Decreases the brightness level by the specified
        increments.  Increments are floats ranging from -1 (black/no
        brightenss) to 1 (white/100% brightness).  0 means no change.
    
        Arguments:
        - red:    The amount to alter the red brightness level
        - green:  The amount to alter the green brightness level
        - blue:   The amount to alter the blue brightness level
        - updateScreen:   Whether or not to update the screen
        """
    
        if not self._initialized:
            return
    
        self._zoomer.setBrightness(red, green, blue)
    
        if updateScreen:
            self._zoomer.markDirty(self._roi)
    
    def setZoomerContrast(self, red=0, green=0, blue=0, updateScreen=True):
        """Increases/Decreases the contrast level by the specified
        increments.  Increments are floats ranging from -1 (grey/no
        contrast) to 1 (white/back/100% contrast).  0 means no change.
    
        Arguments:
        - red:    The amount to alter the red contrast level
        - green:  The amount to alter the green contrast level
        - blue:   The amount to alter the blue contrast level
        - updateScreen:  Whether or not to update the screen
        """
    
        if not self._initialized:
            return
    
        self._zoomer.setContrast(red, green, blue)
    
        if updateScreen:
            self._zoomer.markDirty(self._roi)
    
    def setMagnifierObjectSize(self, magProperty, size, updateScreen=True):
        """Sets the specified magnifier property to the specified size.
    
        Arguments:
        - magProperty:   The property to set (as a string)
        - size:          The size to apply
        - updateScreen:  Whether or not to update the screen
        """
    
        if not self._initialized:
            return
    
        bonobo.pbclient_set_long(self._magnifierPBag, magProperty, size)
    
        if updateScreen:
            self._zoomer.markDirty(self._roi)
    
    def setZoomerObjectSize(self, magProperty, size, updateScreen=True):
        """Sets the specified zoomer property to the specified size.
    
        Arguments:
        - magProperty:   The property to set (as a string)
        - size:          The size to apply
        - updateScreen:  Whether or not to update the screen
        """
    
        if not self._initialized:
            return
    
        if magProperty == "border-size":
            try:
                left = right = top = bottom = 0
                if orca_state.zoomerType == settings.MAG_ZOOMER_TYPE_RIGHT_HALF:
                    left = size
                elif orca_state.zoomerType == settings.MAG_ZOOMER_TYPE_LEFT_HALF:
                    right = size
                elif orca_state.zoomerType == settings.MAG_ZOOMER_TYPE_TOP_HALF:
                    bottom = size
                elif orca_state.zoomerType == settings.MAG_ZOOMER_TYPE_BOTTOM_HALF:
                    top = size
                elif orca_state.zoomerType == settings.MAG_ZOOMER_TYPE_CUSTOM:
                    if self._targetDisplayBounds.x1 > self._sourceDisplayBounds.x1:
                        left = size
                    if self._targetDisplayBounds.x2 < self._sourceDisplayBounds.x2:
                        right = size
                    if self._targetDisplayBounds.y1 > self._sourceDisplayBounds.y1:
                        top = size
                    if self._targetDisplayBounds.y2 < self._sourceDisplayBounds.y2:
                        bottom = size
                    
                bonobo.pbclient_set_long(self._zoomerPBag, "border-size-left", left)
                bonobo.pbclient_set_long(self._zoomerPBag, "border-size-top", top)
                bonobo.pbclient_set_long(self._zoomerPBag, "border-size-right", right)
                bonobo.pbclient_set_long(self._zoomerPBag, "border-size-bottom", bottom)
            except:
                bonobo.pbclient_set_long(self._zoomerPBag, "border-size", size)
        else:
            bonobo.pbclient_set_long(self._zoomerPBag, magProperty, size)
    
        if updateScreen:
            self._zoomer.markDirty(self._roi)
    
    def setZoomerObjectColor(self, magProperty, colorSetting, updateScreen=True):
        """Sets the specified zoomer property to the specified color.
    
        Arguments:
        - magProperty:  The property to set (as a string)
        - colorSetting: The Orca color setting to apply
        - updateScreen:  Whether or not to update the screen
        """
    
        if not self._initialized:
            return
    
        colorPreference = gtk.gdk.color_parse(colorSetting)
    
        # Convert the colorPreference string to something we can use.
        # The main issue here is that the color preferences are saved
        # as 4 byte values per color.  We only need 2 bytes, so we
        # get rid of the bottom 8 bits.
        #
        colorPreference.red   = colorPreference.red   >> 8
        colorPreference.blue  = colorPreference.blue  >> 8
        colorPreference.green = colorPreference.green >> 8
        colorString = "0x%02X%02X%02X" \
                      % (colorPreference.red,
                         colorPreference.green,
                         colorPreference.blue)
    
        toChange = self._zoomerPBag.getValue(magProperty)
        self._zoomerPBag.setValue(magProperty,
                             ORBit.CORBA.Any(toChange.typecode(),
                                             long(colorString, 0)))
        if updateScreen:
            self._zoomer.markDirty(self._roi)
    
    def setMagnifierObjectColor(self, magProperty, colorSetting, updateScreen=True):
        """Sets the specified magnifier property to the specified color.
    
        Arguments:
        - magProperty:  The property to set (as a string)
        - colorSetting: The Orca color setting to apply
        - updateScreen:  Whether or not to update the screen
        """
    
        if not self._initialized:
            return
    
        colorPreference = gtk.gdk.color_parse(colorSetting)
    
        # Convert the colorPreference string to something we can use.
        # The main issue here is that the color preferences are saved
        # as 4 byte values per color.  We only need 2 bytes, so we
        # get rid of the bottom 8 bits.
        #
        colorPreference.red   = colorPreference.red   >> 8
        colorPreference.blue  = colorPreference.blue  >> 8
        colorPreference.green = colorPreference.green >> 8
        colorString = "0x%02X%02X%02X" \
                      % (colorPreference.red,
                         colorPreference.green,
                         colorPreference.blue)
    
        toChange = self._magnifierPBag.getValue(magProperty)
        self._magnifierPBag.setValue(magProperty,
                                ORBit.CORBA.Any(toChange.typecode(),
                                                long(colorString, 0)))
        if updateScreen:
            self._zoomer.markDirty(self._roi)
    
    def setZoomerMagFactor(self, x, y, updateScreen=True):
        """Sets the magnification level.
    
        Arguments:
        - x: The horizontal magnification level
        - y: The vertical magnification level
        - updateScreen:  Whether or not to update the screen
        """
    
        if not self._initialized:
            return
    
        [oldX, oldY] = self._zoomer.getMagFactor()
    
        self._zoomer.setMagFactor(x, y)
    
        if updateScreen:
            self.__updateROIDimensions()
            if (oldX > x) and (x < 1.5):
                self._minROIX = self._sourceDisplayBounds.x1
                self._minROIY = self._sourceDisplayBounds.y1
                self.__setROI(GNOME.Magnifier.RectBounds(self._minROIX,
                                                    self._minROIY,
                                                    self._minROIX + self._roiWidth,
                                                    self._minROIY + self._roiHeight))
            else:
                extents = orca_state.locusOfFocus.queryComponent().getExtents(0)
                self.__setROICenter(extents.x, extents.y)
    
    def setZoomerSmoothingType(self, smoothingType, updateScreen=True):
        """Sets the zoomer's smoothing type.
    
        Arguments:
        - smoothingType: The type of smoothing to use
        - updateScreen:  Whether or not to update the screen
        """
    
        if not self._initialized:
            return
    
        if smoothingType == settings.MAG_SMOOTHING_MODE_BILINEAR:
            string = "bilinear"
        else:
            string = "None"
    
        try:
            bonobo.pbclient_set_string(self._zoomerPBag, "smoothing-type", string)
        except:
            pass
    
        if updateScreen:
            self._zoomer.markDirty(self._roi)
    
    def setZoomerColorFilter(self, colorFilter, updateScreen=True):
        """Sets the zoomer's color filter.
    
        Arguments:
        - colorFilter: The color filter to apply
        - updateScreen:  Whether or not to update the screen
        """
    
        if not self._initialized or not self.isFilteringCapable():
            return
    
        if colorFilter == settings.MAG_COLOR_FILTERING_MODE_SATURATE_RED:
            toApply = self._zoomer.COLORBLIND_FILTER_T_SELECTIVE_SATURATE_RED
        elif colorFilter == settings.MAG_COLOR_FILTERING_MODE_SATURATE_GREEN:
            toApply = self._zoomer.COLORBLIND_FILTER_T_SELECTIVE_SATURATE_GREEN
        elif colorFilter == settings.MAG_COLOR_FILTERING_MODE_SATURATE_BLUE:
            toApply = self._zoomer.COLORBLIND_FILTER_T_SELECTIVE_SATURATE_BLUE
        elif colorFilter == settings.MAG_COLOR_FILTERING_MODE_DESATURATE_RED:
            toApply = self._zoomer.COLORBLIND_FILTER_T_SELECTIVE_DESSATURATE_RED
        elif colorFilter == settings.MAG_COLOR_FILTERING_MODE_DESATURATE_GREEN:
            toApply = self._zoomer.COLORBLIND_FILTER_T_SELECTIVE_DESSATURATE_GREEN
        elif colorFilter == settings.MAG_COLOR_FILTERING_MODE_DESATURATE_BLUE:
            toApply = self._zoomer.COLORBLIND_FILTER_T_SELECTIVE_DESSATURATE_BLUE
        elif colorFilter == settings.MAG_COLOR_FILTERING_MODE_NEGATIVE_HUE_SHIFT:
            toApply = self._zoomer.COLORBLIND_FILTER_T_HUE_SHIFT_NEGATIVE
        elif colorFilter == settings.MAG_COLOR_FILTERING_MODE_POSITIVE_HUE_SHIFT:
            toApply = self._zoomer.COLORBLIND_FILTER_T_HUE_SHIFT_POSITIVE
        else:
            toApply = self._zoomer.COLORBLIND_FILTER_T_NO_FILTER
    
        colorFilter = self._zoomerPBag.getValue("color-blind-filter")
        self._zoomerPBag.setValue(
             "color-blind-filter",
             ORBit.CORBA.Any(
                 colorFilter.typecode(),
                 toApply))
    
        if updateScreen:
            self._zoomer.markDirty(self._roi)
    
    def hideSystemPointer(self, hidePointer):
        """Hide or show the system pointer.
    
        Arguments:
        -hidePointer: If True, hide the system pointer, otherwise show it.
        """
    
        # Depends upon new functionality in gnome-mag, so just catch the
        # exception if this functionality isn't there.
        #
        try:
            if hidePointer:
                self._magnifier.hideCursor()
            else:
                self._magnifier.showCursor()
        except:
            debug.printException(debug.LEVEL_FINEST)
    
    def isFullScreenCapable(self):
        """Returns True if we are capable of doing full screen (i.e. whether
        composite is being used.
        """
    
        try:
            capable = self._magnifier.fullScreenCapable()
        except:
            capable = False
    
        return capable
    
    def isFilteringCapable(self):
        """Returns True if we're able to take advantage of libcolorblind's color
        filtering.
        """
    
        try:
            capable = self._magnifier.supportColorblindFilters()
        except:
            capable = False
    
        return capable
    
    def updateMouseTracking(self, newMode):
        """Updates the mouse tracking mode.
    
        Arguments:
        -newMode: The new mode to use.
        """
    
        self._mouseTracking = newMode
    
    def updateControlTracking(self, newMode):
        """Updates the control tracking mode.
    
        Arguments:
        -newMode: The new mode to use.
        """
    
        self._controlTracking = newMode
    
    def updateTextTracking(self, newMode):
        """Updates the text tracking mode.
    
        Arguments:
        -newMode: The new mode to use.
        """
    
        self._textTracking = newMode
    
    def updateEdgeMargin(self, amount):
        """Updates the edge margin
    
        Arguments:
        -amount: The new margin to use, in pixels.
        """
    
        self._edgeMargin = amount
    
    def updatePointerFollowsFocus(self, enabled):
        """Updates the pointer follows focus setting.
    
        Arguments:
        -enabled: whether or not pointer follows focus should be enabled.
        """
    
        self._pointerFollowsFocus = enabled
    
    def updatePointerFollowsZoomer(self, enabled):
        """Updates the pointer follows zoomer setting.
    
        Arguments:
        -enabled: whether or not pointer follows zoomer should be enabled.
        """
    
        self._pointerFollowsZoomer = enabled
    
    def finishLiveUpdating(self):
        """Restores things that were altered via a live update."""
    
        self._liveUpdatingMagnifier = False
        self._mouseTracking = _settingsManager.getSetting('magMouseTrackingMode')
        self._controlTracking = _settingsManager.getSetting('magControlTrackingMode')
        self._textTracking = _settingsManager.getSetting('magTextTrackingMode')
        self._edgeMargin = _settingsManager.getSetting('magEdgeMargin')
        self._pointerFollowsFocus = _settingsManager.getSetting('magPointerFollowsFocus')
        self._pointerFollowsZoomer = \
            _settingsManager.getSetting('magPointerFollowsZoomer')
    
        if _settingsManager.getSetting('enableMagnifier'):
            self.setupMagnifier(_settingsManager.getSetting('magZoomerType'))
            self.init()
        else:
            self.shutdown()
    
    ######################################################################
    #                                                                    #
    #                        Input Event Handlers                        #
    #                                                                    #
    ######################################################################
    
    def toggleColorEnhancements(self, script=None, inputEvent=None):
        """Toggles the color enhancements on/off."""
    
        if not self._initialized:
            return
    
        # We don't want to stomp on a command-altered magnification level.
        #
        [levelX, levelY] = self._zoomer.getMagFactor()
        
        normal = {'enableMagZoomerColorInversion': False,
                  'magBrightnessLevelRed': 0,
                  'magBrightnessLevelGreen': 0,
                  'magBrightnessLevelBlue': 0,
                  'magContrastLevelRed': 0,
                  'magContrastLevelGreen': 0,
                  'magContrastLevelBlue': 0,
                  'magColorFilteringMode': settings.MAG_COLOR_FILTERING_MODE_NONE,
                  'magSmoothingMode': settings.MAG_SMOOTHING_MODE_BILINEAR,
                  'magZoomerBorderColor': '#000000',
                  'magZoomFactor': levelX}
    
        if orca_state.colorEnhancementsEnabled:
            self.__setupZoomer(restore = normal)
            # Translators: "color enhancements" are changes users can
            # make to the appearance of the screen to make things easier
            # to see, such as inverting the colors or applying a tint.
            #
            orca_state.activeScript.presentMessage(
                _("Color enhancements disabled."))
        else:
            toRestore = {'magZoomFactor': levelX}
            self.__setupZoomer(restore = toRestore)
            # Translators: "color enhancements" are changes users can
            # make to the appearance of the screen to make things easier
            # to see, such as inverting the colors or applying a tint.
            #
            orca_state.activeScript.presentMessage(_("Color enhancements enabled."))
    
        orca_state.colorEnhancementsEnabled = \
                                        not orca_state.colorEnhancementsEnabled
    
        return True
    
    def toggleMouseEnhancements(self, script=None, inputEvent=None):
        """Toggles the mouse enhancements on/off."""
    
        if not self._initialized:
            return
    
        if orca_state.mouseEnhancementsEnabled:
            self.setMagnifierCrossHair(False, False)
            self.setMagnifierObjectColor("cursor-color", "#000000", False)
            self.setMagnifierCursor(True, False, 0)
            # Translators: "mouse enhancements" are changes users can
            # make to the appearance of the mouse pointer to make it
            # easier to see, such as increasing its size, changing its
            # color, and surrounding it with crosshairs.
            #
            orca_state.activeScript.presentMessage(
                _("Mouse enhancements disabled."))
        else:
            # We normally toggle "on" what the user has enabled by default.
            # However, if the user's default settings are to disable all mouse
            # enhancements "on" and "off" are the same thing.  If that is the
            # case and this command is being used, the user probably expects
            # to see *something* change. We don't know what, so enable both
            # the cursor and the cross-hairs.
            #
            cursorEnable = _settingsManager.getSetting('enableMagCursor')
            crossHairEnable = _settingsManager.getSetting('enableMagCrossHair')
            if not (cursorEnable or crossHairEnable):
                cursorEnable = True
                crossHairEnable = True
    
            self.setMagnifierCursor(
                cursorEnable,
                _settingsManager.getSetting('enableMagCursorExplicitSize'),
                _settingsManager.getSetting('magCursorSize'),
                False)
            self.setMagnifierObjectColor(
                "cursor-color",
                _settingsManager.getSetting('magCursorColor'),
                False)
            self.setMagnifierObjectColor(
                "crosswire-color",
                _settingsManager.getSetting('magCrossHairColor'),
                False)
            self.setMagnifierCrossHairClip(
                _settingsManager.getSetting('enableMagCrossHairClip'),
                False)
            self.setMagnifierCrossHair(crossHairEnable)
            # Translators: "mouse enhancements" are changes users can
            # make to the appearance of the mouse pointer to make it
            # easier to see, such as increasing its size, changing its
            # color, and surrounding it with crosshairs.
            #
            orca_state.activeScript.presentMessage(_("Mouse enhancements enabled."))
    
        orca_state.mouseEnhancementsEnabled = \
                                        not orca_state.mouseEnhancementsEnabled
        return True
    
    def increaseMagnification(self, script=None, inputEvent=None):
        """Increases the magnification level."""
    
        if not self._initialized:
            return
    
        [levelX, levelY] = self._zoomer.getMagFactor()
    
        # Move in increments that are sensible based on the current level of
        # magnification.
        #
        if 1 <= levelX < 4:
            increment = 0.25
        elif 4 <= levelX < 7:
            increment = 0.5
        else:
            increment = 1
    
        newLevel = levelX + increment
        if newLevel <= 16:
            self.setZoomerMagFactor(newLevel, newLevel)
            orca_state.activeScript.presentMessage(str(newLevel))
    
        return True
    
    def decreaseMagnification(self, script=None, inputEvent=None):
        """Decreases the magnification level."""
    
        if not self._initialized:
            return
    
        [levelX, levelY] = self._zoomer.getMagFactor()
    
        # Move in increments that are sensible based on the current level of
        # magnification.
        #
        if 1 <= levelX < 4:
            increment = 0.25
        elif 4 <= levelX < 7:
            increment = 0.5
        else:
            increment = 1
    
        newLevel = levelX - increment
        if newLevel >= 1:
            self.setZoomerMagFactor(newLevel, newLevel)
            orca_state.activeScript.presentMessage(str(newLevel))
    
        return True
    
    def toggleMagnifier(self, script=None, inputEvent=None):
        """Toggles the magnifier."""
    
        if not self._initialized:
            self.init()
            # Translators: this is the message spoken when a user enables the
            # magnifier.  In addition to screen magnification, the user's
            # preferred colors and mouse customizations are loaded.
            #
            orca_state.activeScript.presentMessage(_("Magnifier enabled."))
        else:
            self.shutdown()
            # Translators: this is the message spoken when a user disables the
            # magnifier, restoring the screen contents to their normal colors
            # and sizes.
            #
            orca_state.activeScript.presentMessage(_("Magnifier disabled."))
    
        return True
    
    def cycleZoomerType(self, script=None, inputEvent=None):
        """Allows the user to cycle through the available zoomer types."""
    
        if not self._initialized:
            return
    
        # There are 6 possible zoomer types
        #
        orca_state.zoomerType += 1
    
        if orca_state.zoomerType >= 6:
            orca_state.zoomerType = 0
    
        if orca_state.zoomerType == settings.MAG_ZOOMER_TYPE_FULL_SCREEN \
           and not self._fullScreenCapable:
            orca_state.zoomerType += 1
    
        # We don't want to stomp on any command-altered settings
        #
        toRestore = {}
    
        [levelX, levelY] = self._zoomer.getMagFactor()
        if levelX != _settingsManager.getSetting('magZoomFactor'):
            toRestore['magZoomFactor'] = levelX
    
        if not orca_state.colorEnhancementsEnabled:
            toRestore.update(\
                {'enableMagZoomerColorInversion': False,
                 'magBrightnessLevelRed': 0,
                 'magBrightnessLevelGreen': 0,
                 'magBrightnessLevelBlue': 0,
                 'magContrastLevelRed': 0,
                 'magContrastLevelGreen': 0,
                 'magContrastLevelBlue': 0,
                 'magColorFilteringMode': settings.MAG_COLOR_FILTERING_MODE_NONE,
                 'magSmoothingMode': settings.MAG_SMOOTHING_MODE_BILINEAR,
                 'magZoomerBorderColor': '#000000'})
    
        self.setupMagnifier(orca_state.zoomerType, restore = toRestore)
    
        if not orca_state.mouseEnhancementsEnabled:
            self.setMagnifierCrossHair(False)
            self.setMagnifierObjectColor("cursor-color",
                                    _settingsManager.getSetting('magCursorColor'),
                                    False)
            self.setMagnifierCursor(False, False, 0)
    
        if orca_state.zoomerType == settings.MAG_ZOOMER_TYPE_FULL_SCREEN:
            if self._fullScreenCapable:
                # Translators: magnification will use the full screen.
                #
                zoomerType = _("Full Screen")
            else:
                # Translators: the user attempted to switch to full screen
                # magnification, but his/her system doesn't support it.
                #
                zoomerType = _("Full Screen mode unavailable")
        elif orca_state.zoomerType == settings.MAG_ZOOMER_TYPE_TOP_HALF:
            # Translators: magnification will use the top half of the screen.
            #
            zoomerType = _("Top Half")
        elif orca_state.zoomerType == settings.MAG_ZOOMER_TYPE_BOTTOM_HALF:
            # Translators: magnification will use the bottom half of the screen.
            #
            zoomerType = _("Bottom Half")
        elif orca_state.zoomerType == settings.MAG_ZOOMER_TYPE_LEFT_HALF:
            # Translators: magnification will use the left half of the screen.
            #
            zoomerType = _("Left Half")
        elif orca_state.zoomerType == settings.MAG_ZOOMER_TYPE_RIGHT_HALF:
            # Translators: magnification will use the right half of the screen.
            #
            zoomerType = _("Right Half")
        elif orca_state.zoomerType == settings.MAG_ZOOMER_TYPE_CUSTOM:
            # Translators: the user has selected a custom area of the screen
            # to use for magnification.
            #
            zoomerType = _("Custom")
        else:
            # This shouldn't happen, but just in case....
            zoomerType = ""
    
        orca_state.activeScript.presentMessage(zoomerType)
        
        return True       
    
    def disable(self):
        settings.enableMagnifier = False
        self.isActive = False
        self.shutdown()

IPlugin.register(magPlugin)
