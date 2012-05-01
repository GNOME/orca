from orca import settings_manager
from json import load, dump
from pprint import pprint

def exerciseBackendAPI(backendName, profile):
    settingsManager = settings_manager.SettingsManager(backendName)

    print("\n\n================ Testing Backend %s ====================\n\n" % \
            backendName)
    print('Profile: ', profile)
    print('Profiles list: ', settingsManager.availableProfiles())

    #settingsManager.setProfile(profile)

    # Getters
    preferences = settingsManager.getPreferences(profile)
    print('preferences: \n', preferences, '\n\n')

    generalSettings = settingsManager.getGeneralSettings(profile)
    print('generalSettings: \n', generalSettings, '\n\n')

    pronunciations = settingsManager.getPronunciations(profile)
    print('pronunciations: \n', pronunciations, '\n\n')

    keybindings = settingsManager.getKeybindings(profile)
    print('keybindings: \n', keybindings, '\n\n')

    # Adding new settings to the profile and merging them
    newGeneralSettings = getSettingsFromFile('general')
    print("newGeneralSettings = ")
    pprint(newGeneralSettings)
    settingsManager._setProfileGeneral(newGeneralSettings)
    generalSettings = settingsManager.getGeneralSettings(profile)
    print("generalSettings = ")
    pprint(generalSettings)

    newKeybindingsSettings = getSettingsFromFile('keybindings')
    print("\n\nnewKeybindingsSettings = ")
    pprint(newKeybindingsSettings)
    settingsManager._setProfileKeybindings(newKeybindingsSettings)
    keybindings = settingsManager.getKeybindings(profile)
    print("keybindings = ")
    pprint(keybindings)

    newPronunciationsSettings = getSettingsFromFile('pronunciations')
    print("\n\nnewPronunciationsSettings = ")
    pprint(newPronunciationsSettings)
    settingsManager._setProfileGeneral(newPronunciationsSettings)
    pronunciations = settingsManager.getPronunciations(profile)
    print("pronunciations = ")
    pprint(pronunciations)

    #settingsManager.saveSettings()
    isFirstStart = settingsManager.isFirstStart()
    print("\n\nIs First Start? => ", isFirstStart)
    print("\n\nSetting firstStart key")
    settingsManager.setFirstStart()
    isFirstStart = settingsManager.isFirstStart()
    print("\n\nIs First Start? => ", isFirstStart)
    print("\n\n===========================================================\n\n")

    print("\n\nTesting import from a file I")
    print("\n===========================================================")
    availableProfilesBefore = settingsManager.availableProfiles()
    print("\nAvailable Profiles BEFORE the import  => ", availableProfilesBefore)
    settingsManager.importProfile('importFile.conf')
    availableProfilesAfter = settingsManager.availableProfiles()
    print("\nAvailable Profiles AFTER the import  => ", availableProfilesAfter)

    print("\n\nTesting import from a file II")
    print("\n===========================================================")
    availableProfilesBefore = settingsManager.availableProfiles()
    print("\nAvailable Profiles BEFORE the import  => ", availableProfilesBefore)
    settingsManager.importProfile('importFile2.conf')
    availableProfilesAfter = settingsManager.availableProfiles()
    print("\nAvailable Profiles AFTER the import  => ", availableProfilesAfter)
    

def getSettingsFromFile(dictName):
    fileName = '%sSettings.conf' % dictName
    try:
        dictFile = open(fileName)
    except:
        import sys
        print("You should run the test from the test directory")
        sys.exit()
    settings = load(dictFile)
    dictFile.close()
    return settings

# main
profile = 'default'
print('profile: default backendName: json\n')
exerciseBackendAPI('json', 'default')
#print 'profile: default backendName: gconf\n'
#exerciseBackendAPI('gconf', 'default')
#exerciseBackendAPI('default', 'gsettings', s)
