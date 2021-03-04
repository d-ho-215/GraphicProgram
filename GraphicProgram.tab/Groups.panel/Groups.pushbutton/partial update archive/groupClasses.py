
class box:
    global doc, cdoc, levID, lev

    def draw(self, originX, originY):
        self.x = originX
        self.y = originY
        self.xw = self.x + self.width  #plus to make it draw to the right
        self.yh = self.y - self.height #minus to make it draw in the down direction
        
        #create XYZ points from basic coordinates
        self.p1 = XYZ(self.x, self.y, 0)
        self.p2 = XYZ(self.xw, self.y, 0)
        self.p3 = XYZ(self.xw, self.yh, 0)
        self.p4 = XYZ(self.x, self.yh, 0)
        
        #create Lines from XYZ points
        self.L1 = Line.CreateBound(self.p1, self.p2)
        self.L2 = Line.CreateBound(self.p2, self.p3)
        self.L3 = Line.CreateBound(self.p3, self.p4)
        self.L4 = Line.CreateBound(self.p4, self.p1)

        #if room, draw filled region, else draw detail lines
        if self.isRoom:
            self.cLoop = CurveLoop.Create(List[Curve]([self.L1, self.L2, self.L3, self.L4]))
            FilledRegion.Create(doc, filledRegionTypeID, revit.active_view.Id, List[CurveLoop]([self.cLoop]))
        else:
            self.cArray = CurveArray()
            self.cArray.Append(self.L1)
            self.cArray.Append(self.L2)
            self.cArray.Append(self.L3)
            self.cArray.Append(self.L4)
            
            cdoc.NewDetailCurveArray(revit.active_view, self.cArray)

class dRoom(box):
    def __init__(self, name, qyt, size, dept, maxWidth, maxHeight):
        self.name = name
        self.qty = int(qty)
        self.size = int(size)
        self.dept = dept
        if maxWidth:
            #print("init mW")
            self.mW = int(maxWidth)
        else:
            self.mW = 0
        if maxHeight:
            #print("init mH")
            self.mH = int(maxHeight)
        else:
            self.mH = 0
        self.x = 0
        self.xw = 0
        self.y = 0
        self.yh = 0
        self.height = 0
        self.width = 0
        self.isRoom = True
        
    def square(self):
        self.height = math.sqrt(self.size)
        self.width = self.height
        
    def rect(self):
        #print("rect()")
        if self.mW > 0:
            #print("mW True")
            if math.sqrt(self.size) <= self.mW:
                #print("mW greater than sqrt")
                self.square()
            else:
                #print("self.width = self.mW")
                self.width = self.mW
                self.height = self.size / self.width
        elif self.mH > 0:
            if math.sqrt(self.size) <= self.mH:
                self.square()
            else:
                self.height = self.mH
                self.width = self.size / self.height
        else:
            #print("self.square")
            self.square()
        #print("rect() finished")
        
    def label(self):
        #TextNote.Create(document, viewId, XYZ, text, typeId)
        self.textPt = XYZ(self.x, self.y + 10, 0)
        titleText = "{name}  \n[ {qty} @ {size} NSF ]".format(name = self.name, qty = self.qty, size = self.size)
        TextNote.Create(doc, revit.active_view.Id, self.textPt, titleText, textTypeID)

class group(box):
    def __init__(self, name, size = 0, maxWidth = 200, maxHeight = 300):
        self.rooms = []
        self.isRoom = False
        self.name = name
        self.size = int(size)
        self.mW = int(maxWidth)
        self.mH = int(maxHeight)
        self.x = 0
        self.xw = 0
        self.y = 0
        self.yh = 0
        self.height = maxHeight
        self.width = maxWidth
        self.xstart = 0
        self.ystart = 0
        self.margin = 10
        self.voffset = 20
        self.offset = 5

    def addroom(self, room):
        self.rooms.append(room)

    def setstarts(self):
        self.xstart = self.x + self.margin
        self.ystart = self.y - self.voffset

    def drawrooms(self):
        for room in self.rooms:
            room.draw(startx, starty)
            self.xstart = self.xstart + self.
            
