import os
import re
import time
import audio
import appuifw
import math
import e32
from key_codes import *
from graphics import *
import random

class TextWriter:    
    def __init__(self, canvas):
        self.canvas = canvas
        self.coords = [0,0]
        self.spacing = 5
        
    def render_line(self, text, font, fill):
        bounding, to_right, fits = self.canvas.measure_text(text, font=font)
        self.canvas.text([self.coords[0], self.coords[1] - bounding[1]], unicode(text), font=font, fill=fill)
        self.coords = [self.coords[0], 
                       self.coords[1] - bounding[1] + bounding[3] + self.spacing                       
                       ]

    def chop(self, text, font, width):
        lines = []
        text_left = text
        while len(text_left) > 0: 
            bounding, to_right, fits = self.canvas.measure_text(
                    text_left, font=font, 
                    maxwidth=width)
            if fits <= 0:
                lines.append(text_left)
                break
            slice = text_left[0:fits]
            adjust = 0
        
            if len(slice) < len(text_left):
                rindex = slice.rfind(" ")            
                if rindex > 0:
                    adjust = 1
                    slice = slice[0:rindex]
                                
            lines.append(slice)
            text_left = text_left[len(slice)+adjust:]
        
        return lines
        
    def GetNeededHeight(self, text, font, totalWidthAvailable):
        textBounds = self.canvas.measure_text(text, font=font)[0]
        fontHeight = -(textBounds[1] - textBounds[3])
        chopped_lines = self.chop(text, font, totalWidthAvailable)
        return len(chopped_lines) * fontHeight
        
    def render(self, text, fontName, fontFlags, initialFontSize, bounds, fill=0x000000):
        text = unicode(text)        
        totalHeightAvailable = bounds[3] - bounds[1]
        totalWidthAvailable = bounds[2] - bounds[0]
        totalHeightNeeded = 10000
        currentFontSize = initialFontSize + 1
        while totalHeightNeeded > totalHeightAvailable and currentFontSize > 5:
	    currentFontSize -= 1
	    font = (fontName, currentFontSize, fontFlags)
	    totalHeightNeeded = self.GetNeededHeight(text, font, totalWidthAvailable)
        chopped_lines = self.chop(text, font, totalWidthAvailable)
        freeVSpace = totalHeightAvailable - totalHeightNeeded
        self.spacing = freeVSpace / (len(chopped_lines) + 1)
        self.coords = [bounds[0],bounds[1] + self.spacing]
        
        for chopped_line in chopped_lines:
            self.render_line(chopped_line, font, fill)
                
class MediaFile:
    def __init__(self):
        self.PlayableFileTypes = [".wav", ".mp3", ".m4b", ".m4a", ".wma", ".amr", ".acc", ".awb", ".flac"]
    def IsPlayable(self, filename):
        return os.path.splitext(filename)[1].lower() in self.PlayableFileTypes

class Library:
    def __init__(self, path):
        self.books = []
        self.libPath = path
    
    def LoadLibrary(self):
        self.mediaFile = MediaFile()
        for name in os.listdir(self.libPath):
            path = os.path.join(self.libPath, name)
            if os.path.isdir(path) :
                self.books.append(Book(path, name, False))
            else:
                if self.mediaFile.IsPlayable(path):
                    self.books.append(Book(self.libPath, name, True))
                    pass
                
                
    def GetBookByName(self, bookName):
        for book in self.books:
	    if book.bookName == bookName:
	        return book
	return self.books[0]      

class Book:
    def __init__(self, bookPath, bookName, isSingelFile):
        self.bookParts = []
        self.mediaFile = MediaFile()
        self.isSingleFile = isSingelFile
        self.bookName = bookName
        self.bookPath = bookPath
        self.currentBookPart = ""
        self.currentBookPartIndex = 0
        
    def AddBookPart(self, bookPartFileName, bookPartDisplay):
        hash = self.replaceNumbersRegex.sub(self.ReplaceNumbers, bookPartFileName)
        self.bookParts.append((bookPartFileName, bookPartDisplay, hash))
        
    def ReplaceNumbers(self, match ):
       value = int( match.group() )
       return "%06d"%value
       
    def Load(self):
        self.replaceNumbersRegex = re.compile(r'\d+')
        if self.isSingleFile:
            self.AddSingleFileBook(self.bookName)
        else:
            self.AddDirBook(self.bookName)
            
    def AddSingleFileBook(self, fileName):
        self.AddBookPart(os.path.join(self.bookPath, fileName), fileName)

    def ScanDirForBookparts(self, bookPath):
        for bookPartName in os.listdir(bookPath):
            fullPathToCheck = os.path.join(bookPath, bookPartName)
            if os.path.isfile(fullPathToCheck) and self.mediaFile.IsPlayable(fullPathToCheck):
                self.AddBookPart(fullPathToCheck, bookPartName)
            if os.path.isdir(fullPathToCheck):
	        self.ScanDirForBookparts(fullPathToCheck)
 
       
    def AddDirBook(self, dirName):
        self.ScanDirForBookparts(self.bookPath)
        self.bookParts.sort(self.CompareBookParts)
	    
    def CompareBookParts(self, x, y):
      xName, xDisplay,xHash = x
      yName, yDisplay,yHash = y
      
      if xHash == yHash :
        return 0
      if xHash < yHash:
        return -1
      return 1
 
 

