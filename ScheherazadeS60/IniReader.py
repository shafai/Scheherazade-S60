class IniReader:
    def __init__(self, fileContent):
        self.lines = fileContent.splitlines()
    def ReadSetting(self, settingName, defaulValue):
    	for line in self.lines:
	    if line.startswith(settingName+"="):
	        value = line[len(settingName)+1:]
	        return value
	return defaulValue
