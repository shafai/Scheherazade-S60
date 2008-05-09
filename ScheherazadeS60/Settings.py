class Settings:
    def __init__(self):
        settingsPath = "c:\\data\\Scheherazade"
        if not os.path.exists(settingsPath):
          os.makedirs(settingsPath)
        
        self.setingFileName = settingsPath + "\\Scheherazade.settings"
        self.currentBook = ""
        self.autoBookmarkSaveInterval = 30
        self.volume = 5

        self.rewindSeconds = 20
        self.rewindOnPauseSeconds = 5
        self.longRewindSeconds = 60
        self.libPath = "E:\\AudioBooks"
        self.voiceTaggingEnabled = 0
        self.voiceTagFileFormat = "AMR"
    
    def Save(self):
        f = open(self.setingFileName, 'wt')
        f.write("AutoBookmarkSaveInterval=%d\n"%self.autoBookmarkSaveInterval)
        f.write("CurrentBook=%s\n"%self.currentBook)
        f.write("Volume=%s\n"%self.volume)
        f.write("LibPath=%s\n"%self.libPath)
        f.write("RewindSeconds=%d\n"%self.rewindSeconds)
        f.write("RewindOnPauseSeconds=%d\n"%self.rewindOnPauseSeconds)
        f.write("LongRewindSeconds=%d\n"%self.longRewindSeconds)
        f.write("VoiceTaggingEnabled=%d\n"%self.voiceTaggingEnabled)
        f.write("VoiceTagFileFormat=%s\n"%self.voiceTagFileFormat)
        f.close()

    def Load(self):
        if os.path.exists(self.setingFileName):
            f = open(self.setingFileName, 'rt')
            iniReader = IniReader(f.read())
            f.close()
            
            self.autoBookmarkSaveInterval = int(iniReader.ReadSetting("AutoBookmarkSaveInterval", self.autoBookmarkSaveInterval))
            self.currentBook = iniReader.ReadSetting("CurrentBook", self.currentBook)
            self.volume = int(iniReader.ReadSetting("Volume", self.volume))

            self.libPath = iniReader.ReadSetting("LibPath", self.libPath)
            self.rewindSeconds = int(iniReader.ReadSetting("RewindSeconds", self.rewindSeconds))
            self.rewindOnPauseSeconds = int(iniReader.ReadSetting("RewindOnPauseSeconds", self.rewindOnPauseSeconds))
            self.longRewindSeconds = int(iniReader.ReadSetting("LongRewindSeconds", self.longRewindSeconds))
            self.voiceTaggingEnabled = int(iniReader.ReadSetting("VoiceTaggingEnabled", self.voiceTaggingEnabled))
            self.voiceTagFileFormat = iniReader.ReadSetting("VoiceTagFileFormat", self.voiceTagFileFormat)

            if not os.path.exists(os.path.join(self.libPath, self.currentBook)):
                self.currentBook = ""
    
    def ShowOptionsForm(self):
      appuifw.app.title = u'Settings'
      myForm = SettinsEditForm(self)
      myForm.Show( )
      appuifw.app.title = u'Scheherazade'
      if myForm.isSaved:
        needRestart = False
        if self.libPath != myForm.GetlibLocation():
	      needRestart = True
        self.libPath = myForm.GetlibLocation()
        self.rewindSeconds = myForm.GetRewindSeconds()
        self.rewindOnPauseSeconds = myForm.GetRewindOnPauseSeconds()
        self.longRewindSeconds = myForm.GetLongRewindSeconds()
        self.voiceTaggingEnabled = myForm.GetVoiceTaggingEnabled()
        self.voiceTagFileFormat = myForm.GetVoiceTagFileFormat()
        #self.autoBookmarkSaveInterval = 30
        self.Save()
        if needRestart:
	      appuifw.note(u"Changes will take effect next time you run Scheherazade.")

