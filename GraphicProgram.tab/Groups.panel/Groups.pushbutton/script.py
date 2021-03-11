__title__ = "Graphic Program"
__doc__ = "Generate a graphic program from CSV data file."
__author__ = "Daniel Howard, Ballinger"

#from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Transaction
from Autodesk.Revit.DB import *
from Autodesk.Revit.Creation import *
from pyrevit import revit, DB
from pyrevit import forms
from System.Collections.Generic import List #import ILists type

import math
import csv
import os


#os.chdir('C:\\Users\\howar\\Documents\\MypyRevitExtensions\\Test Files')

forms.alert("Select CSV file with program data.", 
    sub_msg="Click OK to browse to file location", 
    title="Select CSV File",
    ok=True, 
    cancel=True, 
    exitscript=True)
csv_file = forms.pick_file(files_filter='CSV files | *.csv')

programCsv = open(csv_file)
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
filledRegionTypeDefaultID = filledRegionTypeCollector[0].Id

#create dictionary to store type IDs as values for type name key - allows selection based on dept / group name
filledRegionTypes = {}
frtc = FilteredElementCollector(doc).OfClass(DB.FilledRegionType)
for frt in frtc:
    frtname = frt.LookupParameter('Type Name').AsString()
    frtid = frt.Id
    filledRegionTypes[frtname] = frtid
    
#forms.alert(str(filledRegionTypes))

textTypes = {}
#textTypeCollector = list(FilteredElementCollector(doc).OfClass(DB.TextNoteType))
#textTypeID = textTypeCollector[0].Id
ttc = FilteredElementCollector(doc).OfClass(DB.TextNoteType)
for tt in ttc:
    ttname = tt.LookupParameter('Type Name').AsString()
    ttid = tt.Id
    textTypes[ttname] = ttid


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
        #not room would be a group
        if self.isRoom:
            self.cLoop = CurveLoop.Create(List[Curve]([self.L1, self.L2, self.L3, self.L4]))
            deptname = self.dept
            if deptname in filledRegionTypes:
                filledRegionTypeId = filledRegionTypes[deptname]
            else:
                filledRegionTypeId = filledRegionTypeDefaultID
            FilledRegion.Create(doc, filledRegionTypeId, revit.active_view.Id, List[CurveLoop]([self.cLoop]))
        else:
            self.cArray = CurveArray()
            self.cArray.Append(self.L1)
            self.cArray.Append(self.L2)
            self.cArray.Append(self.L3)
            self.cArray.Append(self.L4)
            
            cdoc.NewDetailCurveArray(revit.active_view, self.cArray)

class dRoom(box):
    def __init__(self, name, qty, size, dept, maxWidth, maxHeight):
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
        self.roomTextPt = XYZ(self.x, self.y + 14, 0)
        self.infoTextPt = XYZ(self.x, self.y + 6, 0)
        infoText = "[ {qty} @ {size} NSF ]".format(qty = self.qty, size = self.size)
        TextNote.Create(doc, revit.active_view.Id, self.roomTextPt, self.name, textTypes["GP Room Title"])
        TextNote.Create(doc, revit.active_view.Id, self.infoTextPt, infoText, textTypes["GP Room Info"])

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
        self.currentx = 0
        self.currenty = 0
        self.netarea = 0

    def addroom(self, room):
        self.rooms.append(room)

#    def setstarts(self):
#        self.xstart = self.x + self.margin
#        self.ystart = self.y - self.voffset
#        self.currentx = self.xstart
#        self.currenty = self.ystart

#    def drawrooms(self):
#        for room in self.rooms:
#            room.draw(currentx, currenty)
#            self.currentx = self.currentx + self.offset + room.width
            
    def label(self):
        #TextNote.Create(document, viewId, XYZ, text, typeId)
        self.textPt = XYZ(self.x, self.y + 20, 0)
        titleText = "{name} - {area} NSF".format(name = self.name, area = self.netarea)
        TextNote.Create(doc, revit.active_view.Id, self.textPt, titleText, textTypes["GP Dept Title"])
        
    def totalArea(self):
        for room in self.rooms:
            if room.qty > 1:
                netroomarea = room.size * room.qty
            else:
                netroomarea = room.size
            self.netarea += netroomarea
                
            



t = Transaction(doc, "Create Program Diagram")
t.Start()

xoffset = 2
yoffset = 2
ybreak = 20
yMroomBreak = 2 # for multiple room breaks
origx = 0
origy = 0

#generate room data structure from data pulled from csv file
for room in programData:
    name = room[0].upper()
    qty = room[1]
    size = room[2]
    dept = room[3].upper()
    maxWidth = room[4]
    maxHeight = room[5]
    
    if dept not in depts:
        depts[dept] = group(dept)
    
    dR = dRoom(name, qty, size, dept, maxWidth, maxHeight)
    depts[dept].addroom(dR)

"""
    if dR.qty > 1:
        for i in range(dR.qty):
            dR.draw(origx, origy)
            if i == 0:
                dR.label()
            origx += (dR.height + xoffset)
        origx = 0
        origy -= (dR.height + ybreak)
    else:
        
        dR.draw(origx, origy)
        dR.label()
        origy -= (dR.height + ybreak)
"""
for dept in depts.values():
    dept.totalArea()
    dept.draw(origx, origy)
    dept.label()
    rOrigx = origx + xoffset
    rOrigy = origy - ybreak
    maxRheight = 0
    for room in dept.rooms:
        room.rect()
#        if rOrigx + room.width + 5 >= origx + dept.width:
#            rOrigx = origx + xoffset
#            rOrigy -= maxRheight + ybreak
        if room.qty > 1:
            for i in range(room.qty):
                if i == 0:
                    room.draw(rOrigx, rOrigy)
                    room.label()
                elif rOrigx + (2 *room.width) + xoffset >= dept.xw:
                    rOrigx = dept.x + xoffset
                    rOrigy -= (room.height + yMroomBreak)
                    room.draw(rOrigx, rOrigy)
                else:
                    rOrigx += (room.width + xoffset)
                    room.draw(rOrigx, rOrigy)
        else:
            room.draw(rOrigx, rOrigy)
            room.label()
        rOrigx = dept.x + xoffset
        rOrigy -= (room.height + ybreak)

    origx += dept.width + 5
    origy = 0

    
    #print(dR.name, dR.size, dR.dept, "mW= ", dR.mW, "mH= ", dR.mH, dR.width, dR.height)



t.Commit()
