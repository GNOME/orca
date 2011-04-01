def getSpeechServerFactories():
    print 'getSpeechServerFactories()'
    return []

def _initSpeechServer(moduleName=None, speechServerInfo=None):
    print '_initSpeechServer'

def init():
    print 'init'

def __resolveACSS(acss=None):
    print '__resolveACSS'

def sayAll(utteranceIterator=None, progressCallback=None):
    print 'sayAll'

def _speak(text, acss, interrupt):
    print '_speak'

def speak(content, acss=None, interrupt=True):
    print 'speak from %s' % orca_state.activeScript

def speakKeyEvent(event_string, eventType):
    print 'speakKeyEvent'

def speakCharacter(character, acss=None):
    print 'speakCharacter'

def isSpeaking():
    print ' isSpeaking'

def getInfo():
    print 'getInfo'

def stop():
    print 'stop from %s' % orca_state.activeScript

def updatePunctuationLevel(script=None, inputEvent=None):
    print 'updatePunctuationLevel'

def increaseSpeechRate(script=None, inputEvent=None):
    print 'increaseSpeechRate'

def decreaseSpeechRate(script=None, inputEvent=None):
    print 'decreaseSpeechRate'

def increaseSpeechPitch(script=None, inputEvent=None):
    print 'increaseSpeechPitch'

def decreaseSpeechPitch(script=None, inputEvent=None):
    print 'decreaseSpeechPitch'

def shutdown():
    print 'shutdown'

def reset(text=None, acss=None):
    print 'reset'

def testNoSettingsInit():
    print 'testNoSettingsInit'

def test():
    print 'test'

def _processMultiCaseString(string):
    print '_processMultiCaseString('
