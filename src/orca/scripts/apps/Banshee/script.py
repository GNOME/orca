import orca.default as default
import orca.orca_state as orca_state
import pyatspi

from speech_generator import SpeechGenerator
from formatting import Formatting

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """
        default.Script.__init__(self, app)
        self._last_seek_value = 0


    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """
        return SpeechGenerator(self)

    def getFormatting(self):
        """Returns the formatting strings for this script."""
        return Formatting(self)

    def _formatDuration(self, s):
        seconds = '%02d' % (s%60)
        minutes = '%02d' % (s/60)
        hours = '%02d' % (s/3600)
        
        duration = [minutes, seconds]
        
        if hours != '00':
            duration.insert(0, hours)

        return ':'.join(duration)

    def _isSeekSlider(self, obj):
        return bool(pyatspi.findAncestor(
                obj, lambda x: x.getRole() == pyatspi.ROLE_TOOL_BAR))

    def visualAppearanceChanged(self, event, obj):
        if event.type == 'object:property-change:accessible-value' and \
                self._isSeekSlider(obj):
            try:
                value = obj.queryValue()
            except NotImplementedError:
                return default.Script.getTextForValue(self, obj)

            current_value = int(value.currentValue)/1000

            if current_value in \
                    range(self._last_seek_value, self._last_seek_value + 4):
                if self.isSameObject(obj, orca_state.locusOfFocus):
                    self.updateBraille(obj)
                return

            self._last_seek_value = current_value

        default.Script.visualAppearanceChanged(self, event, obj)
            

    def getTextForValue(self, obj):
        if not self._isSeekSlider(obj):
            return default.Script.getTextForValue(self, obj)

        try:
            value = obj.queryValue()
        except NotImplementedError:
            return default.Script.getTextForValue(self, obj)
        else:
            return self._formatDuration(int(value.currentValue)/1000)
