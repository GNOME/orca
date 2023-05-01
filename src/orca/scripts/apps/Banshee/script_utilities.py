import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

import orca.script_utilities as script_utilities
from orca.ax_object import AXObject


class Utilities(script_utilities.Utilities):

    def __init__(self, script):
        """Creates an instance of the Utilities class.

        Arguments:
        - script: the script with which this instance is associated.
        """

        script_utilities.Utilities.__init__(self, script)

    def _formatDuration(self, s):
        seconds = '%02d' % (s%60)
        minutes = '%02d' % (s/60)
        hours = '%02d' % (s/3600)
        
        duration = [minutes, seconds]
        
        if hours != '00':
            duration.insert(0, hours)

        return ':'.join(duration)

    def isSeekSlider(self, obj):
        return bool(AXObject.find_ancestor(
                obj, lambda x: Atspi.Accessible.get_role(x) == Atspi.Role.TOOL_BAR))

    def textForValue(self, obj):
        if not self.isSeekSlider(obj):
            return script_utilities.Utilities.textForValue(self, obj)

        try:
            value = obj.queryValue()
        except NotImplementedError:
            return script_utilities.Utilities.textForValue(self, obj)
        else:
            return self._formatDuration(int(value.currentValue)/1000)
