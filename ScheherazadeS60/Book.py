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
 
