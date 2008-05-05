class LogWriter:
	def __init__(self):
	  self.logFileName = "c:\\data\\Scheherazade\\Scheherazade.Log"
	 
	def Log(self, message):
	  logFile = open(self.logFileName, 'at')
	  logFile.write(message + "\n");
	  logFile.close()
  
