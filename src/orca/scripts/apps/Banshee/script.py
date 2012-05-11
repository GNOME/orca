import orca.scripts.default as default
import orca.orca_state as orca_state

from .script_utilities import Utilities
from .speech_generator import SpeechGenerator
from .formatting import Formatting

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

    def getUtilities(self):
        """Returns the utilites for this script."""

        return Utilities(self)

    def visualAppearanceChanged(self, event, obj):
        if event.type == 'object:property-change:accessible-value' and \
                self.utilities.isSeekSlider(obj):
            try:
                value = obj.queryValue()
            except NotImplementedError:
                return default.Script.visualAppearanceChanged(self, event, obj)

            current_value = int(value.currentValue)/1000

            if current_value in \
                    range(self._last_seek_value, self._last_seek_value + 4):
                if self.utilities.isSameObject(obj, orca_state.locusOfFocus):
                    self.updateBraille(obj)
                return

            self._last_seek_value = current_value

        default.Script.visualAppearanceChanged(self, event, obj)

