__title__ = "Multiple Rooms"
__doc__ = "Create mutiples of room based on quantity"
__author__ = "Daniel Howard, Ballinger"

#from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Transaction
from Autodesk.Revit.DB import *
from Autodesk.Revit.Creation import *
from pyrevit import revit, DB
from System.Collections.Generic import List #import ILists type

import math
import csv
import os


os.chdir('C:\\Users\\howar\\Documents\\MypyRevitExtensions\\Test Files')

programCsv = open('Test Program.csv')
programReader = csv.reader(programCsv)
programData = list(programReader)
programCsv.close()

#remove first line, since that's headers in the Excel / CSV file
programData.pop(0)

rooms = []
depts = {}

### Name, Quantity, Square Ft, Department, MaxWidth, MaxHeight

doc = __revit__.ActiveUIDocument.Document
cdoc = doc.Create

levID = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().FirstElementId()
lev = doc.GetElement(levID)

filledRegionTypeCollector = list(FilteredElementCollector(doc).OfClass(DB.FilledRegionType))
filledRegionTypeID = filledRegionTypeCollector[0].Id

textTypeCollector = list(FilteredElementCollector(doc).OfClass(DB.TextNoteType))
textTypeID = textTypeCollector[0].Id

class box:
    def __init__(self, name, size = 0, maxWidth = 0, maxHeight = 0, parent = None):
        global doc, cdoc, levID, lev
        self.parent = parent
        self.name = name
        self.mW = int(maxWidth)
        self.mH = int(maxHeight)
        self.x = 0
        self.xw = 0
        self.y = 0
        self.yh = 0
        self.height = 0
        self.width = 0
        if not size:
            if maxWidth and maxHeight:
                self.size = self.mW * self.mH
        self.isRoom = False
        
    def square(self):
        if self.isRoom:
            self.height = math.sqrt(self.size)
            self.width = self.height
        else:
            print("Can't be square, not a room, dummy.")
        
    def rect(self):
        if self.mW and self.mH:
            self.width = self.mW
            self.height = self.mH
        elif self.mW > 0:
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

    def setorigins(self, originX, originY):
        self.x = originX
        self.y = originY
    
    def draw(self):
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
            #create CurveLoop #CurveLooops needed for drawing filled regions
            #CurveLoop.Create(curves) #CurveLoop.Create(IList)
            self.cLoop = CurveLoop.Create(List[Curve]([self.L1, self.L2, self.L3, self.L4]))
            #FilledRegion.Create(document, typeId, viewId, boundaries) #FilledRegion.Create(Doucment, ElementId, ElementId, IList<CurveLoop>)
            FilledRegion.Create(doc, filledRegionTypeID, revit.active_view.Id, List[CurveLoop]([self.cLoop]))
        else:
            ###create CurveArray from Lines
            ###CurveArrays needed for drawing continuos detail lines
            self.cArray = CurveArray()
            self.cArray.Append(self.L1)
            self.cArray.Append(self.L2)
            self.cArray.Append(self.L3)
            self.cArray.Append(self.L4)
        
            #draw detail lines from CurveArray
            cdoc.NewDetailCurveArray(revit.active_view, self.cArray)

"""class dRoom(box):
    def __init__(self, name, qyt = 1, size, dept, maxWidth = None, maxHeight = None, parent = None):
        super().__init__(name, size, maxWidth, maxHeight)
        self.parent = parent
        self.qty = int(qty)
        self.dept = dept
        self.isRoom = True
        
    def label(self):
        #TextNote.Create(document, viewId, XYZ, text, typeId)
        self.textPt = XYZ(self.x, self.y + 5, 0)
        titleText = "{name} [ {qty} @ {size} NSF ]".format(name = self.name, qty = self.qty, size = self.size)
        TextNote.Create(doc, revit.active_view.Id, self.textPt, titleText, textTypeID)
"""
class group(box):
    def __init__(self, name, size = 0, maxWidth = 200, maxHeight = 300):
        super().__init__(name, size, maxWidth, maxHeight)
        self.rooms = []

    def addroom(self, room):
        self.rooms.append(room)



t = Transaction(doc, "Create Program Diagram")
t.Start()

xoffset = 2
yoffset = 2
ybreak = 20
origx = 0
origy = 0

b = box("a box", size = 500)
b.square()
b.setorigins(origx, origy)
b.draw()

"""
for room in programData:
    name = room[0]
    qty = room[1]
    size = room[2]
    dept = room[3]
    maxWidth = room[4]
    maxHeight = room[5]
    
    if dept not in depts:
        depts[dept] = group(name = dept, size = 0)
"""
"""
    dR = dRoom(name, qty, size, dept, maxWidth, maxHeight)
    dR.rect()
    dR.setorigins(origx, origy)
    dR.label()
    if dR.qty > 1:
        for i in range(dR.qty):
            dR.setorigins(origx, origy)
            dR.draw()
            origx += (dR.height + xoffset)
        origx = 0
        origy -= (dR.height + ybreak)
    else:
        dR.setorigins(origx, origy)
        dR.draw()
        origy -= (dR.height + ybreak)
"""
"""
for dept in depts.values():
    dept.draw()
    origx += dept.maxWidth + 5
"""
    
    #print(dR.name, dR.size, dR.dept, "mW= ", dR.mW, "mH= ", dR.mH, dR.width, dR.height)



t.Commit()
