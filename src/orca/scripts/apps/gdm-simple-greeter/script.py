"""Custom script for gdm-simple-greeter"""
import orca.scripts.default as default

class Script(default.Script):
    def __init__(self, app):
        """Creates a new script for the given application

        Arguments:
        - app: the application to create the script for
        """
        default.Script.__init__(self, app)

    def stopSpeechOnActiveDescendantChanged(self, event):
        return False
