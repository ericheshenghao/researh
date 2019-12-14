# -*- coding: mbcs -*-
# -*- coding: utf-8 -*-
# coding=gbk
from abaqus import*
from abaqusConstants import*
from odbAccess import*
import numpy as np
import os, os.path, sys
from textRepr import *
from visualization import *
import xlwt
import displayGroupOdbToolset as dgo
import random 
import xyPlot 
## 这个脚本用来提取损伤面积
def DAMAGE_Extrac(odbName,instancename,elementSets,variable,NFras,NFraF):
    s=odbName.split("/")
    odb=s[-1]
    o=session.openOdb(name=odb,readOnly=False)
    frames=o.steps['Step-1'].frames
    a=len(frames)
    session.viewports['Viewport: 1'].odbDisplay.setFrame(step=0, frame=a)
    print('The maximum frames now is %s !!!'%a) ##现在最大帧数为a
    
    inst = o.rootAssembly.instances['%s-1'%instancename]
    eleset =  inst.elementSets[elementSets]
    elenum = len(eleset.elements) 
    #node = inst.getNodeFromLabel(label=20)

    NFraB=1
    #NFraF=50
    NFraF=NFraF+1
    area=[]
    for i in range(NFraB,NFraF,NFras): #帧数范围 间隔
        labels,xyz= [], []
        area_single=0
        fop = frames[i].fieldOutputs
        DAMAGEC=fop['%s'%variable]
        DAMAGEC_val=DAMAGEC.getSubset(region=eleset)
        for v in DAMAGEC_val.values:
            if v.data > 0.1:
                labels.append(v.elementLabel)   ##得到单元的编号，算面积的前提
                #s=len(labels)
                #print(s)
                #alue1 = v.DAMAGEC
                #f1.write('%7s  %7s  %7s\n'%(i,value0,value1))
        pass
        for j in range(len(labels)):   
            con=eleset.elements[labels[j]-1].connectivity  
            for k in range(len(con)):
                node = inst.getNodeFromLabel(label=con[k]) ##从节点编号获得节点数据
                xyz.append(node.coordinates)
            pass              ##组装为矩阵
            if len(con)==3:
                x1 = xyz[0][0]
                y1 = xyz[0][1]           
                x2 = xyz[1][0]
                y2 = xyz[1][1]
                x3 = xyz[2][0]
                y3 = xyz[2][1]
                s=abs(((x1*y2-x2*y1)+(x2*y3-x3*y2)+(x3*y1-x1*y3))/2)
                area_single=s+area_single
            elif len(con)==4:
                x1 = xyz[0][0]
                y1 = xyz[0][1]           
                x2 = xyz[1][0]
                y2 = xyz[1][1]
                x3 = xyz[2][0]
                y3 = xyz[2][1]
                x4 = xyz[3][0]
                y4 = xyz[3][1]
                s=abs((x1*y2+x2*y3+x3*y1-(x1*y3+x2*y1+x3*y2))/2+(x1*y3+x3*y4+x4*y1-(x1*y4+x3*y1+x4*y3))/2)
                area_single=s+area_single
        area.append(area_single)
        milestone('Damage caculate process','frames',i,NFraF)
    print('The damage area of frame %s = %s  !!!'%( i,area[-1]))
    time=[]
    for i in range(NFraB,NFraF,NFras):
        time.append(frames[i].frameValue)
    xdata=np.array(time)
    ydata=np.array(area)
    data = zip(xdata,ydata)
    if len(session.xyPlots)!=0:
        xyp = session.xyPlots['XYPlot-1']
    else:
        xyp = session.XYPlot('XYPlot-1')
    chartName = xyp.charts.keys()[0]
    chart = xyp.charts[chartName]
    udata=session.XYData(data=data,name='udata')
    c1 = session.Curve(xyData=udata)
    chart.setValues(curvesToPlot=(c1, ), )
    session.viewports['Viewport: 1'].setValues(displayedObject=xyp)
    