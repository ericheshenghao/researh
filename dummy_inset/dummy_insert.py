# -*- coding: utf-8 -*-
# coding=gbk
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
import shutil
import re

def dummy_inset(modelName, partName):
    def find_key(file,key_word):
            flag=0
            with open(file,'r+') as f:
                for index,line in enumerate(f.readlines()):
                    if key_word in line:
                        flag=1
                        result = "%s在文件的第%s行"%(key_word,index+1)
                        print(result)
                        break
                    else:
                        result = "未在文件中发现%s"%(key_word)
            return(flag,index)


    dir=[]
    cur_dir = os.getcwd()
    cur_d = cur_dir.split("\\")
    cur = ""
    for i in range(len(cur_d)):
        cur = cur+cur_d[i]+'/'

    Model = modelName
    modelname = modelName+".inp"
    dummy_model_name = modelName+"-dummy"
    #### 生成
    mdb.Job(name=Model, model=Model, description='', type=ANALYSIS, 
            atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
            memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
            explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
            modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
            scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=1, 
            numGPUs=0)
    mdb.jobs[Model].writeInput(consistencyChecking=OFF)

    ### 重写入dummy model
    mdb.ModelFromInputFile(name=dummy_model_name, 
        inputFileName=cur+modelname)
    a = mdb.models[dummy_model_name].rootAssembly
    session.viewports['Viewport: 1'].setValues(displayedObject=a)

    #### 查询重新生成的dummy单元的数据并写入 inp文件
    lenth = len(mdb.models[dummy_model_name].parts['PART-1-PICKGEOEDGES'].allSets["COHEELEM-0ALL"].elements)
    for i in range(lenth):
        m = mdb.models[dummy_model_name].parts['PART-1-PICKGEOEDGES'].allSets["COHEELEM-0ALL"].elements[i]
        label_num =m.label+lenth
        connect = m.connectivity
        dir.append("%d,%d,%d,%d,%d" %(label_num,connect[0]+lenth+2,connect[1]+lenth+2,connect[2]+lenth+2,connect[3]+lenth+2))

    key_word = "*Element, type=COH2D4"

    flag,index=find_key(modelname,key_word)
    line1 = "*Element, type=CPE4P"
    line2 = "*Elset, elset=dummy, generate"
    line3  = "%d,  %d,  %d" %(label_num-lenth+1,label_num,1)
    dir.insert(0,line1)
    dir.append(line2)
    dir.append(line3)
    with open(modelname,'r+') as fp:
        lines = []
        for line in fp:                 
            lines.append(line)
    if flag:
        for i in range(lenth+3):
            lines.insert(index+i+lenth+1, dir[i]+'\n') #在第 LINE-1 行插入
    s = ''.join(lines)
    with open(modelname, 'w') as fp:
        fp.write(s)
    try:
        del mdb.models[dummy_model_name]
    except:
        pass

    #### 将 dummyinp 重生成
    mdb.ModelFromInputFile(name=dummy_model_name, 
        inputFileName=cur + modelname)
    a = mdb.models[dummy_model_name].rootAssembly
    session.viewports['Viewport: 1'].setValues(displayedObject=a)
