# gnome-terminal script

import a11y
import speech

def onTextInserted (e):
    if e.source.role != "terminal":
        return
    speech.say ("default", e.any_data)

    
def onTextDeleted (event):
    """Called whenever text is deleted from an object.

    Arguments:
    - event: the Event
    """
    
    # Ignore text deletions from non-focused objects, unless the
    # currently focused object is the parent of the object from which
    # text was deleted
    #
    if (event.source != a11y.focusedObject) \
            and (event.source.parent != a11y.focusedObject):
        pass
    else:
        brlUpdateText (event.source)
