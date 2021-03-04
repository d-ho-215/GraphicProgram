__title__ = "Groups"
__doc__ = "Draw some groups"
__author__ = "Daniel Howard, Ballinger"

#from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Transaction
from Autodesk.Revit.DB import *
from Autodesk.Revit.Creation import *
from pyrevit import revit, DB
from System.Collections.Generic import List #import ILists type

import math
import csv
import os
from groupClasses import *


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

t = Transaction(doc, "Create Program Diagram")
t.Start()

xoffset = 2
yoffset = 2
ybreak = 20
origx = 0
origy = 0

for room in programData:
    name = room[0]
    qty = room[1]
    size = room[2]
    dept = room[3]
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
    dept.draw(origx, origy)
    for room in dept.rooms:
        room.rect()
        if room.qty > 1:
            for i in range(room.qty):
                room.draw(origx, origy)
                if i == 0:
                    room.label()
                origx += (room.height + xoffset)
            origx = 0
            origy -= (room.height + ybreak)
        else:
            room.draw(origx, origy)
            room.label()
            origy -= (room.height + ybreak)
    origx += dept.width + 5
    origy = 0

    
    #print(dR.name, dR.size, dR.dept, "mW= ", dR.mW, "mH= ", dR.mH, dR.width, dR.height)



t.Commit()
