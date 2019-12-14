# -*- coding: utf-8 -*-
# Do not delete the following import lines
from visualization import *
from odbAccess import*
import xlwt
from abaqus import *
import displayGroupOdbToolset as dgo
from abaqusConstants import *
import xyPlot
import random  
def SSExtrac(ODBName,nodeSetName,GroupBox1,odbName,elementSetName,PICK,NODESETS,ELEMENTSETS):
    if GroupBox1=='RF'and NODESETS==True:
        if nodeSetName!=' ALL NODES':
            s=ODBName.split("/")
            odbName=s[-1]
            #odb = openOdb(path= ODBName)
            o=session.openOdb(name=odbName,readOnly=False)
            RefPointSet = o.rootAssembly.nodeSets[nodeSetName]
            session.linkedViewportCommands.setValues(_highlightLinkedViewports=False)
            session.xyDataListFromField(odb=o, outputPosition=NODAL, variable=(('RF', 
                NODAL, ((INVARIANT, 'Magnitude'), )), ('U', NODAL, ((INVARIANT, 
                'Magnitude'), )), ), nodeSets=(nodeSetName, ))
            # instanceL = 'partname'
            # inst = odb.rootAssembly.instances[instanceL]
            # nodesetname='nodeSetName'
            # nodeset =  inst.nodeSets[nodesetname]
            #########################此处可用来获的最大帧数-实时跟新图像##################################
            frames=o.steps['Step-1'].frames
            a=len(frames)
            session.viewports['Viewport: 1'].odbDisplay.setFrame(step=0, frame=a)
            print('The maximum frames now is %s !!!'%a)
            ##########################################################################################
            partname=RefPointSet.nodes[0][0].instanceName
            nodelabel=RefPointSet.nodes[0][0].label
            if len(partname)==0:
                xy1 = session.xyDataObjects['U:Magnitude PI: ASSEMBLY N: %s'% nodelabel]
                xy2 = session.xyDataObjects['RF:Magnitude PI: ASSEMBLY N: %s'% nodelabel]
            else:
                
                xy1 = session.xyDataObjects['U:Magnitude PI: %s N: %s'% (partname, nodelabel)]
                xy2 = session.xyDataObjects['RF:Magnitude PI: %s N: %s'% (partname, nodelabel)]

            xy3 = combine(xy1, xy2)
            if len(session.xyPlots)!=0:
                xyp = session.xyPlots['XYPlot-1']
            else:
                xyp = session.XYPlot('XYPlot-1')
            chartName = xyp.charts.keys()[0]
            chart = xyp.charts[chartName]
            c1 = session.Curve(xyData=xy3)
            chart.setValues(curvesToPlot=(c1, ), )
            session.viewports['Viewport: 1'].setValues(displayedObject=xyp)
            tmpName = xy3.name
            datakey=session.xyDataObjects.keys()
            if 'XYData-1' in datakey:
                session.xyDataObjects.changeKey(tmpName, 'XYData-2')
                del session.xyDataObjects['XYData-1']
            else:
                session.xyDataObjects.changeKey(tmpName, 'XYData-1')
                del session.xyDataObjects['XYData-2']
            del session.xyDataObjects['U:Magnitude PI: %s N: %s'% (partname, nodelabel)]
            del session.xyDataObjects['RF:Magnitude PI: %s N: %s'% (partname, nodelabel)]
            del session.xyDataObjects['U:Magnitude PI: ASSEMBLY N: %s'% nodelabel]
            del session.xyDataObjects['RF:Magnitude PI: ASSEMBLY N: %s'% nodelabel]
        else:
            print('Please reselect!!')



    