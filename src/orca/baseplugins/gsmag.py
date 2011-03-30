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

"""Plugin that implements the GNOME Shell magnifier"""

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
 
import time

class gsMagPlugin(IPlugin, IPresenter, ICommand):
    name = 'GNOME Shell Magnifier'
    description = 'Enable the GNOME Shell magnifier to mag screen' 
    version = '0.9'
    authors = ['J. Ignacio Alvarez <jialvarez@emergya.es>']
    website = 'http://www.emergya.es'
    icon = 'gtk-missing-image'

    def __init__(self):
        pass

    def enable(self):
        print 'GNOME Shell Magnifier plugin started'

        import dbus
        self._bus = dbus.SessionBus()
        _proxy_obj = self._bus.get_object("org.gnome.Magnifier",
                                     "/org/gnome/Magnifier")
        self._magnifier = dbus.Interface(_proxy_obj, "org.gnome.Magnifier")
        self._zoomer = None
       
        global orca
        global debug
        global eventsynthesizer
        global settings
        global orca_state
        global gconf
        global _

        import orca.orca as orca
        import orca.debug as debug
        import orca.eventsynthesizer as eventsynthesizer
        import orca.settings as settings
        import orca.orca_state as orca_state
        import gconf
        
        from orca.orca_i18n import _
        
        # Some GConf settings that gs-mag uses
        #
        global A11Y_MAG_PREFS_DIR
        global MOUSE_MODE_KEY
        global GS_MAG_NONE
        global GS_MAG_CENTERED
        global GS_MAG_PUSH
        global GS_MAG_PROPORTIONAL
        global CROSSHAIRS_SHOW_KEY

        A11Y_MAG_PREFS_DIR  = "/desktop/gnome/accessibility/magnifier"
        MOUSE_MODE_KEY      = A11Y_MAG_PREFS_DIR + "/mouse_tracking"
        GS_MAG_NONE         = 0
        GS_MAG_CENTERED     = 1
        GS_MAG_PUSH         = 2
        GS_MAG_PROPORTIONAL = 3
        CROSSHAIRS_SHOW_KEY = A11Y_MAG_PREFS_DIR + "/show_cross_hairs"
        
        self._gconfClient = gconf.client_get_default()
        
        # If True, the magnifier is active
        #
        self._isActive = False
        
        # Whether or not we're in the process of making "live update" changes
        # to the location of the magnifier.
        #
        self._liveUpdatingMagnifier = False
        
        # The current modes of tracking, for use with "live update" changes.
        #
        self._controlTracking = None
        self._edgeMargin = None
        self._mouseTracking = None
        self._pointerFollowsZoomer = None
        self._pointerFollowsFocus = None
        self._textTracking = None
       
        global gtk
        import gtk
        _display = gtk.gdk.display_get_default()
        _screen = _display.get_default_screen()
        self._screenWidth = _screen.get_width()
        self._screenHeight = _screen.get_height()
        
        # If True, this module has been initialized.
        #
        self._initialized = False
        self._fullScreenCapable = False
        self._wasActiveOnInit = False
        self._crossHairsShownOnInit = False
        
        # The width and height, in unzoomed system coordinates of the rectangle that,
        # when magnified, will fill the viewport of the magnifier - this needs to be
        # sync'd with the magnification factors of the zoom area.
        #
        self._roiWidth = 0
        self._roiHeight = 0
        
        # The current region of interest as specified by the upper left corner.
        #
        _roi = None
        
        # Minimum/maximum values for the center of the ROI
        # in source screen coordinates.
        #
        self._minROIX = 0
        self._maxROIX = 0
        self._minROIY = 0
        self._maxROIY = 0

        _settingsManager = getattr(orca, '_settingsManager')

        plugins = _settingsManager.getPlugins(_settingsManager.getSetting('activeProfile')[1])
        print 'estoy en el enable del gsmag y plugins = ', plugins

        self.isActive = plugins['gsmag']['active']

        settings.enableMagnifier = True
        self.shutdown()
        self.init()

    ########################################################################
    #                                                                      #
    # Methods for magnifying objects                                       #
    #                                                                      #
    ########################################################################
    
    def _setROICenter(self, x, y):
        """Centers the region of interest around the given point.
    
        Arguments:
        - x: integer in unzoomed system coordinates representing x component
        - y: integer in unzoomed system coordinates representing y component
        """
        self._zoomer.shiftContentsTo(x, y)
    
    def _setROICursorPush(self, x, y, width, height, edgeMargin = 0):
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
        # [[[WDW - probably should not make a D-Bus call each time.]]]
        #
        edgeMargin = min(edgeMargin, 50)/100.00
        edgeMarginX = edgeMargin * self._screenWidth/settings.magZoomFactor
        edgeMarginY = edgeMargin * self._screenHeight/settings.magZoomFactor
    
        # Determine if the accessible is partially to the left, right,
        # above, or below the current region of interest (ROI).
        # [[[WDW - probably should not make a D-Bus call each time.]]]
        #
        [roiLeft, roiTop, roiRight, roiBottom] = self._zoomer.getRoi()
        roiWidth = roiRight - roiLeft
        roiHeight = roiBottom - roiTop
        leftOfROI = (x - edgeMarginX) <= roiLeft
        rightOfROI = (x + width + edgeMarginX) >= (roiLeft + roiWidth)
        aboveROI = (y - edgeMarginY)  <= roiTop
        belowROI = (y + height + edgeMarginY) >= (roiTop + roiHeight)
    
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
        x1 = roiLeft
        x2 = roiLeft + roiWidth
        y1 = roiTop
        y2 = roiTop + roiHeight
    
        if leftOfROI:
            x1 = max(0, x - edgeMarginX)
            x2 = x1 + roiWidth
        elif rightOfROI:
            x = min(self._screenWidth, x + edgeMarginX)
            if width > roiWidth:
                x1 = x
                x2 = x1 + roiWidth
            else:
                x2 = x + width
                x1 = x2 - roiWidth
    
        if aboveROI:
            y1 = max(0, y - edgeMarginY)
            y2 = y1 + roiHeight
        elif belowROI:
            y = min(self._screenHeight, y + edgeMarginY)
            if height > roiHeight:
                y1 = y
                y2 = y1 + roiHeight
            else:
                y2 = y + height
                y1 = y2 - roiHeight
    
        self._setROICenter((x1 + x2) / 2, (y1 + y2) / 2)
    
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
                    self._setROICenter(x, y)
                elif self._textTracking == settings.MAG_TRACKING_MODE_PUSH:
                    self._setROICursorPush(x, y, width, height, self._edgeMargin)
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
                _lastMouseEventWasRoute = True
                eventsynthesizer.generateMouseEvent(x, y + height - 1, "abs")
    
            if self._controlTracking == settings.MAG_TRACKING_MODE_CENTERED:
                centerX = x + width/2
                centerY = y + height/2
    
                # Be sure that the upper-left corner of the object will still
                # be visible on the screen.
                # [[[WDW - probably should not make a getRoi call each time]]]
                #
                [roiLeft, roiTop, roiRight, roiBottom] = self._zoomer.getRoi()
                roiWidth = roiRight - roiLeft
                roiHeight = roiBottom - roiTop
                if width > roiWidth:
                    centerX = x
                if height > roiHeight:
                    centerY = y
    
                self._setROICenter(centerX, centerY)
            elif self._controlTracking == settings.MAG_TRACKING_MODE_PUSH:
                self._setROICursorPush(x, y, width, height)
    
    ########################################################################
    #                                                                      #
    # Methods for updating live tracking settings                          #
    #                                                                      #
    ########################################################################
    
    def updateControlTracking(self, newMode):
        """Updates the control tracking mode.
    
        Arguments:
        -newMode: The new mode to use.
        """
        self._controlTracking = newMode
        
    def updateEdgeMargin(self, amount):
        """Updates the edge margin
    
        Arguments:
        -amount: The new margin to use, in pixels.
        """
        self._edgeMargin = amount
    
    def updateMouseTracking(self, newMode):
        """Updates the mouse tracking mode.
    
        Arguments:
        -newMode: The new mode to use.
        """
        self._mouseTracking = newMode
    
        # Comparing Orca and GS-mag, modes are the same, but different values:
        # Orca:  centered=0, proportional=1, push=2, none=3
        # GS-mag: none=0, centered=1, push=2, proportional=3
        # Use Orca's values as index into following array (hack).
        #
        gsMagModes = \
            [GS_MAG_CENTERED, GS_MAG_PROPORTIONAL, GS_MAG_PUSH, GS_MAG_NONE]
        self._gconfClient.set_int(MOUSE_MODE_KEY, gsMagModes[newMode])
    
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
    
    def updateTextTracking(self, newMode):
        """Updates the text tracking mode.
    
        Arguments:
        -newMode: The new mode to use.
        """
        self._textTracking = newMode
    
    def finishLiveUpdating(self):
        """Restores things that were altered via a live update."""
    
        self._liveUpdatingMagnifier = False
        self._mouseTracking = settings.magMouseTrackingMode
        self._controlTracking = settings.magControlTrackingMode
        self._textTracking = settings.magTextTrackingMode
        self._edgeMargin = settings.magEdgeMargin
        self._pointerFollowsFocus = settings.magPointerFollowsFocus
        self._pointerFollowsZoomer = settings.magPointerFollowsZoomer
    
        if settings.enableMagnifier:
            self.setupMagnifier(settings.magZoomerType)
            self.init()
        else:
            self.shutdown()
    
    ########################################################################
    #                                                                      #
    # Methods for updating appearance settings                             #
    #                                                                      #
    ########################################################################
    
    def applySettings(self):
        """Looks at the user settings and applies them to the magnifier."""
        self.__setupMagnifier(settings.magZoomerType)
        self.__setupZoomer(settings.magZoomerType)
    
        self._mouseTracking = settings.magMouseTrackingMode
        self._controlTracking = settings.magControlTrackingMode
        self._textTracking = settings.magTextTrackingMode
        self._edgeMargin = settings.magEdgeMargin
        self._pointerFollowsZoomer = settings.magPointerFollowsZoomer
        self._pointerFollowsFocus = settings.magPointerFollowsFocus
    
    def hideSystemPointer(self, hidePointer):
        """Hide or show the system pointer.
    
        Arguments:
        -hidePointer: If True, hide the system pointer, otherwise show it.
        """
        try:
            if hidePointer:
                self._magnifier.hideCursor()
            else:
                self._magnifier.showCursor()
        except:
            debug.printException(debug.LEVEL_FINEST)
    
    def __setupMagnifier(self, position, restore=None):
        """Creates the magnifier in the position specified.
    
        Arguments:
        - position: the position/type of zoomer (full, left half, etc.)
        - restore:  a dictionary of all of the settings which should be restored
        """

        if not restore:
            restore = {}
    
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
        hideCursor = restore.get('magHideCursor', settings.magHideCursor)
        if hideCursor \
           and self._fullScreenCapable \
           and position == settings.MAG_ZOOMER_TYPE_FULL_SCREEN:
            self.hideSystemPointer(True)
        else:
            self.hideSystemPointer(False)
    
        orca_state.zoomerType = position
        updateTarget = True
    
        value = restore.get('magCrossHairColor', settings.magCrossHairColor)
        self.setMagnifierObjectColor("crosswire-color", value, False)
    
        enableCrossHair = restore.get('enableMagCrossHair',
                                      settings.enableMagCrossHair)
        self.setMagnifierCrossHair(enableCrossHair, False)
    
        value = restore.get('enableMagCrossHairClip',
                            settings.enableMagCrossHairClip)
        self.setMagnifierCrossHairClip(value, False)
    
        orca_state.mouseEnhancementsEnabled = enableCrossHair
    
    def __setupZoomer(self, position, left=None, top=None, right=None,
                      bottom=None, restore=None):
        """Creates a zoomer in the magnifier.
        The position of the zoomer onscreen is based on the given arguments.  If
        none are supplied, defaults to the settings for the given zoomer position.
    
        Arguments:
        - position: position of the zoomer view port (top half, left half, custom)
        - left:     left edge of zoomer's viewport (for custom -- optional)
        - top:      top edge of zoomer's viewport (for custom -- optional)
        - right:    right edge of zoomer's viewport (for custom -- optional)
        - bottom:   bottom edge of zoomer's viewport (for custom -- optional)
        - restore:  dictionary of the settings; used for zoom factor (optional)
        """
    
        if not restore:
            restore = {}
    
        # full screen is the default.
        #
        prefLeft = 0
        prefTop = 0
        prefRight = prefLeft + self._screenWidth
        prefBottom = prefTop + self._screenHeight
    
        if position == settings.MAG_ZOOMER_TYPE_TOP_HALF:
            prefBottom = prefTop + self._screenHeight/2
        elif position == settings.MAG_ZOOMER_TYPE_BOTTOM_HALF:
            prefTop = self._screenHeight/2
            prefBottom = prefTop + self._screenHeight/2
        elif position == settings.MAG_ZOOMER_TYPE_LEFT_HALF:
            prefRight = prefLeft + self._screenWidth/2
        elif position == settings.MAG_ZOOMER_TYPE_RIGHT_HALF:
            prefLeft = self._screenWidth/2
            prefRight = prefLeft + self._screenWidth/2
        elif position == settings.MAG_ZOOMER_TYPE_CUSTOM:
            prefLeft = settings.magZoomerLeft if left == None else left
            prefTop = settings.magZoomerTop if top == None else top
            prefRight = settings.magZoomerRight if right == None else right
            prefBottom = settings.magZoomerBottom if bottom == None else bottom
    
        magFactor = restore.get('magZoomFactor', settings.magZoomFactor)
        viewWidth = prefRight - prefLeft
        viewHeight = prefBottom - prefTop
        self._roiWidth = viewWidth / magFactor
        self._roiHeight = viewHeight / magFactor
    
        debug.println(debug.LEVEL_ALL,
                      "Magnifier zoomer ROI size desired: width=%d, height=%d)" \
                      % (self._roiWidth, self._roiHeight))
    
        # If there are zoom regions, use the first one; otherwise create one.
        #
        zoomerPaths = self._magnifier.getZoomRegions()
        if len(zoomerPaths) > 0:
            self._zoomer = self._bus.get_object('org.gnome.Magnifier', zoomerPaths[0])
            self._zoomer.setMagFactor(magFactor, magFactor)
            self._zoomer.moveResize([prefLeft, prefTop, prefRight, prefBottom])
        else:
            zoomerPath = self._magnifier.createZoomRegion(
                magFactor, magFactor,
    	        [0, 0, self._roiWidth, self._roiHeight],
    	        [prefLeft, prefTop, prefRight, prefBottom])
            self._zoomer = self._bus.get_object('org.gnome.Magnifier', zoomerPath)
            self._magnifier.addZoomRegion(zoomerPath)
    
        self.__updateROIDimensions()
    
    def __updateROIDimensions(self):
        """Updates the ROI width, height, and maximum and minimum values.
        """
        roi = self._zoomer.getRoi()
        self._roiWidth = roi[2] - roi[0]
        self._roiHeight = roi[3] - roi[1]
    
        self._minROIX = self._roiWidth / 2
        self._minROIY = self._roiHeight / 2
    
        self._maxROIX = self._screenWidth - (self._roiWidth / 2)
        self._maxROIY = self._screenHeight - (self._roiHeight / 2)
    
        debug.println(debug.LEVEL_ALL,
                      "Magnifier ROI min/max center: (%d, %d), (%d, %d)" \
                      % (self._minROIX, self._minROIY, self._maxROIX, self._maxROIY))
    
    def setupMagnifier(self, position, left=None, top=None, right=None,
                       bottom=None, restore=None):
        """Creates the magnifier in the position specified.
    
        Arguments:
        - position: the position/type of zoomer (full, left half, etc.)
        - left:     the left edge of the zoomer (only applicable for custom)
        - top:      the top edge of the zoomer (only applicable for custom)
        - right:    the right edge of the zoomer (only applicable for custom)
        - bottom:   the top edge of the zoomer (only applicable for custom)
        - restore:  a dictionary of all of the settings that should be restored
        """
        self._liveUpdatingMagnifier = True
        self.__setupMagnifier(position, restore)
        self.__setupZoomer(position, left, top, right, bottom, restore)
    
    def setMagnifierCursor(self, enabled, customEnabled, size, updateScreen=True):
        """Sets the cursor.
    
        Arguments:
        - enabled:        Whether or not the cursor should be enabled
        - customEnabled:  Whether or not a custom size has been enabled
        - size:           The size it should be set to
        - updateScreen:   Whether or not to update the screen
        """
        # [[[WDW - To be implemented]]]
        pass
    
    def setMagnifierCrossHair(self, enabled, updateScreen=True):
        """Sets the cross-hair.
    
        Arguments:
        - enabled: Whether or not the cross-hair should be enabled
        - updateScreen:  Whether or not to update the screen.
        """
    
        if not self._initialized:
            return
    
        size = 0
        if enabled:
            size = settings.magCrossHairSize
    
        self._magnifier.setCrosswireSize(size)
        self._gconfClient.set_bool(CROSSHAIRS_SHOW_KEY, enabled)
    
    def setMagnifierCrossHairClip(self, enabled, updateScreen=True):
        """Sets the cross-hair clip.
    
        Arguments:
        - enabled: Whether or not the cross-hair clip should be enabled
        - updateScreen:   Whether or not to update the screen (ignored)
        """
    
        if not self._initialized:
            return
    
        self._magnifier.setCrosswireClip(enabled)
    
    def setMagnifierObjectColor(self, magProperty, colorSetting, updateScreen=True):
        """Sets the specified zoomer property to the specified color.
    
        Arguments:
        - magProperty:  The property to set (as a string).  Only 'crosswire-color'.
        - colorSetting: The Orca color setting to apply
        - updateScreen:  Whether or not to update the screen
        """
    
        colorPreference = gtk.gdk.color_parse(colorSetting)
        # Convert the colorPreference string to something we can use.
        # The main issue here is that the color preferences are saved
        # as 4 byte values per color.  We only need 2 bytes, so we
        # get rid of the bottom 8 bits.  Default 'ff' for alpha.
        #
        colorPreference.red   = colorPreference.red   >> 8
        colorPreference.blue  = colorPreference.blue  >> 8
        colorPreference.green = colorPreference.green >> 8
        colorString = "0x%02X%02X%02Xff" \
                      % (colorPreference.red,
                         colorPreference.green,
                         colorPreference.blue)
    
        # [[[JS - Handle only 'crosswire-color' for now]]]
        # Shift left 8 bits to put in alpha value.
        if magProperty == 'crosswire-color':
            crossWireColor = int(colorString, 16)
            self._magnifier.setCrosswireColor(crossWireColor & 0xffffffff)
    
        # [[[WDW - To be implemented]]]
        else:
            pass
    
    def setMagnifierObjectSize(self, magProperty, size, updateScreen=True):
        """Sets the specified magnifier property to the specified size.
    
        Arguments:
        - magProperty:   The property to set (as a string)
        - size:          The size to apply
        - updateScreen:  Whether or not to update the screen
        """
    
        # [[[JS - Handle only 'crosswire-size' for now]]]
        if magProperty == 'crosswire-size':
            self._magnifier.setCrosswireSize(size)
    
        # [[[WDW - To be implemented]]]
        else:
            pass
    
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
        # [[[WDW - To be implemented]]]
        pass
    
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
        # [[[WDW - To be implemented]]]
        pass
    
    def setZoomerColorFilter(self, colorFilter, updateScreen=True):
        """Sets the zoomer's color filter.
    
        Arguments:
        - colorFilter: The color filter to apply
        - updateScreen:  Whether or not to update the screen
        """
        # [[[WDW - To be implemented]]]
        pass
    
    def setZoomerColorInversion(self, enabled, updateScreen=True):
        """Sets the color inversion.
    
        Arguments:
        - enabled: Whether or not color inversion should be enabled
        - updateScreen:   Whether or not to update the screen
        """
        # [[[WDW - To be implemented]]]
        pass
    
    def setZoomerMagFactor(self, x, y, updateScreen=True):
        """Sets the magnification level.
    
        Arguments:
        - x: The horizontal magnification level
        - y: The vertical magnification level
        - updateScreen:  Whether or not to update the screen
        """
        self._zoomer.setMagFactor(x, y)
    
    def setZoomerObjectColor(self, magProperty, colorSetting, updateScreen=True):
        """Sets the specified zoomer property to the specified color.
    
        Arguments:
        - magProperty:  The property to set (as a string)
        - colorSetting: The Orca color setting to apply
        - updateScreen:  Whether or not to update the screen
        """
        # [[[WDW - To be implemented]]]
        pass
    
    def setZoomerObjectSize(self, magProperty, size, updateScreen=True):
        """Sets the specified zoomer property to the specified size.
    
        Arguments:
        - magProperty:   The property to set (as a string)
        - size:          The size to apply
        - updateScreen:  Whether or not to update the screen
        """
        # [[[WDW - To be implemented]]]
        pass
    
    def setZoomerSmoothingType(self, smoothingType, updateScreen=True):
        """Sets the zoomer's smoothing type.
    
        Arguments:
        - smoothingType: The type of smoothing to use
        - updateScreen:  Whether or not to update the screen
        """
        # [[[WDW - To be implemented]]]
        pass
    
    ########################################################################
    #                                                                      #
    # Methods for changing settings via keyboard/mouse events              #
    #                                                                      #
    ########################################################################
    
    def cycleZoomerType(self, script=None, inputEvent=None):
        """Allows the user to cycle through the available zoomer types."""
        # [[[WDW - To be implemented]]]
        pass
    
    def decreaseMagnification(self, script=None, inputEvent=None):
        """Decreases the magnification level."""
        # [[[WDW - To be implemented]]]
        pass
    
    def increaseMagnification(self, script=None, inputEvent=None):
        """Increases the magnification level."""
        # [[[WDW - To be implemented]]]
        pass
    
    def toggleColorEnhancements(self, script=None, inputEvent=None):
        """Toggles the color enhancements on/off."""
        # [[[WDW - To be implemented]]]
        pass
    
    def toggleMouseEnhancements(self, script=None, inputEvent=None):
        """Toggles the mouse enhancements on/off."""
        # [[[WDW - To be implemented]]]
        pass
    
    def toggleMagnifier(self, script=None, inputEvent=None):
        """Toggles the magnifier."""
        if not self._magnifier.isActive():
            init()
            # Translators: this is the message spoken when a user enables the
            # magnifier.  In addition to screen magnification, the user's
            # preferred colors and mouse customizations are loaded.
            #
            orca_state.activeScript.presentMessage(_("Magnifier enabled."))
        else:
            shutdown()
            # Translators: this is the message spoken when a user disables the
            # magnifier, restoring the screen contents to their normal colors
            # and sizes.
            #
            orca_state.activeScript.presentMessage(_("Magnifier disabled."))
    
    ########################################################################
    #                                                                      #
    # Methods for obtaining magnifier capabilities                         #
    #                                                                      #
    ########################################################################
    
    def isFilteringCapable(self):
        """Returns True if we're able to take advantage of libcolorblind's color
        filtering.
        """
        # [[[WDW - To be implemented]]]
        return False
    
    def isFullScreenCapable(self):
        """Returns True if we are capable of doing full screen (i.e. whether
        composite is being used.
        """
        return True
    
    ########################################################################
    #                                                                      #
    # Methods for starting and stopping the magnifier                      #
    #                                                                      #
    ########################################################################
    
    def init(self):
        """Initializes the magnifier, bringing the magnifier up on the
        display.
    
        Returns True if the initialization procedure was run or False if this
        module has already been initialized.
        """
        if self._initialized:
            return False
    
        try:
            self._initialized = True
            self._wasActiveOnInit = self._magnifier.isActive()
            self._crossHairsShownOnInit = self._gconfClient.get_bool(CROSSHAIRS_SHOW_KEY)
            self.applySettings()
            self._magnifier.setActive(True)
            self._isActive = self._magnifier.isActive()
            return True
    
        except:
            self._initialized = False
            raise
        
    def shutdown(self):
        """Shuts down the magnifier module.
        Returns True if the shutdown procedure was run or False if this
        module has not been initialized.
        """

        #if not self._initialized:
        #    return False
    
        self._magnifier.setActive(self._wasActiveOnInit)
        self._gconfClient.set_bool(CROSSHAIRS_SHOW_KEY, self._crossHairsShownOnInit)
        self._isActive = self._magnifier.isActive()
        if not self._isActive:
            self.hideSystemPointer(False)
    
        self._initialized = False
        return True

    def disable(self):
        settings.enableMagnifier = False
        self.isActive = False
        self.shutdown()

IPlugin.register(gsMagPlugin)
