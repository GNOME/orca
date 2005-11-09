# Orca
#
# Copyright 2004-2005 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

"""Manages the default speech server for orca.  A script can use this
as its speech server, or it can feel free to create one of its own.
"""

import debug
import settings
import speechserver

from orca_i18n import _           # for gettext support

# The speech server to use for all speech operations.
#
__speechserver = None

def getSpeechServerFactories():
    """Imports all known SpeechServer factory modules.  Returns a list
    of modules that implement the getSpeechServers method, which
    returns a list of speechserver.SpeechServer instances.
    """
    
    factories = []
    
    moduleNames = settings.getSetting("speechFactoryModules",
                                      ["gnomespeechfactory"])

    for moduleName in moduleNames:
        try:
            module =  __import__(moduleName, 
                                 globals(), 
                                 locals(), 
                                 [''])
            factories.append(module)
        except:
            debug.printException(debug.LEVEL_SEVERE)

    return factories

def init():
    
    global __speechserver

    if __speechserver:
        return

    # We first try to setup thing from the user's preferences.
    # If that doesn't work, we'll fall back to the first engine
    # we find.
    #
    voices = settings.getSetting("voices", {})
    factory = None    
    for voiceName in voices.keys():
        [moduleName, serverName, acssDict] = voices[voiceName]
        if not factory:
            try:
                factory =  __import__(moduleName, 
                                      globals(), 
                                      locals(), 
                                      [''])
            except:
                try:
                    moduleName = moduleName.replace("orca.","",1)
                    factory =  __import__(moduleName, 
                                          globals(), 
                                          locals(), 
                                          [''])
                except:
                    debug.printException(debug.LEVEL_SEVERE)
                    
        if not __speechserver:
            try:
                speechservers = factory.getSpeechServers([serverName])
                __speechserver = speechservers[0]
            except:
                debug.printException(debug.LEVEL_SEVERE)                
        try:
            acss = speechserver.ACSS(acssDict)
            __speechserver.setACSS(voiceName, acss)
        except:
            debug.printException(debug.LEVEL_SEVERE)
        
    if not __speechserver:
        factories = getSpeechServerFactories()
        servers = factories[0].getSpeechServers()
        __speechserver = servers[0]
        return
        
def speak(text, acssName="default"):
    __speechserver.speak(text, acssName)

def speakUtterances(utterances, acssName="default"):
    __speechserver.speakUtterances(utterances, acssName)

def stop():
    __speechserver.stop()

def increaseSpeechRate(inputEvent=None):
    __speechserver.increaseSpeechRate()
    return True

def decreaseSpeechRate(inputEvent=None):
    __speechserver.decreaseSpeechRate()
    return True

def shutdown():
    global __speechserver
    __speechserver.shutdown()
    __speechserver = None


def testNoSettingsInit():
    init()
    speak("testing")
    
def testRecreate():
    module =  __import__("gnomespeechfactory", 
                         globals(), 
                         locals(), 
                         [''])
    speechservers = module.getSpeechServers(["Fonix DECtalk GNOME Speech Driver"])
    print speechservers
    speechservers[0].speak("testing", "default")
    speechservers[0].shutdown()
    
def test():
    import speechserver
    factories = getSpeechServerFactories()
    for factory in factories:
        print factory.__name__
        servers = factory.getSpeechServers()
        for server in servers:
            print "    ", server.getInfo()
            for family in server.getVoiceFamilies():
                name = family[speechserver.VoiceFamily.NAME]
                print "      ", name
                acss = speechserver.ACSS({speechserver.ACSS.FAMILY : family})
                server.setACSS(name, acss)
                server.speak(name, name)
                server.speak("testing", "default")
            server.shutdown()