class IniReader:
    def __init__(self, fileContent):
        self.lines = fileContent.splitlines()
    def ReadSetting(self, settingName, defaulValue):
    	for line in self.lines:
	    if line.startswith(settingName+"="):
	        value = line[len(settingName)+1:]
	        return value
	return defaulValue
 
class LogWriter:
	def __init__(self):
	  self.logFileName = "c:\\data\\Scheherazade\\Scheherazade.Log"
	 
	def Log(self, message):
	  logFile = open(self.logFileName, 'at')
	  logFile.write(message + "\n");
	  logFile.close()
  
  
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
    
    def Save(self):
        f = open(self.setingFileName, 'wt')
        f.write("AutoBookmarkSaveInterval=%d\n"%self.autoBookmarkSaveInterval)
        f.write("CurrentBook=%s\n"%self.currentBook)
        f.write("Volume=%s\n"%self.volume)
        f.write("LibPath=%s\n"%self.libPath)
        f.write("RewindSeconds=%d\n"%self.rewindSeconds)
        f.write("RewindOnPauseSeconds=%d\n"%self.rewindOnPauseSeconds)
        f.write("LongRewindSeconds=%d\n"%self.longRewindSeconds)
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
        #self.autoBookmarkSaveInterval = 30
        self.Save()
        if needRestart:
	      appuifw.note(u"Changes will take effect next time you run Scheherazade.")

 
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

                 
class Bookmark:
    def __init__(self):
        self.BookPartName = ""
        self.Position = 0
    def Save(self, book):
        fileName = os.path.join(book.bookPath, u"%s.AutoBookmark"%book.bookName)
        f = open(fileName, 'wt')
        f.write("CurrentBookPart=%s\n"%book.currentBookPart)
        posToSave = self.Position/1000000
        f.write("Position=%0d\n"%posToSave)
        f.close()

    def Load(self, book):
        fileName = os.path.join(book.bookPath, u"%s.AutoBookmark"%book.bookName)
        if os.path.exists(fileName):
            f = open(fileName, 'rt')
            iniReader = IniReader(f.read())
            f.close()

            self.BookPartName = iniReader.ReadSetting("CurrentBookPart", self.BookPartName)
            self.Position = int(iniReader.ReadSetting("Position", self.Position)) * 1000000


