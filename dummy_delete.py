from odbAccess import *
from abaqus import*
from abaqusConstants import*
from odbAccess import*
import numpy as np
import os, os.path, sys
from textRepr import *
from visualization import *
import displayGroupOdbToolset as dgo
import random 
import xyPlot

def dummy_delete(modelName,partName):
    p1 = mdb.models[modelName].parts[partName]
    session.viewports['Viewport: 1'].setValues(displayedObject=p1)
    p = mdb.models[modelName].parts[partName]
    p.deleteElement(elements=p.sets['DUMMY'])