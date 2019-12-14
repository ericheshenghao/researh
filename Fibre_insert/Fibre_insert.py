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
import re
import PolarisCDP_Functions
def Fibre_insert(modelName,partName,variable,uel_mode,concrete,diameter,thick,interact):
    os.chdir(r"c:\temp")
    Model=modelName    
    m=mdb.models[Model]
    p=m.parts[partName]
    a1 = mdb.models[modelName].rootAssembly
    key_len=len(a1.allInstances.keys())
    for i in range(key_len):
        del a1.features[a1.allInstances.keys()[0]]
    a1.Instance(name=partName + '-1', part=p, dependent=ON)
    e=p.edges
    edges=variable
    Nodes_dic={}
    coord=[]
    B21=[]
    Nodes_len=len(p.nodes)
    print ('[info] 检查插入节点')
    
    for i in range(len(e)):
        flag=[]
        for j in range(len(edges)):
            if i==edges[j].index:
                flag=1
        if flag==1:
            continue
        Nodes_tep={}
        key=[]
        B21_element=[]
        Nodes=e[i].getNodes()  ## 第i条边的所有节点
        if Nodes==None:
            print ('错误:未进行网格划分')
        for j in range(len(Nodes)):  ## 第0-j个节点
            coord=[]
            Nodes_num=Nodes[j]   ## 第0个节点
            for k in range(len(Nodes_num.coordinates)-1):
                label=int(Nodes_num.label)
                coord.append(Nodes_num.coordinates[k])
            Nodes_dic[label+Nodes_len]=coord ##得到所有边上的所有节点,这个坐标不能用，会出错！！
            Nodes_tep[label]=coord 
            Nodes_sot=sorted(Nodes_tep.items(),key=lambda item:item[1]) #排序好的节点
        for l in range(len(Nodes_sot)-1):
            B21_element.append(Nodes_sot[l][0])
            B21_element.append(Nodes_sot[l+1][0])
        B21+=B21_element  ##B21为所有纤维节点
    ########################## Nodes_dic-所有节点坐标 B21-所有纤维节点  生成inp文件
    a = mdb.models[Model].rootAssembly
    mdb.Job(name='Job-99', model=Model, description='', type=ANALYSIS, 
        atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
        memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
        modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
        scratch='', resultsFormat=ODB, parallelizationMethodExplicit=DOMAIN, 
        numDomains=1, activateLoadBalancing=False, multiprocessingMode=DEFAULT, 
        numCpus=1, numGPUs=0)
    mdb.jobs['Job-99'].writeInput(consistencyChecking=OFF)
    del mdb.jobs['Job-99']

    ###############################修改input部分
    
    File_path='C:/temp/'
    Inp_name='job-99.inp'
    NEW_INPNAME='TestNew1.inp'
    with open(File_path+Inp_name,'r') as Ori_inp:
        #读取节点编号及坐标信息
        Node_dic={}

        Inp_line=Ori_inp.readlines()
        #Inp_val辅助判断
        #结点存储为字典格式，结点号为索引，其索引内容为结点坐标
        Inp_value=0

        for i in range(len(Inp_line)):
            if Inp_line[i].startswith('*Node'):
                Inp_value+=1
            if Inp_line[i].startswith('*Element'):
                Inp_value+=1
                break
            if Inp_value==1:
                try:
                    Node1=[float(cor) for cor in Inp_line[i+1].split(',')]
                    Node1[0]=int(Node1[0])
                    Node_dic[Node1[0]]=[]
                    Node_dic[Node1[0]].append(Node1[1])
                    Node_dic[Node1[0]].append(Node1[2])
                except:pass
        key_list=Nodes_dic.keys()
        for i in range(len(key_list)):
            if len(Node_dic)==0:
                print('请先进行装配')
            key=key_list[i]
            Nodes_dic[key][0]=Node_dic[key-Nodes_len][0]
            Nodes_dic[key][1]=Node_dic[key-Nodes_len][1]

        Element_dic_FOUR={}
        Element_dic_THREE={}          
        Inp_value=0
        EL_FOUR=[]
        EL_THR=[]
        for i in range(len(Inp_line)):
            if Inp_line[i].startswith('*Element'):
                Inp_value+=1
            if Inp_value==1:
                try:
                    Node1=[int(cor) for cor in Inp_line[i+1].split(',')]
                    if len(Node1)==5:
                        Element_dic_FOUR[Node1[0]]=[]
                        EL_FOUR.append(Node1[0])
                        Element_dic_FOUR[Node1[0]].extend(Node1[1:5])                           
                    elif len(Node1)==4:
                        Element_dic_THREE[Node1[0]]=[]
                        EL_THR.append(Node1[0])
                        Element_dic_THREE[Node1[0]].extend(Node1[1:4])   #此处用extend更好
                except:
                    Inp_value=0
        ##生成新坐标

        key_list = Element_dic_FOUR.keys()
        key_list1 = Element_dic_THREE.keys()
        endnum=max(key_list)+1
        if len(Element_dic_THREE)!=0:
            endnum1=max(key_list1)+1
            if endnum1>endnum:
                endnum=endnum1
        #生成纤维单元
        Element_B21={}
        num=0
        for i in range(len(B21)/2):
            a=int(B21[num])+Nodes_len
            b=int(B21[num+1])+Nodes_len
            Element_B21[endnum+i]=[a,b]
            num+=2

        key_list = Element_B21.keys()
        endnum=max(key_list)+1
        #生成coh单元
        Element_coh={} 
        num=0
        for i in range(len(B21)/2):
            a = int(B21[num])
            b = int(B21[num+1])
            c = int(B21[num])+Nodes_len
            d = int(B21[num+1])+Nodes_len
            Element_coh[endnum+i]=[d,c,a,b]
            num+=2
        endnum=endnum+i+1
        #生成dummmy单元
        Element_dummmy={}
        num=0
        if uel_mode:
            for i in range(len(B21)/2):
                a = int(B21[num])
                b = int(B21[num+1])
                c = int(B21[num])+Nodes_len
                d = int(B21[num+1])+Nodes_len
                Element_dummmy[endnum+i]=[d,c,a,b]
                num+=2

        ######生成新的inp文件
        File_path='C:/temp/'
        outfile=open(File_path+NEW_INPNAME,'w+')
        outfile.close()
        with open(File_path+NEW_INPNAME,'w') as outfile:
        #文件头的书写
            Heading=[]
            Heading.append('*Heading')
            Heading.append('** Job name: TestNew1 Model name: TestNew1')
            Heading.append('** Generated by: Abaqus/CAE 6.14-1')
            Heading.append('**')
            Heading.append('** PARTS')
            Heading.append('**')
            Heading.append('*Part, name=coh_insert')
            Heading.append('*Node')
            #Part相关节点及单元信息写入
            #NODE
            for i in range(len(Heading)):
                # print(Heading[i],file=outfile)
                print>>outfile,Heading[i]

            #NODE
            #字典按照keys大小排
            NODE_OUTPUT=sorted(Node_dic.items(),key=lambda e:e[0])
            for i in range(len(NODE_OUTPUT)):
                print>>outfile, "%9d,   %9f,   %9f" % (NODE_OUTPUT[i][0],NODE_OUTPUT[i][1][0],NODE_OUTPUT[i][1][1])
            #     print("%9d, %9f, %9f" %(NODE_OUTPUT[i][0],NODE_OUTPUT[i][1][0],NODE_OUTPUT[i][1][1]),file=outfile)
            NODE_OUTPUT=sorted(Nodes_dic.items(),key=lambda e:e[0])
            for i in range(len(NODE_OUTPUT)):
                print>>outfile, "%9d,   %9f,   %9f" % (NODE_OUTPUT[i][0],NODE_OUTPUT[i][1][0],NODE_OUTPUT[i][1][1])

            #生成CPS4R或CPS3
            if len(EL_THR)!=0:
                CO_TYPE='*Element, type=CPS3'
                print>>outfile,CO_TYPE
                NODE_OUTPUT1=sorted(Element_dic_THREE.items(),key=lambda e:e[0])
                for i in range(len(EL_THR)):
                    print>>outfile,"%5d, %5d, %5d, %5d" %(NODE_OUTPUT1[i][0],NODE_OUTPUT1[i][1][0],NODE_OUTPUT1[i][1][1],NODE_OUTPUT1[i][1]\
                        [2])
            CO_TYPE='*Element, type=CPS4'
            print>>outfile,CO_TYPE
            NODE_OUTPUT=sorted(Element_dic_FOUR.items(),key=lambda e:e[0])
            for i in range(len(EL_FOUR)):
                print>>outfile,"%5d, %5d, %5d, %5d, %5d" %(NODE_OUTPUT[i][0],NODE_OUTPUT[i][1][0],NODE_OUTPUT[i][1][1],NODE_OUTPUT[i][1]\
                    [2],NODE_OUTPUT[i][1][3])

            ##生成B21单元
            CO_TYPE='*Element, type=B21'
            print>>outfile,CO_TYPE
            NODE_OUTPUT=sorted(Element_B21.items(),key=lambda e:e[0])
            for i in range(len(NODE_OUTPUT)):
                print>>outfile,"%5d, %5d, %5d" %(NODE_OUTPUT[i][0],NODE_OUTPUT[i][1][0],NODE_OUTPUT[i][1][1])

            ##生成COH单元
            CO_TYPE='*Element, type=COH2D4, ELSET=CO_SET'
            if uel_mode:
                CO_TYPE='*Element, type=COH2D4'
            print>>outfile,CO_TYPE
            NODE_OUTPUT=sorted(Element_coh.items(),key=lambda e:e[0])
            for i in range(len(NODE_OUTPUT)):
                print>>outfile,"%5d, %5d, %5d, %5d, %5d" %(NODE_OUTPUT[i][0],NODE_OUTPUT[i][1][0],NODE_OUTPUT[i][1][1],NODE_OUTPUT[i][1]\
                    [2],NODE_OUTPUT[i][1][3])

            ##生成dummy单元
            if uel_mode:
                CO_TYPE='*Element, type=CPE4P,ELSET=dummy'
                print>>outfile,CO_TYPE
                NODE_OUTPUT=sorted(Element_dummmy.items(),key=lambda e:e[0])
                for i in range(len(NODE_OUTPUT)):
                    print>>outfile,"%5d, %5d, %5d, %5d, %5d" %(NODE_OUTPUT[i][0],NODE_OUTPUT[i][1][0],NODE_OUTPUT[i][1][1],NODE_OUTPUT[i][1]\
                        [2],NODE_OUTPUT[i][1][3])

            #写入cohesive单元集合
            COINP_SET='*Elset, elset=CO_SET, generate'
            print>>outfile,COINP_SET
            key_list = Element_coh.keys()
            print>>outfile,"%5d, %5d,%5d"%(min(key_list),max(key_list),1)
            #写入B21单元集合
            COINP_SET='*Elset, elset=fiber, generate'
            print>>outfile,COINP_SET
            key_list = Element_B21.keys()
            print>>outfile,"%5d, %5d,%5d"%(min(key_list),max(key_list),1)
            ##打印基体单元
            COINP_SET='*Elset, elset=matrix, generate'
            print>>outfile,COINP_SET
            print>>outfile,"%5d, %5d,%5d"%(1,min(key_list)-1,1)
            ##分开打印


            ##打印结尾部分
            end=['*End Part','**','**','** ASSEMBLY','**','*Assembly, name=Assembly','**','*Instance, name=coh_insert-1, part=coh_insert',\
                '*End Instance','**','*End Assembly']
            for i in end:
                print>>outfile,i
    outfile.close()
    Ori_inp.close()
    ## 删除掉job-99.inp文件
    Inp_name='job-99.inp'
    os.remove(File_path+Inp_name)
    ## 检查目录中是否有TestNew1 mdb存在
    if 'TestNew1' in mdb.models.keys():
        del mdb.models['TestNew1']
    else:
        pass
    mdb.ModelFromInputFile(name='TestNew1', inputFileName='C:/temp/TestNew1.inp')
    a = mdb.models['TestNew1'].rootAssembly
    print ('[info] 生成新模型')
    print ('[info] Finish')
    session.viewports['Viewport: 1'].setValues(displayedObject=a)
    ### 生成cps3集合
    elements=[]
    p = mdb.models['TestNew1'].parts['COH_INSERT']
    ele = p.elements
    try:
        for i in range(len(EL_THR)):
            elements.append(ele[EL_THR[i]-1:EL_THR[i]])
        p.Set(elements=elements, name='cps3')
    except:
        print("没有cps3单元不生成集合")
    ### 生成cps4集合
    elements=[]
    for i in range(len(EL_FOUR)):
        elements.append(ele[EL_FOUR[i]-1:EL_FOUR[i]])
    p.Set(elements=elements, name='cps4')
    ### 再生成inp文件
    mdb.Job(name='TestNew1', model='TestNew1', description='', type=ANALYSIS, 
        atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
        memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
        modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
        scratch='', resultsFormat=ODB, parallelizationMethodExplicit=DOMAIN, 
        numDomains=1, activateLoadBalancing=False, multiprocessingMode=DEFAULT, 
        numCpus=1, numGPUs=0)
    mdb.jobs['TestNew1'].writeInput(consistencyChecking=OFF)
    del mdb.jobs['TestNew1']
    material_insert(concrete,diameter,modelName,partName,variable,uel_mode,thick,interact)
    os.chdir(r"d:\temp")
