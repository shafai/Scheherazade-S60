class SettinsEditForm(object):
    
    def __init__( self, settings ):
        self.libLocationDisplays = [u'Phone Memory', u'Memory Card']
        self.libLocations = ["C:\\Data\\AudioBooks", "E:\\AudioBooks"]
        self.fields = [
                         ( u'Location for Audiobooks', 'combo', ( self.libLocationDisplays, self.libLocations.index(settings.libPath) ) ),
                         ( u'Short rewind (Left, Right)','number', settings.rewindSeconds ),
                         ( u'Long rewind (4,6)','number', settings.longRewindSeconds ),
                         ( u'Rewind on pause','number', settings.rewindOnPauseSeconds )
                      ]
 
    def Show( self ):
        self.isSaved = False
        self.form = appuifw.Form(self.fields, appuifw.FFormEditModeOnly | appuifw.FFormDoubleSpaced)
        self.form.save_hook = self.SavedCallBack
        #self.form.flags = appuifw.FFormEditModeOnly
        self.form.execute( )
 
 
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