class Scheherazade:

    def __init__(self):
        self.font = ('normal',None,FONT_BOLD|FONT_ANTIALIAS)
        self.currentPos = 0
        self.currentBookpartDuration = 0
        self.audioPlayer = audio.Sound()
        self.screenWidth = 240
        self.screenTopMargin = 5
        self.exitflag=0
        self.fieldcolor=(192,192,128)
        self.old_body=appuifw.app.body
        self.settings = Settings()
        self.logWriter = LogWriter()
        self.Loading = True
        self.canvas=appuifw.Canvas(redraw_callback=self.redraw)
        appuifw.app.body=self.canvas
        self.canvas.clear(self.fieldcolor)
        self.settings.Load()
        if not os.path.exists(self.settings.libPath):
          os.makedirs(self.settings.libPath)
        self.library = Library(self.settings.libPath)
        self.library.LoadLibrary()
        if len(self.library.books) == 0:
            appuifw.note(u"No books found, please copy at least one book to your AudioBooks folder.")
            self.set_exit()
            return
 
        if self.settings.currentBook == "":
            appuifw.note(u"Please Choose a book to listen to.")
            self.SelectBook()
            if self.settings.currentBook == "":
                self.set_exit()
                return
        
        appuifw.app.menu = [
                            (u'Select book', self.SelectBook), 
                            (u'Settings', self.settings.ShowOptionsForm),
#                            (u'-', None),
                            (u'About', self.About)
                            ]
        
        self.LoadBook()
        self.lastSavedbookmark = time.time()
        
        self.canvas.bind(EKey6,lambda:self.Forward(self.settings.longRewindSeconds))
        self.canvas.bind(EKey4,lambda:self.Rewind(self.settings.longRewindSeconds))
        self.canvas.bind(EKey9,lambda:self.NextBookPart())
        self.canvas.bind(EKey7,lambda:self.PrevBookPart())
        self.canvas.bind(EKeySelect,lambda:self.PlayPause())
        self.canvas.bind(EKeyRightArrow,lambda:self.Forward(self.settings.rewindSeconds))
        self.canvas.bind(EKeyUpArrow,lambda:self.VolUp())
        self.canvas.bind(EKeyLeftArrow,lambda:self.Rewind(self.settings.rewindSeconds))
        self.canvas.bind(EKeyDownArrow,lambda:self.VolDown())
        self.isChangingPosition = 0
        self.Loading = False
        self.redraw(None)

    def LoadBook(self):
        self.currentBook = self.library.GetBookByName(self.settings.currentBook)
        self.currentBook.Load()
        if len(self.currentBook.bookParts) == 0:
	    appuifw.note(u"Book seems to have no playable files in it, please select another book.")
	    self.SelectBook()
 
        self.currentPos = 0
        self.autoBookmark = Bookmark()
        self.autoBookmark.Load(self.currentBook)
        bookPartIndex = 0
        if os.path.exists(self.autoBookmark.BookPartName):
            idx = 0
            for bookPartName, bookPartDisplay, hash in self.currentBook.bookParts:
              if self.autoBookmark.BookPartName  == bookPartName:
                  bookPartIndex =  idx
                  break
              idx += 1
        
        self.SetCurrentBookPart(bookPartIndex)
        self.currentPos = self.autoBookmark.Position
    
    def GetCurrentMediaPosition(self):
        if self.audioPlayer.state() == audio.EPlaying:
          self.currentPos = self.audioPlayer.current_position()
        return self.currentPos

    def SetCurrentMediaPosition(self, pos):
          isPlaying = self.audioPlayer.state() == audio.EPlaying
          if isPlaying:
            if not self.isChangingPosition:
                self.isChangingPosition = 1
                self.audioPlayer.stop()
                self.audioPlayer.set_position(pos)
                self.Play()
                self.isChangingPosition = 0
          else:
	    self.currentPos = pos
          self.DrawPosition()	
	
    def About(self):
        fields = [
                         ( u'Application Name','text', u'Scheherazade' ),
                         ( u'Company','text', u'PlatySoft Pty Ltd' ),
                         ( u'Download Terms and conditions','text', u'www.PlatySoft.com.au' ),
                         ( u'Download Users manual','text', u'www.PlatySoft.com.au' ),
                         ( u'Download the latest version','text', u'www.PlatySoft.com.au' ),
                         ( u'Support','text', u'Support@PlatySoft.com.au' )
                      ]
        form = appuifw.Form(fields, appuifw.FFormAutoLabelEdit | appuifw.FFormDoubleSpaced)
        form.execute( )
        #self.aboutText = appuifw.Text()
        #appuifw.app.body=self.aboutCanvas

    def SelectBook(self):
        self.logWriter.Log("Selecting a book")
        self.logWriter.Log("There are %d books in the library:"%len(self.library.books))
        for book in self.library.books:
          self.logWriter.Log("   bookname: %s"%book.bookName)
        listOfBookNames = [u"%s"%book.bookName for book in self.library.books]
        self.logWriter.Log("Created List of books")
        index = appuifw.popup_menu(listOfBookNames, u"Select a book:")
        if index >= 0:
	    self.settings.currentBook = self.library.books[index].bookName
	    self.settings.Save()
	    self.LoadBook()
       
    def VolUp(self):
        if self.settings.volume < self.audioPlayer.max_volume():
          self.settings.volume+=1
          self.audioPlayer.set_volume(self.settings.volume)
          self.DrawVolume()
          self.settings.Save()

    def VolDown(self):
        if self.settings.volume > 0:
          self.settings.volume -= 1
          self.audioPlayer.set_volume(self.settings.volume)
          self.DrawVolume()
          self.settings.Save()

    def NextBookPart(self):
        currentBookPartIndex = self.GetCurrentBookPartIndex()
        if currentBookPartIndex < len(self.currentBook.bookParts) - 1:
            isPlaying = self.audioPlayer.state() == audio.EPlaying
            if isPlaying:
	        self.audioPlayer.stop()

    	    self.SetCurrentBookPart(currentBookPartIndex + 1)

            if isPlaying:
	        self.Play()
	    self.DrawBookPartName()
	    
    def GetCurrentBookPartIndex(self):
        return self.currentBook.currentBookPartIndex
        
    def PrevBookPart(self):
        currentBookPartIndex = self.GetCurrentBookPartIndex()
        if currentBookPartIndex > 0:
            isPlaying = self.audioPlayer.state() == audio.EPlaying
            if isPlaying:
	        self.audioPlayer.stop()
            
            self.SetCurrentBookPart(currentBookPartIndex - 1)

            if isPlaying:
	        self.Play()
	    self.DrawBookPartName()
    
    def Play(self):
        self.audioPlayer.set_volume(self.settings.volume)        
        self.audioPlayer.play(callback=self.endOfPlay)
    
    def SetCurrentBookPart(self, bookPartIndex):
        self.currentBook.currentBookPartIndex = bookPartIndex
        self.currentBook.currentBookPart, displayName, hash = self.currentBook.bookParts[bookPartIndex]
        if not os.path.exists(self.currentBook.currentBookPart):
	    appuifw.note(u"book part not found, starting from first part.")
            self.SetCurrentBookPart(0)
        self.audioPlayer.close()
        self.SetCurrentMediaPosition(0)
        self.audioPlayer = audio.Sound.open(self.currentBook.currentBookPart)
        self.currentBookpartDuration = self.audioPlayer.duration()
        self.DrawBookPartName()
        
        
    def endOfPlay(self, prevStat, newStat, error):
        if error == 0:
          if newStat == audio.EOpen and prevStat == audio.EPlaying:
            currentBookPartIndex = self.currentBook.currentBookPartIndex
            if currentBookPartIndex < len(self.currentBook.bookParts) - 1:        	    
                self.SetCurrentBookPart(currentBookPartIndex + 1)
	        self.Play()
            else:
                audio.say(u"Congradulations, you finished yet another book.")
        
    def PlayPause(self):
        if self.audioPlayer.state() == audio.EPlaying:
          self.GetCurrentMediaPosition()
          self.audioPlayer.stop()
          self.Rewind(self.settings.rewindOnPauseSeconds)
          self.SaveAutoBookmark()
        else:
          self.audioPlayer.set_position(self.currentPos)
          self.Play()
        
        
    def Rewind(self, seconds):
          pos = self.GetCurrentMediaPosition() - (seconds * 1000000)
          if pos < 0:
            if self.GetCurrentBookPartIndex() > 0:
                isPlaying = self.audioPlayer.state() == audio.EPlaying
	        self.SetCurrentBookPart(self.GetCurrentBookPartIndex()-1)
	        pos = self.currentBookpartDuration + pos
	        if pos < 0:
	            pos = 0
	        if isPlaying:
	            self.Play()
                self.SetCurrentMediaPosition(pos)     
            else:
	        pos = 0
                self.SetCurrentMediaPosition(pos)
          else:
            self.SetCurrentMediaPosition(pos)

    def Forward(self, seconds):
          pos = self.GetCurrentMediaPosition() + (seconds * 1000000)
          if pos>self.currentBookpartDuration:
	    if self.GetCurrentBookPartIndex() < len(self.currentBook.bookParts) - 1:
                isPlaying = self.audioPlayer.state() == audio.EPlaying
	        pos =  pos - self.currentBookpartDuration
	        self.SetCurrentBookPart(self.GetCurrentBookPartIndex()+1)
	        if pos>self.currentBookpartDuration:
	            pos = 0
	        if isPlaying:
	            self.Play()
                self.SetCurrentMediaPosition(pos)     
          else:          
            self.SetCurrentMediaPosition(pos)

    def close_canvas(self): 
        appuifw.app.body=self.old_body
        self.canvas=None
        appuifw.app.exit_key_handler=None

    def redraw(self,rect):
        if not self.Loading:
          self.canvas.clear(self.fieldcolor)
          self.DrawPosition()
          self.DrawVolume()
          self.DrawBookPartName()
      
    def MilliSecondToString(self, microSeconds):
      seconds = microSeconds / 1000000
      hours = seconds / 3600
      seconds -= (hours * 3600)
      minutes = seconds / 60
      seconds -= (minutes * 60)
      return "%02d:%02d:%02d"%(hours, minutes, seconds)

    def DrawText(self, text, yLoc):
        
        (textrect,shift,numberOfChars)=self.canvas.measure_text(text,font= self.font, maxwidth=self.screenWidth)
        fontHeight = textrect[3]-textrect[1]
        self.canvas.rectangle((0,yLoc,self.screenWidth, fontHeight + yLoc),fill=(192,192,128))
        if len(text)>numberOfChars:
            self.canvas.text((0,yLoc - textrect[1]),text[:numberOfChars] ,(0,0,0), self.font)
            self.canvas.text((0,yLoc + (fontHeight*1.1) - textrect[1]),text[numberOfChars:],(0,0,0), self.font)
        else:
            self.canvas.text((0,yLoc - textrect[1]),text,(0,0,0), self.font)


    def DrawPosition(self):
        self.GetCurrentMediaPosition()
        self.canvas.rectangle((0,self.screenTopMargin,self.screenWidth, 45),fill=(192,192,128))
                
        self.canvas.rectangle((self.screenTopMargin, 25,self.screenWidth - self.screenTopMargin, 45), fill = None, width = 3, outline=(96,96,64))
        if self.currentBookpartDuration > 0:
          gPos = int(self.currentPos * (self.screenWidth - 16) / self.currentBookpartDuration)
          self.canvas.rectangle((5 + 3, 25 + 3, 5 + 3 + gPos, 45 - 3), fill = (96,96,64))
        
        positionText=u"%s of %s"%(self.MilliSecondToString(self.currentPos), self.MilliSecondToString(self.currentBookpartDuration))
        textrect=self.canvas.measure_text(positionText, font= self.font)[0]
        self.canvas.text(((self.screenWidth - textrect[2] + textrect[0])/2, self.screenTopMargin - textrect[1]),positionText, (0,0,0), self.font)


    def DrawVolume(self):
      if not self.Loading:
        textrect=self.canvas.measure_text(u"V", font= self.font)[0]
        fontHeight = -(textrect[3] - textrect[1])
        
        self.canvas.rectangle((0,55,self.screenWidth, 75),fill=(192,192,128))
        self.canvas.text((5,55 - textrect[1]),u"Volume:",(0,0,0), self.font)
        
        volumeText=u"%s%s"%(u"\u25A0"*self.settings.volume, u"\u25A1"*(10-self.settings.volume))
        self.canvas.text((82,55 - textrect[1]),volumeText,(96,96,64), ('title',None,FONT_BOLD|FONT_ANTIALIAS))

    def DrawBookPartName(self): 
        if not self.Loading:
            writer = TextWriter(self.canvas)
            self.canvas.rectangle((5,85,235, 145),fill=(200,200,128))
            #self.canvas.rectangle((5,85,235, 145),width = 1, outline=(96,96,64))
            writer.render("%s"%self.currentBook.bookName, "normal", None, 30, [5,85,235, 145], fill=0x000000)
            self.canvas.rectangle((5,155,235, 200),fill=(192,192,128))
            bookPartFileName, bookPartDisplay, hash = self.currentBook.bookParts[self.currentBook.currentBookPartIndex]
            writer.render("%s"%bookPartDisplay, "normal", None, 30, [5,155,235, 200], fill=0x000000)
            self.canvas.rectangle((5,205,235, 230),fill=(192,192,128))
            
            if self.currentBookpartDuration > 0:
                self.canvas.rectangle((5,205,235, 230), fill = None, width = 3, outline=(96,96,64))
                gPos = int((self.currentBook.currentBookPartIndex+1) * (self.screenWidth - 16) / len(self.currentBook.bookParts))
                self.canvas.rectangle((5 + 3, 205 + 3, 5 + 3 + gPos, 230 - 3), fill = (96,96,64))
        
    def set_exit(self):
        self.SaveAutoBookmark()
        self.audioPlayer.stop()
        self.exitflag=1

    def SaveAutoBookmark(self):
        self.GetCurrentMediaPosition()
        self.autoBookmark.Position = self.currentPos
        self.autoBookmark.Save(self.currentBook)
        self.lastSavedbookmark = time.time()

    def RedrawAbout(self,rect):
        self.aboutCanvas.clear(self.fieldcolor)
        self.aboutCanvas.text((82,55),u"test",(0,0,0), (u'title',None,FONT_BOLD|FONT_ANTIALIAS))
        

    def run(self):
        appuifw.app.exit_key_handler=self.set_exit
        appuifw.app.title = u"Scheherazade"
        while not self.exitflag:
            self.DrawPosition()
            e32.ao_sleep(1)
            if time.time() - self.lastSavedbookmark > self.settings.autoBookmarkSaveInterval:
                self.SaveAutoBookmark()
        self.close_canvas()
        
cheherazade=Scheherazade()
cheherazade.run()
