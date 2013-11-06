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

    def onValueChanged(self, event):
        obj = event.source
        if self.utilities.isSeekSlider(obj):
            value = obj.queryValue()
            current_value = int(value.currentValue)/1000
            if current_value in \
                    range(self._last_seek_value, self._last_seek_value + 4):
                if self.utilities.isSameObject(obj, orca_state.locusOfFocus):
                    self.updateBraille(obj)
                return

            self._last_seek_value = current_value

        default.Script.onValueChanged(self, event)

