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
