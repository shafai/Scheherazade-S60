class SettinsEditForm(object):
    
    def __init__( self, settings ):
        self.libLocationDisplays = [u'Phone Memory', u'Memory Card']
        self.yesNoOptions = [u'Yes', u'No']
        self.recordingFormatsUnicode = [u'AMR', u'WAV']
        self.recordingFormats = ['AMR', 'WAV']
        self.libLocations = ["C:\\Data\\AudioBooks", "E:\\AudioBooks"]
        self.fields = [
                         ( u'Location for Audiobooks', 'combo', ( self.libLocationDisplays, self.libLocations.index(settings.libPath) ) ),
                         ( u'Short rewind (Left, Right)','number', settings.rewindSeconds ),
                         ( u'Long rewind (4,6)','number', settings.longRewindSeconds ),
                         ( u'Rewind on pause','number', settings.rewindOnPauseSeconds ),
                         ( u'Voice tagging', 'combo', ( self.yesNoOptions, self.BooleanReverse(settings.voiceTaggingEnabled) ) ),
                         ( u'Voice tag file format', 'combo', ( self.recordingFormatsUnicode, self.recordingFormats.index(settings.voiceTagFileFormat)) ),
                         ( u'Rewind on phone call','number', settings.rewindOnCallSeconds)
                      ]
 
    def Show( self ):
        self.isSaved = False
        self.form = appuifw.Form(self.fields, appuifw.FFormEditModeOnly | appuifw.FFormDoubleSpaced)
        self.form.save_hook = self.SavedCallBack
        #self.form.flags = appuifw.FFormEditModeOnly
        self.form.execute( )

    def BooleanReverse(self, number):
        if number == 1:
            return 0
        else:
            return 1
 
 
    def SavedCallBack( self, aBool ):
        self.isSaved = aBool
                  
    def GetlibLocation( self ):
        return self.libLocations[self.form[0][2][1]]
  
    def GetRewindSeconds( self ):
        return self.form[1][2]
 
    def GetLongRewindSeconds( self ):
        return self.form[2][2]

    def GetRewindOnPauseSeconds( self ):
        return self.form[3][2]

    def GetVoiceTaggingEnabled( self ):
        return self.BooleanReverse(self.form[4][2][1])

    def GetVoiceTagFileFormat( self ):
        return self.recordingFormats[self.form[5][2][1]]
       
    def GetRewindOnCallSeconds(self):
        return self.form[6][2]
    