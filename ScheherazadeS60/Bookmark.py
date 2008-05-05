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

