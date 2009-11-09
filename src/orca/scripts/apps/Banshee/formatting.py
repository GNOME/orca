import copy

import pyatspi

import orca.formatting

formatting = {
    'speech': {
        # When the rating widget changes values, it emits an accessible
        # name changed event. Because it is of ROLE_UNKNOWN, the default
        # speech_generator's _getDefaultSpeech handles it. And because
        # the widget is already focused, it doesn't speak anything. We
        # want to speak the widget's name as it contains the number of
        # stars being displayed.
        #
        'REAL_ROLE_TABLE_CELL': {
            'unfocused': '(tableCell2ChildLabel + tableCell2ChildToggle)\
                          or (columnHeaderIfToggleAndNoText\
                              + cellCheckedState\
                              + (realActiveDescendantDisplayedText or imageDescription)\
                              + (expandableState and (expandableState + numberOfChildren))\
                              + required)'
            },
    }
}

class Formatting(orca.formatting.Formatting):
    def __init__(self, script):
        orca.formatting.Formatting.__init__(self, script)
        self.update(copy.deepcopy(formatting))
