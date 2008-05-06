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
import traceback

#{*Import TextWriter.py*}
#{*Import MediaFile.py*}
#{*Import Library.py*}
#{*Import Book.py*}
#{*Import IniReader.py*}
#{*Import LogWriter.py*}
#{*Import Settings.py*}
#{*Import SettinsEditForm.py*}
#{*Import Bookmark.py*}

class KeyboardHandler:
	def __init__(self):
	    self.lastKeyPressed = 0
	    self.bindings = []
	    self.logWriter = LogWriter()
	    
	def KeyEventHandler(self, arg):
	    for (keyCode, pressCallable, keptPressingCallable, releaseCallable) in self.bindings:
	        if keyCode == arg['scancode']:
	            if arg['type'] == appuifw.EEventKeyDown:
	                if pressCallable != None:
	                    pressCallable()
	            if arg['type'] == appuifw.EEventKey:
	                if keptPressingCallable != None:
	                    keptPressingCallable()
	            if arg['type'] == appuifw.EEventKeyUp:
	                if releaseCallable != None:
	                    releaseCallable()
	                
	def Bind(self, keyCode, pressedCallback = None, keptPressedCallback = None, releasedCallback = None):
	    self.bindings.append((keyCode, pressedCallback, keptPressedCallback, releasedCallback))
                  

class Scheherazade:

    def __init__(self):
        self.font = ('normal',None,FONT_BOLD|FONT_ANTIALIAS)
        self.currentPos = 0
        self.keyboardHandler = KeyboardHandler()
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
        self.canvas=appuifw.Canvas(redraw_callback=self.redraw, event_callback=self.keyboardHandler.KeyEventHandler)
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
        
        #self.canvas.bind(EKey6,lambda:self.Forward(self.settings.longRewindSeconds))
        self.keyboardHandler.Bind(EScancode6,lambda:self.Forward(self.settings.longRewindSeconds))
        self.keyboardHandler.Bind(EScancode4,lambda:self.Rewind(self.settings.longRewindSeconds))
        self.keyboardHandler.Bind(EScancode9,lambda:self.NextBookPart())
        self.keyboardHandler.Bind(EScancode7,lambda:self.PrevBookPart())
        self.keyboardHandler.Bind(EScancodeSelect, None, None, lambda:self.PlayPause())
        self.keyboardHandler.Bind(EScancodeRightArrow,lambda:self.Forward(self.settings.rewindSeconds))
        self.keyboardHandler.Bind(EScancodeUpArrow,lambda:self.VolUp())
        self.keyboardHandler.Bind(EScancodeLeftArrow,lambda:self.Rewind(self.settings.rewindSeconds))
        self.keyboardHandler.Bind(EScancodeDownArrow,lambda:self.VolDown())
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
       try:
          listOfBookNames = [unicode(book.bookName) for book in self.library.books]
          index = appuifw.popup_menu(listOfBookNames, u"Select a book:")
          if index >= 0:
	      self.settings.currentBook = self.library.books[index].bookName
	      self.settings.Save()
          self.LoadBook()
       except:
          self.logWriter.Log("\n".join(traceback.format_exception(*sys.exc_info())))

       
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

    def run(self):
        appuifw.app.exit_key_handler=self.set_exit
        appuifw.app.title = u"PlatySoft's Scheherazade"
        while not self.exitflag:
            self.DrawPosition()
            e32.ao_sleep(1)
            if time.time() - self.lastSavedbookmark > self.settings.autoBookmarkSaveInterval:
                self.SaveAutoBookmark()
        self.close_canvas()

cheherazade=Scheherazade()
cheherazade.run()
