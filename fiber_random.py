# -*- coding: mbcs -*-
# Do not delete the following import lines
# import displayGroupMdbToolset as dgm
from abaqus import *
from abaqusConstants import *
import __main__
import math
import section
import regionToolset
import numpy as np
import random 

lf=10
number=2000
Nx=400
Ny=100
i=1
arr=[]
arr1=[]
arr2=[]
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)

# x=random.sample(range(0, Nx), Nx)
# x.sort(reverse=False)
# y=random.sample(range(0, Ny), Ny)
# y.sort(reverse=False)
flag=[]
x0=0
y0=0
while i <number:
    
    if flag==1:
        if x0<Nx-1 and y0<Ny-1:
            x0=x0+0.5
            y0=y0
        elif x0>Nx-1.5 and y0<Ny-1:
            x0=1
            y0=y0+0.5
        elif x0<Nx-1 and y0>Ny-1:
            x0=1
            y0=1
    else:
        x0=random.random()*Nx
        y0=random.random()*Ny
    flag=[]
    
    a=2*math.pi*random.random()
    a1=math.cos(a)
    while abs(a1)<0.85:
        a=2*math.pi*random.random()
        a1=math.cos(a)

    a2=math.sin(a)
    x1=x0+lf*a1
    y1=y0+lf*a2
    if (x1>Nx-1 or x1<1 or y1>Ny-1 or y1<1 or x0>Nx-1 or x0<1 or y0>Ny-1 or y0<1):
        continue
    n=len(arr)/2
    arr_n=0
    for j in range(0,n):
        p1=np.array([arr[arr_n],arr[arr_n+1]])
        p2=np.array([arr1[arr_n],arr1[arr_n+1]])
        p3=(x0,y0)
        p4=(x1,y1)
        p5=p3-p1
        p6=p3-p2
        p7=p4-p1
        p8=p4-p2
        p9=math.hypot(p5[0],p5[1])
        p10=math.hypot(p6[0],p6[1])
        p11=math.hypot(p7[0],p7[1])
        p12=math.hypot(p8[0],p8[1])
        Point_x0  = x0
        Point_y0  = y0
        Point_x1  = x1
        Point_y1  = y1
        line_x0  = arr[arr_n]
        line_y0  = arr[arr_n+1]
        line_x1  = arr1[arr_n]
        line_y1  = arr1[arr_n+1]
        d0,d1=10,10
        if line_y1 - line_y0 == 0:
            d0=math.fabs(Point_y0 - line_y0)
            d1=math.fabs(Point_y1 - line_y0)
        k1=line_y1-line_y0
        k2=line_x0-line_x1
        k3=line_x1*line_y0-line_x0*line_y1
        d1=(math.fabs(k1*Point_x0+k2*Point_y0+k3))/(math.pow(k1*k1+k2*k2,0.5))
        d2=(math.fabs(k1*Point_x1+k2*Point_y1+k3))/(math.pow(k1*k1+k2*k2,0.5))

        k4=y1-y0
        k5=x0-x1
        k6=x1*y0-x0*y1
        d3=(math.fabs(k4*line_x0+k5*line_y0+k6))/(math.pow(k4*k4+k5*k5,0.5))
        d4=(math.fabs(k4*line_x1+k5*line_y1+k6))/(math.pow(k4*k4+k5*k5,0.5))

        # if d1<1 or d2<1 or d3<1 or d4<1:
        #     flag=1
        #     continue
        if p9<1 or p10<1 or p11<1 or p12<1:
            flag=1
            continue
        arr_n=arr_n+2
    if flag==1:
        continue
    arr.extend([x0,y0])
    arr1.extend([x1,y1])
    arr2.extend([x0,y0,x1,y1])
    s.Line(point1=(x0, y0), point2=(x1, y1))
    i+=1
    milestone('Caculate process','number',i,number)
## 修改路径
# File_path='C:/temp/'
# file = open(File_path+'fiber_coord','w+')
# EL=0
# for i in range(0,len(arr2),4):
#     print>>file,"%5s, %5s,  %5s,  %5s" % (arr2[0+EL],arr2[1+EL],arr2[2+EL],arr2[3+EL])
#     EL=EL+4
# file.close()    
p = mdb.models['Model-1'].Part(name='fiber', dimensionality=TWO_D_PLANAR, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['fiber']
p.BaseWire(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['fiber']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
del mdb.models['Model-1'].sketches['__profile__']
##############生成平板
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(0.0, 0.0), point2=(400.0, 100.0))
p = mdb.models['Model-1'].Part(name='matrix', dimensionality=TWO_D_PLANAR, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['matrix']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['matrix']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
del mdb.models['Model-1'].sketches['__profile__']



