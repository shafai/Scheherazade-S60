class MediaFile:
    def __init__(self):
        self.PlayableFileTypes = [".wav", ".mp3", ".m4b", ".m4a", ".wma", ".amr", ".acc", ".awb", ".flac"]
        self.settings = Settings()
        
    def IsPlayable(self, filename):
        return os.path.splitext(filename)[1].lower() in self.PlayableFileTypes and filename.find(self.settings.tagFileNameBase) == -1
