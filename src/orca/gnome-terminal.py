# gnome-terminal script

import a11y
import speech

def onTextInserted (e):
    if e.source.role != "terminal":
        return
    speech.say ("default", e.any_data)
    
