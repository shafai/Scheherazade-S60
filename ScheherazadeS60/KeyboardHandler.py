class KeyboardHandler:
	def __init__(self):
	    self.lastKeyPressed = 0
	    self.bindings = {}
	    self.logWriter = LogWriter()
	    
	def KeyEventHandler(self, arg):
	    scanCode = arg['scancode']
	    if self.bindings.has_key(scanCode):
	        if arg['type'] == appuifw.EEventKeyDown:
	            if self.bindings[scanCode][0] != None:
	                self.bindings[scanCode][0]()
	        if arg['type'] == appuifw.EEventKey:
	            if self.bindings[scanCode][1] != None:
	                self.bindings[scanCode][1]()
	        if arg['type'] == appuifw.EEventKeyUp:
	            if self.bindings[scanCode][2] != None:
	                self.bindings[scanCode][2]()
	                
	def Bind(self, keyCode, pressedCallback = None, keptPressedCallback = None, releasedCallback = None):
	    self.bindings[keyCode] = (pressedCallback, keptPressedCallback, releasedCallback)
