#!/usr/bin/python

import sys

from orca.gui.toolkit import Toolkit

statusbar = None

def onToggled(widget):
    label = widget.getDisplayedText()
    state = widget.getState()
    statusbar.setMessage("'%s' toggled to: %s" % (label, state), 0)

def onClicked(widget, function=None):
    statusbar.setMessage("'%s' clicked" % widget.getDisplayedText(), 0)
    if function:
        function()

def onValueChanged(widget):
    statusbar.setMessage("value changed to: %f" % widget.getValue(), 0)

def onTextChanged(widget):
    statusbar.setMessage("text is now: %s" % widget.getDisplayedText(), 0)

def onSelectionChanged(widget, position=None):
    if position == None:
        position = widget.getSelectedItemPosition()
    text = widget.getSelectedText()
    statusbar.setMessage(
        "selected item is at index %d and contains '%s'" % (position, text), 0)

def onPageChanged(widget, index=-1):
    statusbar.setMessage("Active page is now page %s" % index, 0)

def onWindowCloseEvent(widget, event):
    print "Close event for window: %s" % widget.getTitle()
    widget.destroy()
    quit()

def onResponse(widget, responseID):
    print widget, responseID

def showWindow(window):
    window.display()

def runTest(toolkitName):
    # TODO: This test should be broken up, of course. I am putting off
    # doing that because having a single dialog with which to check
    # all changes is incredibly convenient -- especially given three
    # toolkits actively being implemented.

    global statusbar

    toolkit = Toolkit(toolkitName)

    window = toolkit.createWindow("Test Window for %s" % toolkitName)
    window.bind(window.SIGNAL_CLOSE_EVENT, onWindowCloseEvent)

    tabbedWidget = toolkit.createTabbedWidget()
    window.add(tabbedWidget)
    tabbedWidget.bind(tabbedWidget.SIGNAL_PAGE_CHANGED, onPageChanged)

    statusbar = toolkit.createStatusBar()
    statusbar.setSpacing(10)
    window.add(statusbar)

    table = toolkit.createTable(2, 2)
    label = toolkit.createLabel('Toggles')
    tabbedWidget.addPage(table, label)

    frame = toolkit.createFrame('Checkboxes')
    frame.setShadowType(frame.SHADOW_IN)
    frame.setBorderWidth(10)
    table.add(frame, 0, 0)

    vbox = toolkit.createVBox()
    vbox.alignLeft()
    vbox.setLeftPadding(12)
    vbox.alignTop()
    vbox.setTopPadding(6)
    frame.add(vbox)

    cb1 = toolkit.createCheckbox('CB 1 (checked)', True)
    cb1.bind(cb1.SIGNAL_TOGGLED, onToggled)
    vbox.add(cb1)

    cb2 = toolkit.createCheckbox('CB 2 (unchecked)', False)
    cb2.bind(cb2.SIGNAL_TOGGLED, onToggled)
    vbox.add(cb2)

    cb3 = toolkit.createCheckbox('_CB 3 (uses underline)', False)
    cb3.bind(cb3.SIGNAL_TOGGLED, onToggled)
    vbox.add(cb3)

    frame = toolkit.createFrame('Radio Buttons')
    frame.setShadowType(frame.SHADOW_OUT)
    frame.setBorderWidth(10)
    table.add(frame, 0, 1)

    vbox = toolkit.createVBox()
    vbox.alignLeft()
    vbox.setLeftPadding(12)
    vbox.alignTop()
    vbox.setTopPadding(6)
    frame.add(vbox)

    rb1 = toolkit.createRadioButton('RB 1 (selected)', None, True)
    rb1.bind(rb1.SIGNAL_TOGGLED, onToggled)
    vbox.add(rb1)

    rb2 = toolkit.createRadioButton('RB 2 (unselected)', rb1, False)
    rb2.bind(rb2.SIGNAL_TOGGLED, onToggled)
    vbox.add(rb2)

    rb3 = toolkit.createRadioButton('_RB 3 (uses underline)', rb1, False)
    rb3.bind(rb3.SIGNAL_TOGGLED, onToggled)
    vbox.add(rb3)

    table = toolkit.createTable(1, 2)
    label = toolkit.createLabel('Buttons')
    tabbedWidget.addPage(table, label)

    frame = toolkit.createFrame('Simple Buttons')
    frame.setShadowType(frame.SHADOW_IN)
    frame.setBorderWidth(10)
    table.add(frame, 0, 0)

    vbox = toolkit.createVBox()
    vbox.alignLeft()
    vbox.setLeftPadding(12)
    vbox.alignTop()
    vbox.setTopPadding(6)
    frame.add(vbox)

    pb1 = toolkit.createPushButton('Button 1 (is default)')
    vbox.add(pb1)
    pb1.setIsDefault(True)
    pb1.bind(pb1.SIGNAL_CLICKED, onClicked)

    pb2 = toolkit.createPushButton('Button 2 (not default)')
    vbox.add(pb2)
    pb2.setIsDefault(False)
    pb2.bind(pb2.SIGNAL_CLICKED, onClicked)

    pb3 = toolkit.createPushButton('_Button 3 (uses underline)')
    vbox.add(pb3)
    pb3.bind(pb3.SIGNAL_CLICKED, onClicked)

    frame = toolkit.createFrame('Message Dialogs')
    frame.setShadowType(frame.SHADOW_OUT)
    frame.setBorderWidth(10)
    table.add(frame, 0, 1)

    hbox = toolkit.createHBox()
    hbox.setSpacing(10)
    frame.add(hbox)

    vbox = toolkit.createVBox()
    vbox.alignLeft()
    vbox.setLeftPadding(12)
    vbox.alignTop()
    vbox.setTopPadding(6)
    hbox.add(vbox)

    messageDialog = toolkit.createMessageDialog()
    messageDialog.setMainText('Type Not Specified')
    messageDialog.setSecondaryText('Secondary text. Bla bla bla bla bla bla.')
    messageDialog.addButton(messageDialog.BUTTON_CLOSE)
    messageDialog.bind(messageDialog.SIGNAL_RESPONSE, onResponse)
    pb1 = toolkit.createPushButton('Type Not Specified')
    vbox.add(pb1)
    pb1.bind(pb1.SIGNAL_CLICKED, onClicked, messageDialog.display)

    messageDialog = toolkit.createMessageDialog()
    messageDialog.setType(messageDialog.MESSAGE_INFO)
    messageDialog.setMainText('Information')
    messageDialog.setSecondaryText('Secondary text. Bla bla bla bla bla bla.')
    messageDialog.addButton(messageDialog.BUTTON_OK)
    messageDialog.bind(messageDialog.SIGNAL_RESPONSE, onResponse)
    pb2 = toolkit.createPushButton('Information')
    vbox.add(pb2)
    pb2.bind(pb2.SIGNAL_CLICKED, onClicked, messageDialog.display)

    messageDialog = toolkit.createMessageDialog()
    messageDialog.setType(messageDialog.MESSAGE_WARNING)
    messageDialog.setMainText('Warning')
    messageDialog.setSecondaryText('Secondary text. Bla bla bla bla bla bla.')
    messageDialog.addButton(messageDialog.BUTTON_CANCEL)
    messageDialog.bind(messageDialog.SIGNAL_RESPONSE, onResponse)
    pb3 = toolkit.createPushButton('Warning')
    vbox.add(pb3)
    pb3.bind(pb3.SIGNAL_CLICKED, onClicked, messageDialog.display)

    vbox = toolkit.createVBox()
    vbox.alignLeft()
    vbox.setLeftPadding(12)
    vbox.alignTop()
    vbox.setTopPadding(6)
    hbox.add(vbox)

    messageDialog = toolkit.createMessageDialog()
    messageDialog.setType(messageDialog.MESSAGE_QUESTION)
    messageDialog.setMainText('Question')
    messageDialog.setSecondaryText('Secondary text. Bla bla bla bla bla bla.')
    messageDialog.addButton(messageDialog.BUTTON_NO)
    messageDialog.addButton(messageDialog.BUTTON_YES)
    messageDialog.bind(messageDialog.SIGNAL_RESPONSE, onResponse)
    pb4 = toolkit.createPushButton('Question')
    vbox.add(pb4)
    pb4.bind(pb4.SIGNAL_CLICKED, onClicked, messageDialog.display)

    messageDialog = toolkit.createMessageDialog()
    messageDialog.setType(messageDialog.MESSAGE_ERROR)
    messageDialog.setMainText('Error')
    messageDialog.setSecondaryText('Secondary text. Bla bla bla bla bla bla.')
    messageDialog.addButton(messageDialog.BUTTON_CANCEL)
    messageDialog.addButton(messageDialog.BUTTON_OK)
    messageDialog.bind(messageDialog.SIGNAL_RESPONSE, onResponse)
    pb5 = toolkit.createPushButton('Error')
    vbox.add(pb5)
    pb5.bind(pb5.SIGNAL_CLICKED, onClicked, messageDialog.display)

    messageDialog = toolkit.createMessageDialog()
    messageDialog.setType(messageDialog.MESSAGE_ERROR)
    messageDialog.setMainText('Wordy Error')
    messageDialog.setSecondaryText('Secondary text. The presence of the text ' \
                                   'should force the message dialog to grow ' \
                                   'sufficiently to display all of the text ' \
                                   'reasonably. Bla bla bla bla bla bla bla.' \
                                   '\n\nBla bla bla bla bla bla bla bla bla.')
    pb6 = toolkit.createPushButton('Wordy Error')
    messageDialog.bind(messageDialog.SIGNAL_RESPONSE, onResponse)
    vbox.add(pb6)
    pb6.bind(pb6.SIGNAL_CLICKED, onClicked, messageDialog.display)

    table = toolkit.createTable(1, 2)
    label = toolkit.createLabel('Ranges')
    tabbedWidget.addPage(table, label)

    frame = toolkit.createFrame('Spinners')
    frame.setShadowType(frame.SHADOW_IN)
    frame.setBorderWidth(10)
    table.add(frame, 0, 0)

    vbox = toolkit.createVBox()
    vbox.alignLeft()
    vbox.setLeftPadding(12)
    vbox.alignTop()
    vbox.setTopPadding(6)
    frame.add(vbox)

    hbox = toolkit.createHBox()
    hbox.setSpacing(10)
    vbox.add(hbox)

    minValue = -10
    maxValue = 10
    value = -3.5
    step = 1
    page = 5
    precision = 3

    label = toolkit.createLabel('_Volume:')
    spinner = toolkit.createSpinner()
    spinner.setRange(minValue, maxValue)
    spinner.setValue(value)
    spinner.setIncrements(step, page)
    spinner.setPrecision(precision)
    spinner.bind(spinner.SIGNAL_VALUE_CHANGED, onValueChanged)
    spinner.bind(spinner.SIGNAL_TEXT_CHANGED, onTextChanged)
    label.setMnemonicWidget(spinner)
    hbox.add(label)
    hbox.add(spinner)

    hbox = toolkit.createHBox()
    hbox.setSpacing(10)
    vbox.add(hbox)

    precision = 0
    value = 2

    label = toolkit.createLabel('_Rate:')
    spinner = toolkit.createSpinner()
    spinner.setRange(minValue, maxValue)
    spinner.setValue(value)
    spinner.setIncrements(step, page)
    spinner.setPrecision(precision)
    spinner.bind(spinner.SIGNAL_VALUE_CHANGED, onValueChanged)
    spinner.bind(spinner.SIGNAL_TEXT_CHANGED, onTextChanged)
    hbox.add(label, False, True, 10)
    hbox.add(spinner)

    frame = toolkit.createFrame('Sliders')
    frame.setShadowType(frame.SHADOW_OUT)
    frame.setBorderWidth(10)
    table.add(frame, 0, 1)

    vbox = toolkit.createVBox()
    vbox.alignLeft()
    vbox.setLeftPadding(12)
    vbox.alignTop()
    vbox.setTopPadding(6)
    frame.add(vbox)

    minValue = -10
    maxValue = 10
    value = -3.5
    step = 1
    page = 5
    precision = 3

    slider = toolkit.createHSlider()
    slider.setRange(minValue, maxValue)
    slider.setValue(value)
    slider.setIncrements(step, page)
    slider.setPrecision(precision)
    vbox.add(slider, True, True, 0)
    slider.bind(slider.SIGNAL_VALUE_CHANGED, onValueChanged)

    precision = 0
    value = 2

    slider = toolkit.createHSlider()
    slider.setRange(minValue, maxValue)
    slider.setValue(value)
    slider.setIncrements(step, page)
    slider.setPrecision(precision)
    vbox.add(slider)
    slider.bind(slider.SIGNAL_VALUE_CHANGED, onValueChanged)

    table = toolkit.createTable(2, 2)
    label = toolkit.createLabel('Text')
    tabbedWidget.addPage(table, label)

    frame = toolkit.createFrame('Entries')
    frame.setShadowType(frame.SHADOW_IN)
    frame.setBorderWidth(10)
    table.add(frame, 0, 0)

    vbox = toolkit.createVBox()
    vbox.alignLeft()
    vbox.setLeftPadding(12)
    vbox.alignTop()
    vbox.setTopPadding(6)
    frame.add(vbox)

    hbox = toolkit.createHBox()
    hbox.setSpacing(10)
    vbox.add(hbox)

    label = toolkit.createLabel('_Username:')
    entry = toolkit.createEntry('Joanmarie', False)
    entry.bind(entry.SIGNAL_TEXT_CHANGED, onTextChanged)
    label.setMnemonicWidget(entry)
    hbox.add(label)
    hbox.add(entry)

    hbox = toolkit.createHBox()
    hbox.setSpacing(10)
    vbox.add(hbox)

    label = toolkit.createLabel('_Password:')
    entry = toolkit.createEntry('ConsoleAppsRock', True)
    entry.bind(entry.SIGNAL_TEXT_CHANGED, onTextChanged)
    label.setMnemonicWidget(entry)
    hbox.add(label)
    hbox.add(entry)

    frame = toolkit.createFrame('Comboboxes')
    frame.setShadowType(frame.SHADOW_OUT)
    frame.setBorderWidth(10)
    table.add(frame, 0, 1)

    vbox = toolkit.createVBox()
    vbox.alignLeft()
    vbox.setLeftPadding(12)
    vbox.alignTop()
    vbox.setTopPadding(6)
    frame.add(vbox)

    hbox = toolkit.createHBox()
    hbox.setSpacing(10)
    vbox.add(hbox)

    label = toolkit.createLabel('_Standard:')
    comboboxItems = ['one', 'two', 'three', 'four', 'five']
    combobox = toolkit.createTextComboBox()
    for i, item in enumerate(comboboxItems):
        combobox.addItemAtPosition(item, i)
    combobox.setSelectedItem(2)
    combobox.bind(combobox.SIGNAL_SELECTION_CHANGED, onSelectionChanged)
    label.setMnemonicWidget(combobox)
    hbox.add(label)
    hbox.add(combobox, True, True, 10)

    hbox = toolkit.createHBox()
    hbox.setSpacing(10)
    vbox.add(hbox)

    label = toolkit.createLabel('_Editable:')
    comboboxItems = ['edit me!', 'one', 'two', 'three', 'four', 'five']
    combobox = toolkit.createTextComboBox(True)
    for i, item in enumerate(comboboxItems):
        combobox.addItemAtPosition(item, i)
    combobox.setSelectedItem(0)
    combobox.bind(combobox.SIGNAL_SELECTION_CHANGED, onSelectionChanged)
    hbox.add(label)
    hbox.add(combobox, True, True, 10)

    table = toolkit.createTable(1, 2)
    label = toolkit.createLabel('Trees')
    tabbedWidget.addPage(table, label)

    tree = toolkit.createTree(toolkit.TYPE_STRING, toolkit.TYPE_INT, toolkit.TYPE_STRING)
    tree.setColumnTitle(0, 'Word')
    tree.setColumnTitle(1, 'Arabic')
    tree.setColumnTitle(2, 'Roman')
    tree.setGridLines(tree.GRID_LINES_BOTH)
    tree.setRulesHint(True)
    tree.setRootIsDecorated(False)
    tree.sortByColumn(0, tree.ORDER_ASCENDING)
    model = tree.getModel()
    model.append(None, ['One', 1, 'I'])
    model.append(None, ['Two', 2, 'II'])
    model.append(None, ['Three', 3, 'III'])
    model.append(None, ['Four', 4, 'IV'])
    model.append(None, ['Five', 5, 'V'])
    table.add(tree, 0, 0)

    window.display()
    toolkit.main()

    return window

def main():
    try:
       toolkit = sys.argv[1]
    except IndexError:
        toolkit = 'gtk2'

    runTest(toolkit)

    return 0

if __name__ == "__main__":
    sys.exit(main())
