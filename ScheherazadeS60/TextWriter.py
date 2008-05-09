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