def material_insert(concrete,diameter,modelName,partName,variable,uel_mode,thick,interact):
    try:
        if "c:/Users/Hasee/abaqus_plugins/POLARIS_CDP-c" not in os.sys.path:os.sys.path.append(
            "c:/Users/Hasee/abaqus_plugins/POLARIS_CDP-c")
        ####混凝土材料
        mat_dic = {'C15':1,'C20':2,'C25':3,'C30':4,'C35':5,'C40':6,'C45':7,'C50':8,'C55':9,'C60':10,'C65':11,'C70':12,'C75':13,'C80':14}
        material_para = [[2.36E-09,22000,10,1.27],[2.37E-09,25500,13.4,1.54],[2.38E-09,28000,16.7,1.78],[2.39E-09,30000,20.1,2.01]\
            ,[2.39E-09,31500,23.4,2.2],[2.4E-09,32500,26.8,2.39],[2.41E-09,33500,29.6,2.51],[2.42E-09,34500,32.4,2.64]\
                ,[2.43E-09,35500,35.3,2.74],[2.44E-09,36000,38.5,2.85],[2.45E-09,36500,41.5,2.93],[2.46E-09,37000,44.5,2.99]\
                    ,[2.47E-09,37500,47.4,3.05],[2.48E-09,38000,50.2,3.11]]
        m=material_para[mat_dic[concrete]]
        PolarisCDP_Functions.PolarisCDP_Functions().createMaterial(
            matName=concrete, dwz='mm/s/T - (N/MPa)', den=m[0], 
            elas=m[1], pos=0.2, fc=m[2], ft=m[3], p1=38, p2=0.1, p3=1.16, 
            p4=0.66667, p5=1E-05, wt=0, wc=1, fcuStrainType=1, fcStrain=1E-05, 
            ftStrain=1E-05, fcInitial=0.4, ftInitial=0.8, dfc=0.05, damageType=1, 
            ratioc=0.7, ratiot=0.1, maxDamage=0.9)
        mdb.models['TestNew1'].HomogeneousSolidSection(name='concrete', material=concrete, 
            thickness=thick)
        p = mdb.models['TestNew1'].parts['COH_INSERT']
        region = p.sets['MATRIX']
        p = mdb.models['TestNew1'].parts['COH_INSERT']
        p.SectionAssignment(region=region, sectionName='concrete', offset=0.0, 
            offsetType=MIDDLE_SURFACE, offsetField='', 
            thicknessAssignment=FROM_SECTION)
    except:
        print("基体材料属性缺失")
    ####纤维材料
    mdb.models['TestNew1'].Material(name='fiber')
    mdb.models['TestNew1'].materials['fiber'].Elastic(table=((210000.0, 0.3), ))
    mdb.models['TestNew1'].materials['fiber'].Plastic(table=((634.0, 0.0), (847.0, 
        0.1)))
    print(diameter)
    mdb.models['TestNew1'].CircularProfile(name='Profile-1', r=diameter)
    mdb.models['TestNew1'].BeamSection(name='fiber', integration=DURING_ANALYSIS, 
        poissonRatio=0.0, profile='Profile-1', material='fiber', 
        temperatureVar=LINEAR, consistentMassMatrix=True)
    mdb.models['TestNew1'].sections['fiber'].TransverseShearBeam(
        scfDefinition=COMPUTED, slendernessCompensation=COMPUTED, k23=None, 
        k13=None)
    p = mdb.models['TestNew1'].parts['COH_INSERT']
    region = p.sets['FIBER']
    p = mdb.models['TestNew1'].parts['COH_INSERT']
    p.SectionAssignment(region=region, sectionName='fiber', offset=0.0, 
        offsetType=MIDDLE_SURFACE, offsetField='', 
        thicknessAssignment=FROM_SECTION)
    p = mdb.models['TestNew1'].parts['COH_INSERT']
    region=p.sets['FIBER']
    p = mdb.models['TestNew1'].parts['COH_INSERT']
    p.assignBeamSectionOrientation(region=region, method=N1_COSINES, n1=(0.0, 0.0, 
        -1.0))
    a = mdb.models['TestNew1'].rootAssembly
    a.regenerate()
    session.viewports['Viewport: 1'].setValues(displayedObject=a)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(
        adaptiveMeshConstraints=ON, optimizationTasks=OFF, 
        geometricRestrictions=OFF, stopConditions=OFF)
    mdb.models['TestNew1'].StaticStep(name='Step-1', previous='Initial', 
        maxNumInc=5000, initialInc=0.001, minInc=1e-12, nlgeom=ON)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Step-1')
    mdb.models['TestNew1'].steps['Step-1'].setValues(matrixSolver=DIRECT, 
        matrixStorage=UNSYMMETRIC)
    mdb.models['TestNew1'].steps['Step-1'].control.setValues(allowPropagation=OFF, 
        resetDefaultValues=OFF, discontinuous=ON, timeIncrementation=(8.0, 
        10.0, 9.0, 16.0, 10.0, 4.0, 12.0, 20.0, 6.0, 3.0, 50.0))
    mdb.models['TestNew1'].fieldOutputRequests['F-Output-1'].setValues(variables=(
        'S', 'PE', 'PEEQ', 'PEMAG', 'LE', 'U', 'RF', 'CSTRESS', 'CDISP', 
        'DAMAGEC', 'DAMAGET', 'SDEG', 'MVF'))
    ##接触部分  
    if interact:
        session.viewports['Viewport: 1'].assemblyDisplay.setValues(interactions=ON, 
            constraints=ON, connectors=ON, engineeringFeatures=ON, 
            adaptiveMeshConstraints=OFF)
        mdb.models['TestNew1'].ContactProperty('IntProp-1')
        mdb.models['TestNew1'].interactionProperties['IntProp-1'].TangentialBehavior(
            formulation=FRICTIONLESS)
        mdb.models['TestNew1'].interactionProperties['IntProp-1'].NormalBehavior(
            pressureOverclosure=HARD, allowSeparation=ON, 
            constraintEnforcementMethod=DEFAULT)
        session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Initial')
        mdb.models['TestNew1'].ContactStd(name='Int-1', createStepName='Initial')
        mdb.models['TestNew1'].interactions['Int-1'].includedPairs.setValuesInStep(
            stepName='Initial', useAllstar=ON)
        mdb.models['TestNew1'].interactions['Int-1'].contactPropertyAssignments.appendInStep(
            stepName='Initial', assignments=((GLOBAL, SELF, 'IntProp-1'), ))
if __name__ == "__main__":
    Fibre_insert(modelName,partName,variable,uel_mode,concrete,diameter,thick,interact)