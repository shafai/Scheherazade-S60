class MediaFile:
    def __init__(self):
        self.PlayableFileTypes = [".wav", ".mp3", ".m4b", ".m4a", ".wma", ".amr", ".acc", ".awb", ".flac"]
    def IsPlayable(self, filename):
        return os.path.splitext(filename)[1].lower() in self.PlayableFileTypes
