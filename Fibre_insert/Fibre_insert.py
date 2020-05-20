# -*- coding: utf-8 -*-
# coding=gbk
from odbAccess import *
from abaqus import*
from abaqusConstants import*
from material import createMaterialFromDataString
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
import section
import regionToolset
import displayGroupMdbToolset as dgm
import part
import assembly
import step
import interaction
import load
import mesh
import optimization
import job
import sketch
import time


def Fibre_insert(modelName,partName,variable,uel_mode,pattern,diameter,thick,interact,strength):
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
    print ('[info] 完成')
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
    material_insert(pattern,diameter,modelName,partName,variable,uel_mode,thick,interact,strength)
    # 切换到d盘
    os.chdir(r"d:\temp")
def material_insert(pattern,diameter,modelName,partName,variable,uel_mode,thick,interact,strength):
    try:
        if "c:/Users/Hasee/abaqus_plugins/POLARIS_CDP-c" not in os.sys.path:os.sys.path.append(
            "c:/Users/Hasee/abaqus_plugins/POLARIS_CDP-c")
        ####混凝土材料
        mat_dic = {'C15':1,'C20':2,'C25':3,'C30':4,'C35':5,'C40':6,'C45':7,'C50':8,'C55':9,'C60':10,'C65':11,'C70':12,'C75':13,'C80':14}
        # material_para = [[2.36E-09,22000,10,1.27],[2.37E-09,25500,13.4,1.54],[2.38E-09,28000,16.7,1.78],[2.39E-09,30000,20.1,2.01]\
        #     ,[2.39E-09,31500,23.4,2.2],[2.4E-09,32500,26.8,2.39],[2.41E-09,33500,29.6,2.51],[2.42E-09,34500,32.4,2.64]\
        #         ,[2.43E-09,35500,35.3,2.74],[2.44E-09,36000,38.5,2.85],[2.45E-09,36500,41.5,2.93],[2.46E-09,37000,44.5,2.99]\
        #             ,[2.47E-09,37500,47.4,3.05],[2.48E-09,38000,50.2,3.11]]
        # m=material_para[mat_dic[7]]
        # PolarisCDP_Functions.PolarisCDP_Functions().createMaterial(
        #     matName='concrete', dwz='mm/s/T - (N/MPa)', den=m[0],
        #     elas=m[1], pos=0.2, fc=m[2], ft=m[3], p1=38, p2=0.1, p3=1.16,
        #     p4=0.66667, p5=1E-05, wt=0, wc=1, fcuStrainType=1, fcStrain=1E-05,
        #     ftStrain=1E-05, fcInitial=0.4, ftInitial=0.8, dfc=0.05, damageType=1,
        #     ratioc=0.7, ratiot=0.1, maxDamage=0.9)
        # C50
        if strength =="C15":
            createMaterialFromDataString('TestNew1', 'C15', '2018',
                                     """{'name': 'C15', 'elastic': {'temperatureDependency': OFF, 'moduli': LONG_TERM, 'noCompression': OFF, 'noTension': OFF, 'dependencies': 0, 'table': ((22000.0, 0.2),), 'type': ISOTROPIC}, 'density': {'temperatureDependency': OFF, 'table': ((2.36e-09,),), 'dependencies': 0, 'fieldName': '', 'distributionType': UNIFORM}, 'concreteDamagedPlasticity': {'temperatureDependency': OFF, 'concreteCompressionDamage': {'temperatureDependency': OFF, 'table': ((0.0, 0.0), (0.01228836, 1.549e-05), (0.03800663, 3.329e-05), (0.06857575, 5.36e-05), (0.10040229, 7.664e-05), (0.1327548, 0.00010334), (0.16484284, 0.00013404), (0.19762625, 0.00017069), (0.23124196, 0.00021483), (0.26635719, 0.00026916), (0.30539727, 0.00034082), (0.35339714, 0.00044736), (0.44636307, 0.00071878), (0.75046351, 0.00277282), (0.82906916, 0.00434796), (0.87373958, 0.00601764)), 'dependencies': 0, 'tensionRecovery': 0.0}, 'concreteCompressionHardening': {'temperatureDependency': OFF, 'table': ((4.00252, 0.0), (4.51002, 1.549e-05), (5.02161, 3.329e-05), (5.53258, 5.36e-05), (6.03811, 7.664e-05), (6.54552, 0.00010334), (7.04686, 0.00013404), (7.55406, 0.00017069), (8.06074, 0.00021483), (8.56224, 0.00026916), (9.06554, 0.00034082), (9.56778, 0.00044736), (10.0, 0.00071878), (9.49994, 0.00277282), (8.99966, 0.00434796), (8.49937, 0.00601764)), 'rate': OFF, 'dependencies': 0}, 'concreteTensionStiffening': {'temperatureDependency': OFF, 'table': ((1.0164, 0.0), (1.08009, 8.8e-07), (1.14432, 2.17e-06), (1.20788, 4.31e-06), (1.27, 1.184e-05), (1.20642, 3.773e-05), (1.14291, 5.667e-05), (1.07935, 7.605e-05), (1.01567, 9.706e-05), (0.95202, 0.00012052), (0.88846, 0.00014729), (0.82487, 0.00017858), (0.76136, 0.00021586), (0.6978, 0.00026134), (0.63425, 0.00031815), (0.57073, 0.00039099), (0.50723, 0.00048743)), 'rate': OFF, 'dependencies': 0, 'type': STRAIN}, 'dependencies': 0, 'concreteTensionDamage': {'temperatureDependency': OFF, 'table': ((0.0, 0.0), (0.00132416, 8.8e-07), (0.00550414, 2.17e-06), (0.01391001, 4.31e-06), (0.04463731, 1.184e-05), (0.15827404, 3.773e-05), (0.24336913, 5.667e-05), (0.32327022, 7.605e-05), (0.39954964, 9.706e-05), (0.47228575, 0.00012052), (0.54133582, 0.00014729), (0.60660696, 0.00017858), (0.66769265, 0.00021586), (0.72438027, 0.00026134), (0.77626375, 0.00031815), (0.82300615, 0.00039099), (0.86434424, 0.00048743)), 'dependencies': 0, 'compressionRecovery': 1.0, 'type': STRAIN}, 'table': ((38.0, 0.1, 1.16, 0.66667, 1e-05),)}, 'materialIdentifier': '', 'description': 'ConcreteData\nCalculate By: PolarisCDP plugins\nSource: http://xcbjx.taobao.com'}""")
        if strength == "C20":
            createMaterialFromDataString('TestNew1', 'C20', '2018',
                                     """{'name': 'C20', 'elastic': {'temperatureDependency': OFF, 'moduli': LONG_TERM, 'noCompression': OFF, 'noTension': OFF, 'dependencies': 0, 'table': ((25500.0, 0.2),), 'type': ISOTROPIC}, 'density': {'temperatureDependency': OFF, 'table': ((2.37e-09,),), 'dependencies': 0, 'fieldName': '', 'distributionType': UNIFORM}, 'concreteDamagedPlasticity': {'temperatureDependency': OFF, 'concreteCompressionDamage': {'temperatureDependency': OFF, 'table': ((0.0, 0.0), (0.0096635, 1.491e-05), (0.03060486, 3.222e-05), (0.05631818, 5.217e-05), (0.08382987, 7.502e-05), (0.11245884, 0.0001017), (0.14209795, 0.00013337), (0.17221435, 0.00017063), (0.2036304, 0.00021583), (0.23698272, 0.00027185), (0.27417511, 0.00034529), (0.32044748, 0.0004546), (0.41338021, 0.00073984), (0.56897594, 0.00145357), (0.633953, 0.0018881), (0.68324764, 0.00230663), (0.72424616, 0.00273982), (0.75961724, 0.00320221), (0.79089525, 0.0037085), (0.81892072, 0.00427329), (0.84426737, 0.00491523), (0.86726893, 0.00565688), (0.8881883, 0.00653014)), 'dependencies': 0, 'tensionRecovery': 0.0}, 'concreteCompressionHardening': {'temperatureDependency': OFF, 'table': ((5.37897, 0.0), (6.04991, 1.491e-05), (6.72739, 3.222e-05), (7.40524, 5.217e-05), (8.07717, 7.502e-05), (8.75302, 0.0001017), (9.43717, 0.00013337), (10.11451, 0.00017063), (10.79295, 0.00021583), (11.46644, 0.00027185), (12.13662, 0.00034529), (12.80754, 0.0004546), (13.4, 0.00073984), (12.72909, 0.00145357), (12.05737, 0.0018881), (11.38712, 0.00230663), (10.71579, 0.00273982), (10.04564, 0.00320221), (9.37519, 0.0037085), (8.70469, 0.00427329), (8.03349, 0.00491523), (7.36258, 0.00565688), (6.692, 0.00653014)), 'rate': OFF, 'dependencies': 0}, 'concreteTensionStiffening': {'temperatureDependency': OFF, 'table': ((1.23249, 0.0), (1.30972, 1.16e-06), (1.3876, 2.78e-06), (1.46467, 5.34e-06), (1.54, 1.387e-05), (1.46285, 3.66e-05), (1.38574, 5.275e-05), (1.3084, 6.891e-05), (1.23108, 8.598e-05), (1.15403, 0.00010451), (1.07672, 0.00012527), (0.99961, 0.00014889), (0.92243, 0.00017646), (0.84541, 0.00020927), (0.76841, 0.00024939), (0.69131, 0.00029993), (0.61427, 0.00036565), (0.53721, 0.00045468), (0.46019, 0.00058137)), 'rate': OFF, 'dependencies': 0, 'type': STRAIN}, 'dependencies': 0, 'concreteTensionDamage': {'temperatureDependency': OFF, 'table': ((0.0, 0.0), (0.00175547, 1.16e-06), (0.0071103, 2.78e-06), (0.01739988, 5.34e-06), (0.05245598, 1.387e-05), (0.14536228, 3.66e-05), (0.21419471, 5.275e-05), (0.28049011, 6.891e-05), (0.3455113, 8.598e-05), (0.40937741, 0.00010451), (0.47250223, 0.00012527), (0.53430497, 0.00014889), (0.59467966, 0.00017646), (0.65303334, 0.00020927), (0.70896687, 0.00024939), (0.76196277, 0.00029993), (0.81125746, 0.00036565), (0.8561728, 0.00045468), (0.89593744, 0.00058137)), 'dependencies': 0, 'compressionRecovery': 1.0, 'type': STRAIN}, 'table': ((38.0, 0.1, 1.16, 0.66667, 1e-05),)}, 'materialIdentifier': '', 'description': 'ConcreteData\nCalculate By: PolarisCDP plugins\nSource: http://xcbjx.taobao.com'}""")
        if strength == "C25":
            createMaterialFromDataString('TestNew1', 'C25', '2018',
                                     """{'name': 'C25', 'elastic': {'temperatureDependency': OFF, 'moduli': LONG_TERM, 'noCompression': OFF, 'noTension': OFF, 'dependencies': 0, 'table': ((28000.0, 0.2),), 'type': ISOTROPIC}, 'density': {'temperatureDependency': OFF, 'table': ((2.38e-09,),), 'dependencies': 0, 'fieldName': '', 'distributionType': UNIFORM}, 'concreteDamagedPlasticity': {'temperatureDependency': OFF, 'concreteCompressionDamage': {'temperatureDependency': OFF, 'table': ((0.0, 0.0), (0.00803333, 1.444e-05), (0.02577371, 3.144e-05), (0.0473663, 5.071e-05), (0.07161072, 7.362e-05), (0.09729239, 0.00010062), (0.12372024, 0.00013218), (0.15107111, 0.00016959), (0.18010247, 0.00021531), (0.21144151, 0.0002724), (0.2474297, 0.00034887), (0.2927975, 0.00046341), (0.38187635, 0.000751), (0.50487632, 0.00130141), (0.56038041, 0.00162167), (0.60525312, 0.00192373), (0.64464866, 0.00223006), (0.68031231, 0.0025503), (0.71348232, 0.00289587), (0.74459043, 0.00327508), (0.77398788, 0.00369917), (0.80187141, 0.00418214), (0.82838525, 0.00474366), (0.85360607, 0.00541181), (0.87755579, 0.0062287)), 'dependencies': 0, 'tensionRecovery': 0.0}, 'concreteCompressionHardening': {'temperatureDependency': OFF, 'table': ((6.69612, 0.0), (7.54887, 1.444e-05), (8.40833, 3.144e-05), (9.2437, 5.071e-05), (10.09492, 7.362e-05), (10.94942, 0.00010062), (11.79411, 0.00013218), (12.63206, 0.00016959), (13.47313, 0.00021531), (14.30987, 0.0002724), (15.15397, 0.00034887), (15.99294, 0.00046341), (16.7, 0.000751), (15.86189, 0.00130141), (15.02574, 0.00162167), (14.18844, 0.00192373), (13.34953, 0.00223006), (12.51407, 0.0025503), (11.67628, 0.00289587), (10.8392, 0.00327508), (10.00267, 0.00369917), (9.16713, 0.00418214), (8.33199, 0.00474366), (7.49663, 0.00541181), (6.66031, 0.0062287)), 'rate': OFF, 'dependencies': 0}, 'concreteTensionStiffening': {'temperatureDependency': OFF, 'table': ((1.42457, 0.0), (1.51383, 1.34e-06), (1.60385, 3.18e-06), (1.69293, 6.03e-06), (1.78, 1.535e-05), (1.69042, 3.621e-05), (1.60088, 5.085e-05), (1.51156, 6.523e-05), (1.42192, 8.023e-05), (1.33251, 9.629e-05), (1.24302, 0.00011395), (1.15369, 0.00013374), (1.06461, 0.00015635), (0.97552, 0.00018288), (0.88631, 0.00021482), (0.79725, 0.00025429), (0.70818, 0.00030486), (0.61909, 0.00037238), (0.53005, 0.00046724)), 'rate': OFF, 'dependencies': 0, 'type': STRAIN}, 'dependencies': 0, 'concreteTensionDamage': {'temperatureDependency': OFF, 'table': ((0.0, 0.0), (0.00197267, 1.34e-06), (0.00790989, 3.18e-06), (0.01911668, 6.03e-06), (0.0562263, 1.535e-05), (0.13515664, 3.621e-05), (0.19343418, 5.085e-05), (0.25018425, 6.523e-05), (0.30715831, 8.023e-05), (0.36439745, 9.629e-05), (0.42215441, 0.00011395), (0.48017048, 0.00013374), (0.53817226, 0.00015635), (0.59600607, 0.00018288), (0.65329454, 0.00021482), (0.70929474, 0.00025429), (0.76338443, 0.00030486), (0.81467424, 0.00037238), (0.86205795, 0.00046724)), 'dependencies': 0, 'compressionRecovery': 1.0, 'type': STRAIN}, 'table': ((38.0, 0.1, 1.16, 0.66667, 1e-05),)}, 'materialIdentifier': '', 'description': 'ConcreteData\nCalculate By: PolarisCDP plugins\nSource: http://xcbjx.taobao.com'}""")
        if strength == "C30":
            createMaterialFromDataString('TestNew1', 'C30', '2018',
                                     """{'name': 'C30', 'elastic': {'temperatureDependency': OFF, 'moduli': LONG_TERM, 'noCompression': OFF, 'noTension': OFF, 'dependencies': 0, 'table': ((30000.0, 0.2),), 'type': ISOTROPIC}, 'density': {'temperatureDependency': OFF, 'table': ((2.39e-09,),), 'dependencies': 0, 'fieldName': '', 'distributionType': UNIFORM}, 'concreteDamagedPlasticity': {'temperatureDependency': OFF, 'concreteCompressionDamage': {'temperatureDependency': OFF, 'table': ((0.0, 0.0), (0.00627417, 1.325e-05), (0.02055013, 2.91e-05), (0.0389833, 4.788e-05), (0.0596135, 6.987e-05), (0.08195888, 9.607e-05), (0.10542774, 0.000127), (0.13017518, 0.000164), (0.15690757, 0.00020961), (0.1862524, 0.00026707), (0.220072, 0.00034364), (0.2632259, 0.00045856), (0.35153069, 0.00075595), (0.45740261, 0.00123535), (0.50727869, 0.00151021), (0.54882161, 0.00176593), (0.58627284, 0.00202161), (0.62135305, 0.00228768), (0.65483257, 0.00257146), (0.68697998, 0.00287864), (0.71828042, 0.00321976), (0.74870128, 0.00360341), (0.77848261, 0.00404596), (0.80754733, 0.00456641), (0.8359694, 0.00519725), (0.86360184, 0.00598549), (0.89027323, 0.00701057)), 'dependencies': 0, 'tensionRecovery': 0.0}, 'concreteCompressionHardening': {'temperatureDependency': OFF, 'table': ((8.04512, 0.0), (9.06005, 1.325e-05), (10.08483, 2.91e-05), (11.1105, 4.788e-05), (12.12777, 6.987e-05), (13.15116, 9.607e-05), (14.16515, 0.000127), (15.17356, 0.000164), (16.18848, 0.00020961), (17.20119, 0.00026707), (18.21416, 0.00034364), (19.22403, 0.00045856), (20.1, 0.00075595), (19.09059, 0.00123535), (18.08269, 0.00151021), (17.07536, 0.00176593), (16.06895, 0.00202161), (15.0602, 0.00228768), (14.0496, 0.00257146), (13.04289, 0.00287864), (12.03348, 0.00321976), (11.02767, 0.00360341), (10.02044, 0.00404596), (9.01524, 0.00456641), (8.0084, 0.00519725), (7.0018, 0.00598549), (5.99572, 0.00701057)), 'rate': OFF, 'dependencies': 0}, 'concreteTensionStiffening': {'temperatureDependency': OFF, 'table': ((1.60864, 0.0), (1.70944, 1.47e-06), (1.81109, 3.49e-06), (1.91168, 6.58e-06), (2.01, 1.657e-05), (1.90887, 3.605e-05), (1.80769, 4.965e-05), (1.7068, 6.287e-05), (1.60596, 7.647e-05), (1.50483, 9.093e-05), (1.40367, 0.00010662), (1.30304, 0.0001239), (1.20227, 0.00014347), (1.10157, 0.00016606), (1.00089, 0.00019282), (0.9002, 0.00022546), (0.79955, 0.00026663), (0.69889, 0.00032077), (0.5983, 0.00039577), (0.49777, 0.00050696)), 'rate': OFF, 'dependencies': 0, 'type': STRAIN}, 'dependencies': 0, 'concreteTensionDamage': {'temperatureDependency': OFF, 'table': ((0.0, 0.0), (0.00208329, 1.47e-06), (0.00831489, 3.49e-06), (0.01998141, 6.58e-06), (0.05810776, 1.657e-05), (0.12615377, 3.605e-05), (0.1763598, 4.965e-05), (0.22584392, 6.287e-05), (0.27606669, 7.647e-05), (0.32761986, 9.093e-05), (0.38052305, 0.00010662), (0.43448412, 0.0001239), (0.48976193, 0.00014347), (0.54605195, 0.00016606), (0.6030794, 0.00019282), (0.66042317, 0.00022546), (0.71743132, 0.00026663), (0.77327091, 0.00032077), (0.82675822, 0.00039577), (0.87640222, 0.00050696)), 'dependencies': 0, 'compressionRecovery': 1.0, 'type': STRAIN}, 'table': ((38.0, 0.1, 1.16, 0.66667, 1e-05),)}, 'materialIdentifier': '', 'description': 'ConcreteData\nCalculate By: PolarisCDP plugins\nSource: http://xcbjx.taobao.com'}""")
        if strength == "C35":
            createMaterialFromDataString('TestNew1', 'C35', '2018',
                                     """{'name': 'C35', 'elastic': {'temperatureDependency': OFF, 'moduli': LONG_TERM, 'noCompression': OFF, 'noTension': OFF, 'dependencies': 0, 'table': ((31500.0, 0.2),), 'type': ISOTROPIC}, 'density': {'temperatureDependency': OFF, 'table': ((2.39e-09,),), 'dependencies': 0, 'fieldName': '', 'distributionType': UNIFORM}, 'concreteDamagedPlasticity': {'temperatureDependency': OFF, 'concreteCompressionDamage': {'temperatureDependency': OFF, 'table': ((0.0, 0.0), (0.00514658, 1.237e-05), (0.01668035, 2.704e-05), (0.03191952, 4.467e-05), (0.04939079, 6.56e-05), (0.06874591, 9.083e-05), (0.08949927, 0.00012092), (0.11180255, 0.00015726), (0.13632619, 0.00020247), (0.16370611, 0.00025992), (0.19536651, 0.00033611), (0.23664236, 0.00045189), (0.32299322, 0.00075476), (0.41838127, 0.00119657), (0.46451377, 0.0014483), (0.50384046, 0.00168172), (0.53995665, 0.00191359), (0.57439066, 0.00215319), (0.60756279, 0.00240482), (0.64012871, 0.00267641), (0.67239606, 0.00297567), (0.70436052, 0.00331009), (0.73616003, 0.00369197), (0.76783496, 0.00413817), (0.79943092, 0.00467482), (0.83079684, 0.00534015), (0.86174494, 0.00619846), (0.89203188, 0.00736778)), 'dependencies': 0, 'tensionRecovery': 0.0}, 'concreteCompressionHardening': {'temperatureDependency': OFF, 'table': ((9.38838, 0.0), (10.59124, 1.237e-05), (11.77009, 2.704e-05), (12.95205, 4.467e-05), (14.12654, 6.56e-05), (15.31043, 9.083e-05), (16.4859, 0.00012092), (17.6575, 0.00015726), (18.83944, 0.00020247), (20.02172, 0.00025992), (21.19311, 0.00033611), (22.37194, 0.00045189), (23.4, 0.00075476), (22.22335, 0.00119657), (21.0502, 0.0014483), (19.87437, 0.00168172), (18.6996, 0.00191359), (17.5221, 0.00215319), (16.35199, 0.00240482), (15.18074, 0.00267641), (14.00622, 0.00297567), (12.83429, 0.00331009), (11.66325, 0.00369197), (10.49288, 0.00413817), (9.3207, 0.00467482), (8.14915, 0.00534015), (6.97898, 0.00619846), (5.80857, 0.00736778)), 'rate': OFF, 'dependencies': 0}, 'concreteTensionStiffening': {'temperatureDependency': OFF, 'table': ((1.7607, 0.0), (1.87103, 1.57e-06), (1.98229, 3.71e-06), (2.09239, 6.98e-06), (2.2, 1.75e-05), (2.08977, 3.602e-05), (1.97894, 4.899e-05), (1.86795, 6.157e-05), (1.75787, 7.432e-05), (1.64743, 8.777e-05), (1.53719, 0.00010222), (1.42699, 0.00011805), (1.31675, 0.00013578), (1.20623, 0.00015611), (1.09579, 0.00017991), (0.98544, 0.00020859), (0.87517, 0.00024432), (0.76505, 0.0002907), (0.65496, 0.0003542), (0.54495, 0.00044724)), 'rate': OFF, 'dependencies': 0, 'type': STRAIN}, 'dependencies': 0, 'concreteTensionDamage': {'temperatureDependency': OFF, 'table': ((0.0, 0.0), (0.0021459, 1.57e-06), (0.00854346, 3.71e-06), (0.02046804, 6.98e-06), (0.05916158, 1.75e-05), (0.11980566, 3.602e-05), (0.16467786, 4.899e-05), (0.20945151, 6.157e-05), (0.25498436, 7.432e-05), (0.30224572, 8.777e-05), (0.35120142, 0.00010222), (0.40199749, 0.00011805), (0.45468623, 0.00013578), (0.50930614, 0.00015611), (0.56552181, 0.00017991), (0.62302329, 0.00020859), (0.68133879, 0.00024432), (0.73969442, 0.0002907), (0.79709361, 0.0003542), (0.85197499, 0.00044724)), 'dependencies': 0, 'compressionRecovery': 1.0, 'type': STRAIN}, 'table': ((38.0, 0.1, 1.16, 0.66667, 1e-05),)}, 'materialIdentifier': '', 'description': 'ConcreteData\nCalculate By: PolarisCDP plugins\nSource: http://xcbjx.taobao.com'}""")
        if strength == "C40":
            createMaterialFromDataString('TestNew1', 'C40', '2018',
                                     """{'name': 'C40', 'elastic': {'temperatureDependency': OFF, 'moduli': LONG_TERM, 'noCompression': OFF, 'noTension': OFF, 'dependencies': 0, 'table': ((32500.0, 0.2),), 'type': ISOTROPIC}, 'density': {'temperatureDependency': OFF, 'table': ((2.4e-09,),), 'dependencies': 0, 'fieldName': '', 'distributionType': UNIFORM}, 'concreteDamagedPlasticity': {'temperatureDependency': OFF, 'concreteCompressionDamage': {'temperatureDependency': OFF, 'table': ((0.0, 0.0), (0.0037787, 1.054e-05), (0.01284229, 2.384e-05), (0.02488002, 3.978e-05), (0.03948568, 5.962e-05), (0.05568758, 8.334e-05), (0.07349814, 0.00011204), (0.09308559, 0.00014715), (0.11509473, 0.00019133), (0.14018049, 0.00024813), (0.16977793, 0.00032429), (0.20879082, 0.00044024), (0.29220563, 0.00074601), (0.37953723, 0.00116264), (0.42298504, 0.00140127), (0.4604583, 0.00162073), (0.49555745, 0.00183877), (0.52927087, 0.00206141), (0.56238042, 0.00229516), (0.59540588, 0.00254656), (0.62836982, 0.00282007), (0.66149695, 0.00312374), (0.6950021, 0.00346881), (0.72891094, 0.00386957), (0.76316994, 0.00434659), (0.79784063, 0.00493501), (0.83268226, 0.00568878), (0.86745625, 0.00670813)), 'dependencies': 0, 'tensionRecovery': 0.0}, 'concreteCompressionHardening': {'temperatureDependency': OFF, 'table': ((10.72804, 0.0), (12.09129, 1.054e-05), (13.46823, 2.384e-05), (14.81096, 3.978e-05), (16.18198, 5.962e-05), (17.5302, 8.334e-05), (18.87173, 0.00011204), (20.21185, 0.00014715), (21.56702, 0.00019133), (22.92592, 0.00024813), (24.27545, 0.00032429), (25.62438, 0.00044024), (26.8, 0.00074601), (25.45798, 0.00116264), (24.11201, 0.00140127), (22.76872, 0.00162073), (21.41979, 0.00183877), (20.07645, 0.00206141), (18.73383, 0.00229516), (17.38648, 0.00254656), (16.04371, 0.00282007), (14.70322, 0.00312374), (13.3608, 0.00346881), (12.018, 0.00386957), (10.67738, 0.00434659), (9.33458, 0.00493501), (7.99364, 0.00568878), (6.65337, 0.00670813)), 'rate': OFF, 'dependencies': 0}, 'concreteTensionStiffening': {'temperatureDependency': OFF, 'table': ((1.91276, 0.0), (2.03262, 1.62e-06), (2.15348, 3.83e-06), (2.2731, 7.23e-06), (2.39, 1.82e-05), (2.27015, 3.603e-05), (2.15053, 4.846e-05), (2.03049, 6.047e-05), (1.91023, 7.271e-05), (1.79039, 8.545e-05), (1.67084, 9.901e-05), (1.55068, 0.00011384), (1.43106, 0.00013021), (1.31128, 0.00014878), (1.19115, 0.00017037), (1.07153, 0.00019601), (0.95198, 0.00022757), (0.83243, 0.00026809), (0.71289, 0.00032285), (0.59331, 0.00040218), (0.47377, 0.00052843)), 'rate': OFF, 'dependencies': 0, 'type': STRAIN}, 'dependencies': 0, 'concreteTensionDamage': {'temperatureDependency': OFF, 'table': ((0.0, 0.0), (0.00208663, 1.62e-06), (0.00832711, 3.83e-06), (0.02000744, 7.23e-06), (0.05816424, 1.82e-05), (0.11210428, 3.603e-05), (0.15186436, 4.846e-05), (0.19197964, 6.047e-05), (0.23360218, 7.271e-05), (0.27696608, 8.545e-05), (0.32234506, 9.901e-05), (0.3702441, 0.00011384), (0.42030118, 0.00013021), (0.47282684, 0.00014878), (0.52788107, 0.00017037), (0.58492307, 0.00019601), (0.64383985, 0.00022757), (0.704128, 0.00026809), (0.76487973, 0.00032285), (0.82467591, 0.00040218), (0.88124531, 0.00052843)), 'dependencies': 0, 'compressionRecovery': 1.0, 'type': STRAIN}, 'table': ((38.0, 0.1, 1.16, 0.66667, 1e-05),)}, 'materialIdentifier': '', 'description': 'ConcreteData\nCalculate By: PolarisCDP plugins\nSource: http://xcbjx.taobao.com'}""")
        if strength == "C45":
            createMaterialFromDataString('TestNew1', 'C45', '2018',
                                     """{'name': 'C45', 'elastic': {'temperatureDependency': OFF, 'moduli': LONG_TERM, 'noCompression': OFF, 'noTension': OFF, 'dependencies': 0, 'table': ((33500.0, 0.2),), 'type': ISOTROPIC}, 'density': {'temperatureDependency': OFF, 'table': ((2.41e-09,),), 'dependencies': 0, 'fieldName': '', 'distributionType': UNIFORM}, 'concreteDamagedPlasticity': {'temperatureDependency': OFF, 'concreteCompressionDamage': {'temperatureDependency': OFF, 'table': ((0.0, 0.0), (0.00306707, 9.44e-06), (0.01059076, 2.164e-05), (0.02113823, 3.697e-05), (0.03385673, 5.582e-05), (0.04822204, 7.862e-05), (0.06464958, 0.00010714), (0.08296001, 0.00014234), (0.10339396, 0.00018612), (0.12699699, 0.0002428), (0.15521313, 0.00031939), (0.19292485, 0.00043693), (0.272851, 0.00074113), (0.35487678, 0.00114356), (0.39625555, 0.00137435), (0.43249342, 0.0015873), (0.46652015, 0.00179686), (0.4996909, 0.00201141), (0.53252875, 0.00223574), (0.56538556, 0.00247469), (0.59865383, 0.00273502), (0.63242261, 0.00302312), (0.66687085, 0.00334888), (0.7018967, 0.0037235), (0.73775627, 0.00416851), (0.77435655, 0.00471325), (0.8116398, 0.00540848), (0.84941541, 0.00634584), (0.88714801, 0.00770519)), 'dependencies': 0, 'tensionRecovery': 0.0}, 'concreteCompressionHardening': {'temperatureDependency': OFF, 'table': ((11.84917, 0.0), (13.34117, 9.44e-06), (14.85054, 2.164e-05), (16.36464, 3.697e-05), (17.87019, 5.582e-05), (19.35324, 7.862e-05), (20.86377, 0.00010714), (22.36964, 0.00014234), (23.86211, 0.00018612), (25.36073, 0.0002428), (26.85032, 0.00031939), (28.33772, 0.00043693), (29.6, 0.00074113), (28.11951, 0.00114356), (26.635, 0.00137435), (25.14556, 0.0015873), (23.65982, 0.00179686), (22.17131, 0.00201141), (20.6844, 0.00223574), (19.20033, 0.00247469), (17.71292, 0.00273502), (16.22644, 0.00302312), (14.73893, 0.00334888), (13.25859, 0.0037235), (11.77644, 0.00416851), (10.29595, 0.00471325), (8.81563, 0.00540848), (7.334, 0.00634584), (5.85395, 0.00770519)), 'rate': OFF, 'dependencies': 0}, 'concreteTensionStiffening': {'temperatureDependency': OFF, 'table': ((2.0088, 0.0), (2.13467, 1.69e-06), (2.26161, 3.99e-06), (2.38723, 7.51e-06), (2.51, 1.88e-05), (2.38389, 3.624e-05), (2.25734, 4.846e-05), (2.13027, 6.026e-05), (2.00405, 7.215e-05), (1.87734, 8.459e-05), (1.75126, 9.775e-05), (1.62559, 0.00011198), (1.49977, 0.0001277), (1.37369, 0.00014546), (1.24806, 0.00016588), (1.12211, 0.00019015), (0.99632, 0.00021987), (0.87054, 0.00025781), (0.74493, 0.00030878), (0.6194, 0.00038219), (0.49385, 0.00049865)), 'rate': OFF, 'dependencies': 0, 'type': STRAIN}, 'dependencies': 0, 'concreteTensionDamage': {'temperatureDependency': OFF, 'table': ((0.0, 0.0), (0.00215391, 1.69e-06), (0.00857268, 3.99e-06), (0.02053017, 7.51e-06), (0.05929587, 1.88e-05), (0.11041155, 3.624e-05), (0.14818178, 4.846e-05), (0.18642115, 6.026e-05), (0.2259197, 7.215e-05), (0.26755912, 8.459e-05), (0.3112394, 9.775e-05), (0.35720102, 0.00011198), (0.4057728, 0.0001277), (0.45710271, 0.00014546), (0.51092629, 0.00016588), (0.56751335, 0.00019015), (0.62645165, 0.00021987), (0.68737751, 0.00025781), (0.74943022, 0.00030878), (0.81131105, 0.00038219), (0.8708583, 0.00049865)), 'dependencies': 0, 'compressionRecovery': 1.0, 'type': STRAIN}, 'table': ((38.0, 0.1, 1.16, 0.66667, 1e-05),)}, 'materialIdentifier': '', 'description': 'ConcreteData\nCalculate By: PolarisCDP plugins\nSource: http://xcbjx.taobao.com'}""")
        if strength == "C50":
            createMaterialFromDataString('TestNew1', 'C50', '2018',
                                     """{'name': 'C50', 'elastic': {'temperatureDependency': OFF, 'moduli': LONG_TERM, 'noCompression': OFF, 'noTension': OFF, 'dependencies': 0, 'table': ((34500.0, 0.2),), 'type': ISOTROPIC}, 'density': {'temperatureDependency': OFF, 'table': ((2.42e-09,),), 'dependencies': 0, 'fieldName': '', 'distributionType': UNIFORM}, 'concreteDamagedPlasticity': {'temperatureDependency': OFF, 'concreteCompressionDamage': {'temperatureDependency': OFF, 'table': ((0.0, 0.0), (0.00267297, 8.78e-06), (0.00908247, 2.007e-05), (0.01820804, 3.449e-05), (0.02940511, 5.246e-05), (0.04258742, 7.5e-05), (0.05752503, 0.00010281), (0.0744023, 0.0001374), (0.0934767, 0.00018073), (0.11577678, 0.00023723), (0.14275472, 0.0003141), (0.17927119, 0.00043305), (0.2561493, 0.00073633), (0.3339284, 0.00112939), (0.37346132, 0.00135442), (0.40823598, 0.00156091), (0.44154652, 0.00176617), (0.47407629, 0.00197462), (0.50642277, 0.00219129), (0.53902382, 0.00242131), (0.57237641, 0.00267173), (0.60641507, 0.00294722), (0.64127803, 0.00325614), (0.67725801, 0.00361218), (0.71430608, 0.00403193), (0.75253291, 0.00454403), (0.79193369, 0.00519555), (0.83225726, 0.00606866), (0.87308465, 0.00732958)), 'dependencies': 0, 'tensionRecovery': 0.0}, 'concreteCompressionHardening': {'temperatureDependency': OFF, 'table': ((12.968, 0.0), (14.6347, 8.78e-06), (16.27264, 2.007e-05), (17.91834, 3.449e-05), (19.55745, 5.246e-05), (21.21291, 7.5e-05), (22.86025, 0.00010281), (24.50525, 0.0001374), (26.13832, 0.00018073), (27.78068, 0.00023723), (29.41502, 0.0003141), (31.04628, 0.00043305), (32.4, 0.00073633), (30.77242, 0.00112939), (29.14917, 0.00135442), (27.52843, 0.00156091), (25.89193, 0.00176617), (24.26136, 0.00197462), (22.63698, 0.00219129), (21.01538, 0.00242131), (19.38494, 0.00267173), (17.75874, 0.00294722), (16.13735, 0.00325614), (14.51278, 0.00361218), (12.89117, 0.00403193), (11.26919, 0.00454403), (9.64547, 0.00519555), (8.02324, 0.00606866), (6.40267, 0.00732958)), 'rate': OFF, 'dependencies': 0}, 'concreteTensionStiffening': {'temperatureDependency': OFF, 'table': ((2.11284, 0.0), (2.24524, 1.76e-06), (2.37874, 4.15e-06), (2.51087, 7.79e-06), (2.64, 1.941e-05), (2.50756, 3.643e-05), (2.37388, 4.843e-05), (2.2415, 5.984e-05), (2.10932, 7.136e-05), (1.97715, 8.331e-05), (1.8441, 9.606e-05), (1.71132, 0.00010979), (1.57902, 0.00012483), (1.44626, 0.00014174), (1.31411, 0.00016105), (1.18145, 0.00018389), (1.04896, 0.00021167), (0.91678, 0.00024679), (0.78461, 0.00029366), (0.6525, 0.00036062), (0.52045, 0.0004659)), 'rate': OFF, 'dependencies': 0, 'type': STRAIN}, 'dependencies': 0, 'concreteTensionDamage': {'temperatureDependency': OFF, 'table': ((0.0, 0.0), (0.00220831, 1.76e-06), (0.00877089, 4.15e-06), (0.02095125, 7.79e-06), (0.06020447, 1.941e-05), (0.10834336, 3.643e-05), (0.14400881, 4.843e-05), (0.17971013, 5.984e-05), (0.21690341, 7.136e-05), (0.25611298, 8.331e-05), (0.29791203, 9.606e-05), (0.34218215, 0.00010979), (0.38901416, 0.00012483), (0.43888654, 0.00014174), (0.49150209, 0.00016105), (0.54732741, 0.00018389), (0.60601218, 0.00021167), (0.66718876, 0.00024679), (0.73037157, 0.00029366), (0.79435464, 0.00036062), (0.85704683, 0.0004659)), 'dependencies': 0, 'compressionRecovery': 1.0, 'type': STRAIN}, 'table': ((38.0, 0.1, 1.16, 0.66667, 1e-05),)}, 'materialIdentifier': '', 'description': 'ConcreteData\nCalculate By: PolarisCDP plugins\nSource: http://xcbjx.taobao.com'}""")
        if strength == "C55":
            createMaterialFromDataString('TestNew1', 'C55', '2018',
                                     """{'name': 'C55', 'elastic': {'temperatureDependency': OFF, 'moduli': LONG_TERM, 'noCompression': OFF, 'noTension': OFF, 'dependencies': 0, 'table': ((35500.0, 0.2),), 'type': ISOTROPIC}, 'density': {'temperatureDependency': OFF, 'table': ((2.43e-09,),), 'dependencies': 0, 'fieldName': '', 'distributionType': UNIFORM}, 'concreteDamagedPlasticity': {'temperatureDependency': OFF, 'concreteCompressionDamage': {'temperatureDependency': OFF, 'table': ((0.0, 0.0), (0.0022078, 7.9e-06), (0.00761264, 1.832e-05), (0.01548288, 3.186e-05), (0.02533338, 4.896e-05), (0.03713519, 7.063e-05), (0.05071779, 9.763e-05), (0.06627935, 0.00013149), (0.08409196, 0.00017423), (0.10482052, 0.00022941), (0.13025684, 0.00030511), (0.16487348, 0.00042219), (0.240652, 0.00073072), (0.31428121, 0.00111452), (0.3524248, 0.0013368), (0.38611204, 0.0015399), (0.41830252, 0.00173958), (0.45008204, 0.00194273), (0.48208031, 0.00215462), (0.51445742, 0.00237836), (0.54753739, 0.00261922), (0.58167091, 0.00288429), (0.61709383, 0.00318224), (0.65380107, 0.00352318), (0.69180768, 0.00392247), (0.73140393, 0.00440791), (0.77259726, 0.00502255), (0.81519336, 0.00584203), (0.85885104, 0.00701962)), 'dependencies': 0, 'tensionRecovery': 0.0}, 'concreteCompressionHardening': {'temperatureDependency': OFF, 'table': ((14.17206, 0.0), (15.96989, 7.9e-06), (17.7396, 1.832e-05), (19.52066, 3.186e-05), (21.29764, 4.896e-05), (23.09554, 7.063e-05), (24.88791, 9.763e-05), (26.6811, 0.00013149), (28.46468, 0.00017423), (30.23488, 0.00022941), (32.00957, 0.00030511), (33.78272, 0.00042219), (35.3, 0.00073072), (33.53399, 0.00111452), (31.75598, 0.0013368), (29.98618, 0.0015399), (28.21593, 0.00173958), (26.44435, 0.00194273), (24.6683, 0.00215462), (22.89932, 0.00237836), (21.13404, 0.00261922), (19.36514, 0.00288429), (17.59022, 0.00318224), (15.81754, 0.00352318), (14.05202, 0.00392247), (12.284, 0.00440791), (10.51434, 0.00502255), (8.74697, 0.00584203), (6.98166, 0.00701962)), 'rate': OFF, 'dependencies': 0}, 'concreteTensionStiffening': {'temperatureDependency': OFF, 'table': ((2.19287, 0.0), (2.33028, 1.84e-06), (2.46885, 4.32e-06), (2.60598, 8.08e-06), (2.74, 1.999e-05), (2.6017, 3.676e-05), (2.46351, 4.85e-05), (2.32482, 5.98e-05), (2.18599, 7.121e-05), (2.04859, 8.293e-05), (1.91113, 9.531e-05), (1.77277, 0.00010873), (1.63516, 0.00012336), (1.49799, 0.00013966), (1.36061, 0.00015832), (1.2232, 0.00018022), (1.08613, 0.00020671), (0.94901, 0.00024015), (0.81193, 0.00028456), (0.67479, 0.0003478), (0.53769, 0.00044688)), 'rate': OFF, 'dependencies': 0, 'type': STRAIN}, 'dependencies': 0, 'concreteTensionDamage': {'temperatureDependency': OFF, 'table': ((0.0, 0.0), (0.00231122, 1.84e-06), (0.0091449, 4.32e-06), (0.02174384, 8.08e-06), (0.06190769, 1.999e-05), (0.10862616, 3.676e-05), (0.14276057, 4.85e-05), (0.17741817, 5.98e-05), (0.21369254, 7.121e-05), (0.25164046, 8.293e-05), (0.29194815, 9.531e-05), (0.33513144, 0.00010873), (0.38089118, 0.00012336), (0.42947599, 0.00013966), (0.48125991, 0.00015832), (0.5362758, 0.00018022), (0.59435652, 0.00020671), (0.6554723, 0.00024015), (0.71908443, 0.00028456), (0.78418276, 0.0003478), (0.84873666, 0.00044688)), 'dependencies': 0, 'compressionRecovery': 1.0, 'type': STRAIN}, 'table': ((38.0, 0.1, 1.16, 0.66667, 1e-05),)}, 'materialIdentifier': '', 'description': 'ConcreteData\nCalculate By: PolarisCDP plugins\nSource: http://xcbjx.taobao.com'}""")
        if strength == "C60":
            createMaterialFromDataString('TestNew1', 'C60', '2018',
                                     """{'name': 'C60', 'elastic': {'temperatureDependency': OFF, 'moduli': LONG_TERM, 'noCompression': OFF, 'noTension': OFF, 'dependencies': 0, 'table': ((36000.0, 0.2),), 'type': ISOTROPIC}, 'density': {'temperatureDependency': OFF, 'table': ((2.44e-09,),), 'dependencies': 0, 'fieldName': '', 'distributionType': UNIFORM}, 'concreteDamagedPlasticity': {'temperatureDependency': OFF, 'concreteCompressionDamage': {'temperatureDependency': OFF, 'table': ((0.0, 0.0), (0.00153583, 6.1e-06), (0.0056039, 1.499e-05), (0.01163962, 2.676e-05), (0.01949033, 4.208e-05), (0.0292216, 6.197e-05), (0.04075972, 8.722e-05), (0.05432974, 0.00011939), (0.07023007, 0.00016058), (0.08913111, 0.00021444), (0.11246286, 0.00028817), (0.14497791, 0.0004039), (0.21821366, 0.00071441), (0.28827096, 0.00109338), (0.32495187, 0.00131343), (0.35786916, 0.00151592), (0.3895946, 0.00171492), (0.42086482, 0.00191524), (0.45274131, 0.00212483), (0.48507067, 0.00234456), (0.51858708, 0.00258226), (0.55311368, 0.00284082), (0.58908324, 0.00312943), (0.62667565, 0.00345869), (0.66608641, 0.00384453), (0.70747846, 0.0043117), (0.75079543, 0.0048989), (0.79614937, 0.00568053), (0.84321636, 0.00680142), (0.89126848, 0.00860623)), 'dependencies': 0, 'tensionRecovery': 0.0}, 'concreteCompressionHardening': {'temperatureDependency': OFF, 'table': ((15.4221, 0.0), (17.36562, 6.1e-06), (19.33589, 1.499e-05), (21.26611, 2.676e-05), (23.19562, 4.208e-05), (25.15173, 6.197e-05), (27.10582, 8.722e-05), (29.06489, 0.00011939), (31.01756, 0.00016058), (32.95956, 0.00021444), (34.88604, 0.00028817), (36.82719, 0.0004039), (38.5, 0.00071441), (36.56338, 0.00109338), (34.62186, 0.00131343), (32.67643, 0.00151592), (30.72921, 0.00171492), (28.79803, 0.00191524), (26.85167, 0.00212483), (24.92175, 0.00234456), (22.98093, 0.00258226), (21.05284, 0.00284082), (19.12423, 0.00312943), (17.19569, 0.00345869), (15.26619, 0.00384453), (13.33511, 0.0043117), (11.40913, 0.0048989), (9.48205, 0.00568053), (7.55669, 0.00680142), (5.63133, 0.00860623)), 'rate': OFF, 'dependencies': 0}, 'concreteTensionStiffening': {'temperatureDependency': OFF, 'table': ((2.28091, 0.0), (2.42383, 1.87e-06), (2.56796, 4.38e-06), (2.7106, 8.2e-06), (2.85, 2.035e-05), (2.7071, 3.679e-05), (2.56428, 4.831e-05), (2.42093, 5.939e-05), (2.27677, 7.06e-05), (2.13327, 8.214e-05), (1.99061, 9.423e-05), (1.84728, 0.00010725), (1.70457, 0.0001214), (1.56171, 0.00013715), (1.41872, 0.00015508), (1.27594, 0.00017598), (1.13342, 0.00020111), (0.99066, 0.00023266), (0.84787, 0.00027427), (0.70529, 0.00033293), (0.56273, 0.00042396), (0.42016, 0.00058721)), 'rate': OFF, 'dependencies': 0, 'type': STRAIN}, 'dependencies': 0, 'concreteTensionDamage': {'temperatureDependency': OFF, 'table': ((0.0, 0.0), (0.00227395, 1.87e-06), (0.0090096, 4.38e-06), (0.02145742, 8.2e-06), (0.06129324, 2.035e-05), (0.10522931, 3.679e-05), (0.13732996, 4.831e-05), (0.1700193, 5.939e-05), (0.20450674, 7.06e-05), (0.24094056, 8.214e-05), (0.27955962, 9.423e-05), (0.32103308, 0.00010725), (0.36522691, 0.0001214), (0.41259336, 0.00013715), (0.46333843, 0.00015508), (0.5175103, 0.00017598), (0.57515091, 0.00020111), (0.6364037, 0.00023266), (0.70083986, 0.00027427), (0.76748338, 0.00033293), (0.83460577, 0.00042396), (0.89875986, 0.00058721)), 'dependencies': 0, 'compressionRecovery': 1.0, 'type': STRAIN}, 'table': ((38.0, 0.1, 1.16, 0.66667, 1e-05),)}, 'materialIdentifier': '', 'description': 'ConcreteData\nCalculate By: PolarisCDP plugins\nSource: http://xcbjx.taobao.com'}""")
        if strength == "C65":
            createMaterialFromDataString('TestNew1', 'C65', '2018',
                                     """{'name': 'C65', 'elastic': {'temperatureDependency': OFF, 'moduli': LONG_TERM, 'noCompression': OFF, 'noTension': OFF, 'dependencies': 0, 'table': ((36500.0, 0.2),), 'type': ISOTROPIC}, 'density': {'temperatureDependency': OFF, 'table': ((2.45e-09,),), 'dependencies': 0, 'fieldName': '', 'distributionType': UNIFORM}, 'concreteDamagedPlasticity': {'temperatureDependency': OFF, 'concreteCompressionDamage': {'temperatureDependency': OFF, 'table': ((0.0, 0.0), (0.00105707, 4.61e-06), (0.0040075, 1.196e-05), (0.00878127, 2.25e-05), (0.01528734, 3.674e-05), (0.0234341, 5.521e-05), (0.0333741, 7.908e-05), (0.04535697, 0.00010995), (0.05970559, 0.00014996), (0.07709814, 0.00020288), (0.09896214, 0.00027613), (0.12999927, 0.00039246), (0.19940246, 0.00069898), (0.26605739, 0.00107224), (0.30137039, 0.00129023), (0.33316729, 0.00149005), (0.36403497, 0.0016864), (0.39473038, 0.00188428), (0.42600032, 0.00208953), (0.45810938, 0.00230557), (0.49152834, 0.00253814), (0.52616434, 0.00279027), (0.56258703, 0.00307157), (0.60085186, 0.0033908), (0.64115917, 0.0037624), (0.68380584, 0.00421), (0.72881368, 0.00476957), (0.77627901, 0.00550807), (0.82609579, 0.00655934), (0.87764936, 0.0082362)), 'dependencies': 0, 'tensionRecovery': 0.0}, 'concreteCompressionHardening': {'temperatureDependency': OFF, 'table': ((16.66003, 0.0), (18.73545, 4.61e-06), (20.84308, 1.196e-05), (22.96603, 2.25e-05), (25.08605, 3.674e-05), (27.18344, 5.521e-05), (29.28199, 7.908e-05), (31.3891, 0.00010995), (33.49223, 0.00014996), (35.58614, 0.00020288), (37.66405, 0.00027613), (39.75352, 0.00039246), (41.5, 0.00069898), (39.42473, 0.00107224), (37.34165, 0.00129023), (35.26151, 0.00149005), (33.17648, 0.0016864), (31.10107, 0.00188428), (29.02104, 0.00208953), (26.94305, 0.00230557), (24.85558, 0.00253814), (22.77987, 0.00279027), (20.69556, 0.00307157), (18.61284, 0.0033908), (16.53242, 0.0037624), (14.44954, 0.00421), (12.37106, 0.00476957), (10.29528, 0.00550807), (8.22028, 0.00655934), (6.14492, 0.0082362)), 'rate': OFF, 'dependencies': 0}, 'concreteTensionStiffening': {'temperatureDependency': OFF, 'table': ((2.34493, 0.0), (2.49187, 1.9e-06), (2.64005, 4.46e-06), (2.78668, 8.34e-06), (2.93, 2.067e-05), (2.78159, 3.705e-05), (2.63351, 4.854e-05), (2.4851, 5.958e-05), (2.33811, 7.057e-05), (2.19125, 8.192e-05), (2.04454, 9.383e-05), (1.89632, 0.00010672), (1.74966, 0.00012061), (1.60315, 0.00013601), (1.45634, 0.0001535), (1.30921, 0.00017391), (1.16239, 0.00019838), (1.01534, 0.00022901), (0.86878, 0.00026914), (0.72213, 0.00032566), (0.57551, 0.00041319), (0.42894, 0.00056994)), 'rate': OFF, 'dependencies': 0, 'type': STRAIN}, 'dependencies': 0, 'concreteTensionDamage': {'temperatureDependency': OFF, 'table': ((0.0, 0.0), (0.0022835, 1.9e-06), (0.00904427, 4.46e-06), (0.02153085, 8.34e-06), (0.06145088, 2.067e-05), (0.1042219, 3.705e-05), (0.13545873, 4.854e-05), (0.1673063, 5.958e-05), (0.20047512, 7.057e-05), (0.23571659, 8.192e-05), (0.27334189, 9.383e-05), (0.31408983, 0.00010672), (0.35737682, 0.00012061), (0.4038158, 0.00013601), (0.45379573, 0.0001535), (0.50755262, 0.00017391), (0.56500601, 0.00019838), (0.6263824, 0.00022901), (0.69111429, 0.00026914), (0.75869171, 0.00032566), (0.82736886, 0.00041319), (0.8937017, 0.00056994)), 'dependencies': 0, 'compressionRecovery': 1.0, 'type': STRAIN}, 'table': ((38.0, 0.1, 1.16, 0.66667, 1e-05),)}, 'materialIdentifier': '', 'description': 'ConcreteData\nCalculate By: PolarisCDP plugins\nSource: http://xcbjx.taobao.com'}""")
        if strength == "C70":
            createMaterialFromDataString('TestNew1', 'C70', '2018',
                                     """{'name': 'C70', 'elastic': {'temperatureDependency': OFF, 'moduli': LONG_TERM, 'noCompression': OFF, 'noTension': OFF, 'dependencies': 0, 'table': ((37000.0, 0.2),), 'type': ISOTROPIC}, 'density': {'temperatureDependency': OFF, 'table': ((2.46e-09,),), 'dependencies': 0, 'fieldName': '', 'distributionType': UNIFORM}, 'concreteDamagedPlasticity': {'temperatureDependency': OFF, 'concreteCompressionDamage': {'temperatureDependency': OFF, 'table': ((0.0, 0.0), (0.00070565, 3.26e-06), (0.0027521, 9.13e-06), (0.00631393, 1.813e-05), (0.01144977, 3.081e-05), (0.01816465, 4.773e-05), (0.02664287, 7.005e-05), (0.03715562, 9.939e-05), (0.05004835, 0.00013798), (0.06600651, 0.00018968), (0.08645442, 0.00026209), (0.11571424, 0.00037718), (0.18239858, 0.00068328), (0.24626079, 0.00105394), (0.28042367, 0.0012714), (0.31168907, 0.00147272), (0.34182299, 0.00166784), (0.37241522, 0.00186729), (0.40343158, 0.0020718), (0.43557588, 0.0022876), (0.46900661, 0.00251809), (0.50404055, 0.00276892), (0.54070145, 0.00304524), (0.57951369, 0.00335862), (0.62080438, 0.0037239), (0.66460311, 0.00416106), (0.71123511, 0.00470721), (0.76081902, 0.00542694), (0.81335699, 0.00645149), (0.86825929, 0.00808748)), 'dependencies': 0, 'tensionRecovery': 0.0}, 'concreteCompressionHardening': {'temperatureDependency': OFF, 'table': ((17.83293, 0.0), (20.10464, 3.26e-06), (22.34837, 9.13e-06), (24.61244, 1.813e-05), (26.87747, 3.081e-05), (29.12239, 4.773e-05), (31.37261, 7.005e-05), (33.63607, 9.939e-05), (35.89923, 0.00013798), (38.15608, 0.00018968), (40.39837, 0.00026209), (42.63341, 0.00037718), (44.5, 0.00068328), (42.26893, 0.00105394), (40.03293, 0.0012714), (37.77902, 0.00147272), (35.54941, 0.00166784), (33.29618, 0.00186729), (31.06058, 0.0020718), (28.81799, 0.0022876), (26.57827, 0.00251809), (24.33801, 0.00276892), (22.11118, 0.00304524), (19.88073, 0.00335862), (17.6437, 0.0037239), (15.41259, 0.00416106), (13.1822, 0.00470721), (10.95414, 0.00542694), (8.7261, 0.00645149), (6.4996, 0.00808748)), 'rate': OFF, 'dependencies': 0}, 'concreteTensionStiffening': {'temperatureDependency': OFF, 'table': ((2.39295, 0.0), (2.5429, 1.94e-06), (2.69411, 4.54e-06), (2.84375, 8.48e-06), (2.99, 2.097e-05), (2.83935, 3.714e-05), (2.68905, 4.848e-05), (2.5384, 5.936e-05), (2.3889, 7.021e-05), (2.239, 8.143e-05), (2.08867, 9.324e-05), (1.93812, 0.00010588), (1.78822, 0.00011956), (1.6376, 0.00013479), (1.48716, 0.00015201), (1.3374, 0.00017191), (1.18725, 0.00019581), (1.03718, 0.00022559), (0.88749, 0.00026451), (0.7379, 0.00031905), (0.58829, 0.00040318), (0.43877, 0.00055306)), 'rate': OFF, 'dependencies': 0, 'type': STRAIN}, 'dependencies': 0, 'concreteTensionDamage': {'temperatureDependency': OFF, 'table': ((0.0, 0.0), (0.00232232, 1.94e-06), (0.00918518, 4.54e-06), (0.02182904, 8.48e-06), (0.06209024, 2.097e-05), (0.10379921, 3.714e-05), (0.13416426, 4.848e-05), (0.16511607, 5.936e-05), (0.19743315, 7.021e-05), (0.23192331, 8.143e-05), (0.26894374, 9.324e-05), (0.30874692, 0.00010588), (0.35136042, 0.00011956), (0.39745064, 0.00013479), (0.44702493, 0.00015201), (0.50012552, 0.00017191), (0.55732107, 0.00019581), (0.61850839, 0.00022559), (0.68337326, 0.00026451), (0.75137177, 0.00031905), (0.82097416, 0.00040318), (0.88879468, 0.00055306)), 'dependencies': 0, 'compressionRecovery': 1.0, 'type': STRAIN}, 'table': ((38.0, 0.1, 1.16, 0.66667, 1e-05),)}, 'materialIdentifier': '', 'description': 'ConcreteData\nCalculate By: PolarisCDP plugins\nSource: http://xcbjx.taobao.com'}""")
        if strength == "C75":
            createMaterialFromDataString('TestNew1', 'C75', '2018',
                                     """{'name': 'C75', 'elastic': {'temperatureDependency': OFF, 'moduli': LONG_TERM, 'noCompression': OFF, 'noTension': OFF, 'dependencies': 0, 'table': ((37500.0, 0.2),), 'type': ISOTROPIC}, 'density': {'temperatureDependency': OFF, 'table': ((2.47e-09,),), 'dependencies': 0, 'fieldName': '', 'distributionType': UNIFORM}, 'concreteDamagedPlasticity': {'temperatureDependency': OFF, 'concreteCompressionDamage': {'temperatureDependency': OFF, 'table': ((0.0, 0.0), (0.00038211, 1.89e-06), (0.00167218, 6.35e-06), (0.00421643, 1.388e-05), (0.00818906, 2.504e-05), (0.01367327, 4.042e-05), (0.02087953, 6.119e-05), (0.0298933, 8.837e-05), (0.0412332, 0.00012462), (0.05559306, 0.0001738), (0.07439151, 0.0002436), (0.10127145, 0.00035356), (0.1676845, 0.00066811), (0.22901478, 0.00103683), (0.26228364, 0.00125521), (0.29242002, 0.00145419), (0.32201572, 0.00164957), (0.35186041, 0.00184679), (0.38236456, 0.00204942), (0.41428181, 0.00226392), (0.44743188, 0.00249118), (0.48224069, 0.00273719), (0.51916125, 0.00300978), (0.55849079, 0.00331837), (0.60019575, 0.00367374), (0.64486079, 0.00409892), (0.69271131, 0.00462771), (0.74389439, 0.0053203), (0.79861643, 0.0063012), (0.85638399, 0.00785671)), 'dependencies': 0, 'tensionRecovery': 0.0}, 'concreteCompressionHardening': {'temperatureDependency': OFF, 'table': ((18.96688, 0.0), (21.36884, 1.89e-06), (23.74545, 6.35e-06), (26.14789, 1.388e-05), (28.55571, 2.504e-05), (30.94651, 4.042e-05), (33.34733, 6.119e-05), (35.71942, 8.837e-05), (38.10509, 0.00012462), (40.50014, 0.0001738), (42.89926, 0.0002436), (45.2761, 0.00035356), (47.4, 0.00066811), (45.01945, 0.00103683), (42.62398, 0.00125521), (40.24957, 0.00145419), (37.86883, 0.00164957), (35.48959, 0.00184679), (33.11934, 0.00204942), (30.72834, 0.00226392), (28.35304, 0.00249118), (25.98156, 0.00273719), (23.60214, 0.00300978), (21.2154, 0.00331837), (18.84113, 0.00367374), (16.4629, 0.00409892), (14.08524, 0.00462771), (11.71268, 0.0053203), (9.33875, 0.0063012), (6.96722, 0.00785671)), 'rate': OFF, 'dependencies': 0}, 'concreteTensionStiffening': {'temperatureDependency': OFF, 'table': ((2.44097, 0.0), (2.59393, 1.97e-06), (2.74817, 4.63e-06), (2.90081, 8.63e-06), (3.05, 2.127e-05), (2.89746, 3.72e-05), (2.74261, 4.857e-05), (2.59001, 5.929e-05), (2.4357, 7.017e-05), (2.28078, 8.142e-05), (2.12757, 9.311e-05), (1.97358, 0.00010564), (1.81976, 0.00011924), (1.66627, 0.00013425), (1.51344, 0.00015115), (1.36023, 0.00017078), (1.20742, 0.0001942), (1.05466, 0.00022332), (0.90173, 0.00026146), (0.74908, 0.00031479), (0.59649, 0.00039696), (0.44391, 0.00054359)), 'rate': OFF, 'dependencies': 0, 'type': STRAIN}, 'dependencies': 0, 'concreteTensionDamage': {'temperatureDependency': OFF, 'table': ((0.0, 0.0), (0.00236154, 1.97e-06), (0.00932735, 4.63e-06), (0.02212956, 8.63e-06), (0.06273331, 2.127e-05), (0.1033638, 3.72e-05), (0.13335801, 4.857e-05), (0.16342094, 5.929e-05), (0.19543804, 7.017e-05), (0.22971597, 8.142e-05), (0.26606482, 9.311e-05), (0.30535011, 0.00010564), (0.34763224, 0.00011924), (0.39313821, 0.00013425), (0.44202602, 0.00015115), (0.49489025, 0.00017078), (0.55168675, 0.0001942), (0.61265124, 0.00022332), (0.67776796, 0.00026146), (0.74627043, 0.00031479), (0.81674554, 0.00039696), (0.88592092, 0.00054359)), 'dependencies': 0, 'compressionRecovery': 1.0, 'type': STRAIN}, 'table': ((38.0, 0.1, 1.16, 0.66667, 1e-05),)}, 'materialIdentifier': '', 'description': 'ConcreteData\nCalculate By: PolarisCDP plugins\nSource: http://xcbjx.taobao.com'}""")
        if strength == "C80":
            createMaterialFromDataString('TestNew1', 'C80', '2018',
                                     """{'name': 'C80', 'elastic': {'temperatureDependency': OFF, 'moduli': LONG_TERM, 'noCompression': OFF, 'noTension': OFF, 'dependencies': 0, 'table': ((38000.0, 0.2),), 'type': ISOTROPIC}, 'density': {'temperatureDependency': OFF, 'table': ((2.48e-09,),), 'dependencies': 0, 'fieldName': '', 'distributionType': UNIFORM}, 'concreteDamagedPlasticity': {'temperatureDependency': OFF, 'concreteCompressionDamage': {'temperatureDependency': OFF, 'table': ((0.0, 0.0), (0.00013927, 7.4e-07), (0.00088384, 4.12e-06), (0.00265436, 1.046e-05), (0.00572026, 2.039e-05), (0.01022421, 3.453e-05), (0.01639805, 5.405e-05), (0.02436443, 8.004e-05), (0.03463502, 0.00011516), (0.04790982, 0.0001634), (0.06533863, 0.00023155), (0.09105349, 0.00034155), (0.15461188, 0.00065361), (0.21380465, 0.00102141), (0.24610049, 0.00123972), (0.2758315, 0.00144089), (0.30474097, 0.00163551), (0.33406133, 0.0018321), (0.36422857, 0.0020344), (0.39563391, 0.00224629), (0.42893949, 0.00247425), (0.46382022, 0.00271892), (0.50084547, 0.00298856), (0.54044228, 0.00329294), (0.58269852, 0.00364315), (0.62812963, 0.00406056), (0.67702389, 0.00457767), (0.72972787, 0.005254), (0.78633505, 0.00620648), (0.84672305, 0.00771541)), 'dependencies': 0, 'tensionRecovery': 0.0}, 'concreteCompressionHardening': {'temperatureDependency': OFF, 'table': ((20.13669, 0.0), (22.66041, 7.4e-07), (25.22965, 4.12e-06), (27.75918, 1.046e-05), (30.29825, 2.039e-05), (32.82312, 3.453e-05), (35.36221, 5.405e-05), (37.87427, 8.004e-05), (40.40367, 0.00011516), (42.94522, 0.0001634), (45.45925, 0.00023155), (47.9868, 0.00034155), (50.2, 0.00065361), (47.67032, 0.00102141), (45.13404, 0.00123972), (42.59334, 0.00144089), (40.08285, 0.00163551), (37.56992, 0.0018321), (35.05935, 0.0020344), (32.54834, 0.00224629), (30.01043, 0.00247425), (27.4932, 0.00271892), (24.97531, 0.00298856), (22.44974, 0.00329294), (19.93228, 0.00364315), (17.41296, 0.00406056), (14.89613, 0.00457767), (12.38078, 0.005254), (9.87059, 0.00620648), (7.35857, 0.00771541)), 'rate': OFF, 'dependencies': 0}, 'concreteTensionStiffening': {'temperatureDependency': OFF, 'table': ((2.48899, 0.0), (2.64495, 2.01e-06), (2.80223, 4.71e-06), (2.95788, 8.77e-06), (3.11, 2.156e-05), (2.95351, 3.744e-05), (2.79666, 4.864e-05), (2.63959, 5.937e-05), (2.48337, 7.008e-05), (2.32606, 8.118e-05), (2.16994, 9.272e-05), (2.01236, 0.00010515), (1.85626, 0.00011849), (1.69947, 0.00013329), (1.54385, 0.00014986), (1.38776, 0.00016908), (1.23161, 0.00019202), (1.0755, 0.00022048), (0.91959, 0.00025757), (0.76389, 0.00030929), (0.60826, 0.00038871), (0.45267, 0.00052991)), 'rate': OFF, 'dependencies': 0, 'type': STRAIN}, 'dependencies': 0, 'concreteTensionDamage': {'temperatureDependency': OFF, 'table': ((0.0, 0.0), (0.00240114, 2.01e-06), (0.00947073, 4.71e-06), (0.02243225, 8.77e-06), (0.06337974, 2.156e-05), (0.10339657, 3.744e-05), (0.13253992, 4.864e-05), (0.16224474, 5.937e-05), (0.19338488, 7.008e-05), (0.22685202, 8.118e-05), (0.26250306, 9.272e-05), (0.30125504, 0.00010515), (0.34268106, 0.00011849), (0.38763367, 0.00013329), (0.43587074, 0.00014986), (0.48817766, 0.00016908), (0.54469664, 0.00019202), (0.60557576, 0.00022048), (0.670706, 0.00025757), (0.7395919, 0.00030929), (0.810902, 0.00038871), (0.88145451, 0.00052991)), 'dependencies': 0, 'compressionRecovery': 1.0, 'type': STRAIN}, 'table': ((38.0, 0.1, 1.16, 0.66667, 1e-05),)}, 'materialIdentifier': '', 'description': 'ConcreteData\nCalculate By: PolarisCDP plugins\nSource: http://xcbjx.taobao.com'}""")

        createMaterialFromDataString('TestNew1', 'Material-3', '2018',
                                     """{'maxsDamageInitiation': {'temperatureDependency': OFF, 'definition': MSFLD, 'direction': NMORI, 'fnt': 10.0, 'position': CENTROID, 'damageEvolution': {'temperatureDependency': OFF, 'dependencies': 0, 'softening': LINEAR, 'power': None, 'table': ((10.0,),), 'mixedModeBehavior': MODE_INDEPENDENT, 'type': DISPLACEMENT, 'modeMixRatio': ENERGY, 'degradation': MAXIMUM}, 'table': ((2650.0, 2.65, 2.65),), 'ks': 0.0, 'tolerance': 0.05, 'dependencies': 0, 'frequency': 1, 'feq': 10.0, 'alpha': 0.0, 'fnn': 10.0, 'omega': 1.0, 'numberImperfections': 4, 'damageStabilizationCohesive': {'cohesiveCoeff': 0.0001}}, 'materialIdentifier': '', 'description': '', 'elastic': {'temperatureDependency': OFF, 'moduli': LONG_TERM, 'noCompression': OFF, 'noTension': OFF, 'dependencies': 0, 'table': ((10000000.0, 10000.0, 10000.0),), 'type': TRACTION}, 'name': 'Material-3'}""")
        time.sleep(3);
    except:
        print("[info] 基体材料属性缺失")
    #### 纤维材料
    mdb.models['TestNew1'].Material(name='fiber')
    mdb.models['TestNew1'].materials['fiber'].Elastic(table=((210000.0, 0.3), ))
    mdb.models['TestNew1'].materials['fiber'].Plastic(table=((2778.0, 0.0), (2990.0,
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
    # ###################
    # 设置最大增量步数
    mdb.models['TestNew1'].StaticStep(name='Step-1', previous='Initial', 
        maxNumInc=20000, initialInc=0.001, minInc=1e-12, nlgeom=ON)
    ####################
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Step-1')
    mdb.models['TestNew1'].steps['Step-1'].setValues(matrixSolver=DIRECT, 
        matrixStorage=UNSYMMETRIC)
    mdb.models['TestNew1'].steps['Step-1'].control.setValues(allowPropagation=OFF, 
        resetDefaultValues=OFF, discontinuous=ON, timeIncrementation=(8.0, 
        10.0, 9.0, 16.0, 10.0, 4.0, 12.0, 20.0, 6.0, 3.0, 50.0))
    mdb.models['TestNew1'].fieldOutputRequests['F-Output-1'].setValues(variables=(
        'S', 'PE', 'PEEQ', 'PEMAG', 'LE', 'U', 'RF', 'CSTRESS', 'CDISP', 'STATUS',
        'DAMAGEC', 'DAMAGET', 'SDEG', 'MVF'))
    ## 全局接触部分
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
    if pattern=="TPB":

        # 提前设置好材料 concrete Material-3
        mdb.models['TestNew1'].CohesiveSection(name='coh', material='Material-3',
                                               response=TRACTION_SEPARATION, outOfPlaneThickness=None)
        p = mdb.models['TestNew1'].parts['COH_INSERT']
        region = p.sets['CO_SET']
        p = mdb.models['TestNew1'].parts['COH_INSERT']
        p.SectionAssignment(region=region, sectionName='coh', offset=0.0,
                            offsetType=MIDDLE_SURFACE, offsetField='',
                            thicknessAssignment=FROM_SECTION)
        mdb.models['TestNew1'].HomogeneousSolidSection(name='matrix', material=strength,
                                                       thickness=10.0)
        p = mdb.models['TestNew1'].parts['COH_INSERT']
        region = p.sets['MATRIX']
        p = mdb.models['TestNew1'].parts['COH_INSERT']
        p.SectionAssignment(region=region, sectionName='matrix', offset=0.0,
                            offsetType=MIDDLE_SURFACE, offsetField='',
                            thicknessAssignment=FROM_SECTION)
        session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=OFF,
                                                               engineeringFeatures=OFF, mesh=ON)
        session.viewports['Viewport: 1'].partDisplay.meshOptions.setValues(
            meshTechnique=ON)

        # 设置coh单元格格式
        elemType1 = mesh.ElemType(elemCode=COH2D4, elemLibrary=STANDARD,
                                  elemDeletion=ON, viscosity=0.0001, maxDegradation=1)
        p = mdb.models['TestNew1'].parts['COH_INSERT']
        p.allSets["CO_SET"].elements

        elems1 = p.allSets["CO_SET"].elements
        pickedRegions = (elems1,)
        p.setElementType(regions=pickedRegions, elemTypes=(elemType1,))

        session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=ON,
                                                               engineeringFeatures=ON, mesh=OFF)
        session.viewports['Viewport: 1'].partDisplay.meshOptions.setValues(
            meshTechnique=OFF)
        session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=OFF,
                                                               engineeringFeatures=OFF)
        session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
            referenceRepresentation=ON)
        s1 = mdb.models['TestNew1'].ConstrainedSketch(name='__profile__',
                                                      sheetSize=200.0)
        g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
        s1.setPrimaryObject(option=STANDALONE)
        s1.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(12.5, 0.0))
        s1.delete(objectList=(g.findAt((-12.5, 0.0)),))
        s1.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(8.75, -2.5))
        s1.RadialDimension(curve=g.findAt((-8.75, 2.5)), textPoint=(-18.8545761108398,
                                                                    -7.75943374633789), radius=10.0)
        session.viewports['Viewport: 1'].view.setValues(nearPlane=169.236,
                                                        farPlane=207.888, width=114.366, height=45.3934,
                                                        cameraPosition=(
                                                            4.98894, -0.592676, 188.562),
                                                        cameraTarget=(4.98894, -0.592676, 0))
        s1.Line(point1=(-10.0, 0.0), point2=(10.0, 0.0))
        s1.HorizontalConstraint(entity=g.findAt((0.0, 0.0)), addUndoState=False)
        s1.PerpendicularConstraint(entity1=g.findAt((-9.615239, 2.747211)),
                                   entity2=g.findAt((0.0, 0.0)), addUndoState=False)
        s1.CoincidentConstraint(entity1=v.findAt((-10.0, 0.0)), entity2=g.findAt((
            -9.615239, 2.747211)), addUndoState=False)
        s1.CoincidentConstraint(entity1=v.findAt((10.0, 0.0)), entity2=g.findAt((
            -9.615239, 2.747211)), addUndoState=False)
        s1.autoTrimCurve(curve1=g.findAt((-9.615239, 2.747211)), point1=(
            4.29483890533447, -1.66327619552612))
        s1.autoTrimCurve(curve1=g.findAt((1.387012, 9.903343)), point1=(
            12.1968584060669, -3.69741582870483))
        s1.autoTrimCurve(curve1=g.findAt((1.387012, 9.903343)), point1=(
            9.63404560089111, -2.19857549667358))
        s1.undo()
        s1.undo()
        s1.undo()
        s1.autoTrimCurve(curve1=g.findAt((-9.615239, 2.747211)), point1=(
            20.4192314147949, 2.61912393569946))
        p = mdb.models['TestNew1'].Part(name='pin', dimensionality=TWO_D_PLANAR,
                                        type=ANALYTIC_RIGID_SURFACE)
        p = mdb.models['TestNew1'].parts['pin']
        p.AnalyticRigidSurf2DPlanar(sketch=s1)
        s1.unsetPrimaryObject()
        p = mdb.models['TestNew1'].parts['pin']

        print ("创建pin成功")
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        del mdb.models['TestNew1'].sketches['__profile__']

        #  创建bottompin
        s = mdb.models['TestNew1'].ConstrainedSketch(name='__profile__',
                                                     sheetSize=200.0)
        g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
        s.setPrimaryObject(option=STANDALONE)
        session.viewports['Viewport: 1'].view.setValues(nearPlane=149.088,
                                                        farPlane=228.036, width=233.599, height=89.6575,
                                                        cameraPosition=(
                                                            47.5438, -11.1991, 188.562),
                                                        cameraTarget=(47.5438, -11.1991, 0))
        s.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(15.0, 3.75))
        s.RadialDimension(curve=g.findAt((-15.0, -3.75)), textPoint=(-23.4520072937012,
                                                                     -10.1057472229004), radius=10.0)
        session.viewports['Viewport: 1'].view.setValues(nearPlane=165.943,
                                                        farPlane=211.18, width=133.851, height=51.3733, cameraPosition=(
                23.2842, -4.59823, 188.562), cameraTarget=(23.2842, -4.59823, 0))
        s.Line(point1=(-10.0, 0.0), point2=(10.0, 0.0))
        s.HorizontalConstraint(entity=g.findAt((0.0, 0.0)), addUndoState=False)
        s.PerpendicularConstraint(entity1=g.findAt((-9.701425, -2.425356)),
                                  entity2=g.findAt((0.0, 0.0)), addUndoState=False)
        s.CoincidentConstraint(entity1=v.findAt((-10.0, 0.0)), entity2=g.findAt((
            -9.701425, -2.425356)), addUndoState=False)
        s.CoincidentConstraint(entity1=v.findAt((10.0, 0.0)), entity2=g.findAt((
            -9.701425, -2.425356)), addUndoState=False)
        s.autoTrimCurve(curve1=g.findAt((-9.701425, -2.425356)), point1=(
            -1.64888763427734, -9.23435401916504))
        p = mdb.models['TestNew1'].Part(name='pin-bottom', dimensionality=TWO_D_PLANAR,
                                        type=ANALYTIC_RIGID_SURFACE)
        p = mdb.models['TestNew1'].parts['pin-bottom']
        p.AnalyticRigidSurf2DPlanar(sketch=s)
        s.unsetPrimaryObject()
        p = mdb.models['TestNew1'].parts['pin-bottom']
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        del mdb.models['TestNew1'].sketches['__profile__']

        session.viewports['Viewport: 1'].view.setValues(nearPlane=31.7368,
                                                        farPlane=57.7059, width=104.24, height=41.3743,
                                                        viewOffsetX=22.0862,
                                                        viewOffsetY=-4.99483)
        a = mdb.models['TestNew1'].rootAssembly
        a.regenerate()
        session.viewports['Viewport: 1'].setValues(displayedObject=a)
        session.viewports['Viewport: 1'].assemblyDisplay.setValues(
            adaptiveMeshConstraints=OFF)
        a1 = mdb.models['TestNew1'].rootAssembly
        p = mdb.models['TestNew1'].parts['pin']
        a1.Instance(name='pin-1', part=p, dependent=ON)
        session.viewports['Viewport: 1'].view.setValues(nearPlane=807.203,
                                                        farPlane=890.796, width=248.117, height=98.4814,
                                                        viewOffsetX=16.3477,
                                                        viewOffsetY=31.7718)
        a1 = mdb.models['TestNew1'].rootAssembly
        a1.translate(instanceList=('pin-1',), vector=(200.0, 110.0, 0.0))
        session.viewports['Viewport: 1'].view.setValues(nearPlane=769.302,
                                                        farPlane=928.697, width=530.74, height=210.659,
                                                        viewOffsetX=24.6348,
                                                        viewOffsetY=18.7541)
        a1 = mdb.models['TestNew1'].rootAssembly
        p = mdb.models['TestNew1'].parts['pin-bottom']
        a1.Instance(name='pin-bottom-1', part=p, dependent=ON)
        session.viewports['Viewport: 1'].view.setValues(nearPlane=762.215,
                                                        farPlane=935.784, width=516.918, height=205.172,
                                                        viewOffsetX=26.4826,
                                                        viewOffsetY=-9.70818)
        a1 = mdb.models['TestNew1'].rootAssembly
        a1.translate(instanceList=('pin-bottom-1',), vector=(50.0, -10.0, 0.0))
        a1 = mdb.models['TestNew1'].rootAssembly
        a1.LinearInstancePattern(instanceList=('pin-bottom-1',), direction1=(1.0, 0.0,
                                                                             0.0), direction2=(0.0, 1.0, 0.0),
                                 number1=2, number2=1, spacing1=300.0,
                                 spacing2=10.0)
        session.viewports['Viewport: 1'].assemblyDisplay.setValues(
            adaptiveMeshConstraints=ON)
        session.viewports['Viewport: 1'].assemblyDisplay.setValues(interactions=ON,
                                                                   constraints=ON, connectors=ON,
                                                                   engineeringFeatures=ON,
                                                                   adaptiveMeshConstraints=OFF)
        session.viewports['Viewport: 1'].view.setValues(nearPlane=825.622,
                                                        farPlane=872.377, width=138.585, height=55.0065,
                                                        viewOffsetX=34.8667,
                                                        viewOffsetY=39.0543)
        mdb.models['TestNew1'].ContactProperty('IntProp-1')
        mdb.models['TestNew1'].interactionProperties['IntProp-1'].TangentialBehavior(
            formulation=FRICTIONLESS)
        mdb.models['TestNew1'].interactionProperties['IntProp-1'].NormalBehavior(
            pressureOverclosure=HARD, allowSeparation=ON,
            constraintEnforcementMethod=DEFAULT)
        a = mdb.models['TestNew1'].rootAssembly
        s1 = a.instances['pin-1'].edges
        side2Edges1 = s1.findAt(((192.454468, 103.437612, 0.0),), ((209.78296,
                                                                    107.927875, 0.0),), ((195.0, 110.0, 0.0),))
        region1 = regionToolset.Region(side2Edges=side2Edges1)
        a = mdb.models['TestNew1'].rootAssembly
        f1 = a.instances['COH_INSERT-1'].elements
        face1Elements1 = f1[3422:3423]
        face2Elements1 = f1[6232:6233]
        face3Elements1 = f1[4543:4544]
        face4Elements1 = f1[6230:6231]
        region2 = regionToolset.Region(face1Elements=face1Elements1,
                                       face2Elements=face2Elements1, face3Elements=face3Elements1,
                                       face4Elements=face4Elements1)
        mdb.models['TestNew1'].SurfaceToSurfaceContactStd(name='Int-1',
                                                          createStepName='Step-1', master=region1, slave=region2,
                                                          sliding=FINITE,
                                                          thickness=ON, interactionProperty='IntProp-1',
                                                          adjustMethod=TOLERANCE,
                                                          initialClearance=OMIT, datumAxis=None, clearanceRegion=None,
                                                          tied=OFF,
                                                          adjustTolerance=0.15)
        session.viewports['Viewport: 1'].view.setValues(nearPlane=818.03,
                                                        farPlane=879.969, width=206.489, height=81.9583,
                                                        viewOffsetX=-84.1546,
                                                        viewOffsetY=-38.2795)
        a = mdb.models['TestNew1'].rootAssembly
        s1 = a.instances['pin-bottom-1'].edges
        side1Edges1 = s1.findAt(((53.70998, -0.713664, 0.0),), ((59.908872, -8.653058,
                                                                 0.0),), ((45.0, -10.0, 0.0),))
        region1 = regionToolset.Region(side1Edges=side1Edges1)
        a = mdb.models['TestNew1'].rootAssembly
        f1 = a.instances['COH_INSERT-1'].elements
        face1Elements1 = f1[1998:1999]
        face2Elements1 = f1[984:985]
        face3Elements1 = f1[2567:2568]
        face4Elements1 = f1[1979:1980]
        region2 = regionToolset.Region(face1Elements=face1Elements1,
                                       face2Elements=face2Elements1, face3Elements=face3Elements1,
                                       face4Elements=face4Elements1)
        mdb.models['TestNew1'].SurfaceToSurfaceContactStd(name='Int-2',
                                                          createStepName='Step-1', master=region1, slave=region2,
                                                          sliding=FINITE,
                                                          thickness=ON, interactionProperty='IntProp-1',
                                                          adjustMethod=TOLERANCE,
                                                          initialClearance=OMIT, datumAxis=None, clearanceRegion=None,
                                                          tied=OFF,
                                                          adjustTolerance=0.15)
        session.viewports['Viewport: 1'].view.setValues(nearPlane=829.576,
                                                        farPlane=868.423, width=115.114, height=45.6902,
                                                        viewOffsetX=165.043,
                                                        viewOffsetY=-50.5247)
        a = mdb.models['TestNew1'].rootAssembly
        s1 = a.instances['pin-bottom-1-lin-2-1'].edges
        side1Edges1 = s1.findAt(((353.70998, -0.713664, 0.0),), ((359.908872,
                                                                  -8.653058, 0.0),), ((345.0, -10.0, 0.0),))
        region1 = regionToolset.Region(side1Edges=side1Edges1)
        a = mdb.models['TestNew1'].rootAssembly
        f1 = a.instances['COH_INSERT-1'].elements
        face1Elements1 = f1[274:275]
        face2Elements1 = f1[353:354]
        face3Elements1 = f1[1920:1921]
        face4Elements1 = f1[1917:1918]
        region2 = regionToolset.Region(face1Elements=face1Elements1,
                                       face2Elements=face2Elements1, face3Elements=face3Elements1,
                                       face4Elements=face4Elements1)
        mdb.models['TestNew1'].SurfaceToSurfaceContactStd(name='Int-3',
                                                          createStepName='Step-1', master=region1, slave=region2,
                                                          sliding=FINITE,
                                                          thickness=ON, interactionProperty='IntProp-1',
                                                          adjustMethod=TOLERANCE,
                                                          initialClearance=OMIT, datumAxis=None, clearanceRegion=None,
                                                          tied=OFF,
                                                          adjustTolerance=0.15)
        session.viewports['Viewport: 1'].view.setValues(nearPlane=759.82,
                                                        farPlane=938.179, width=531.133, height=210.814,
                                                        viewOffsetX=40.8702,
                                                        viewOffsetY=-0.0419159)
        session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                   predefinedFields=ON, interactions=OFF,
                                                                   constraints=OFF,
                                                                   engineeringFeatures=OFF)
        p1 = mdb.models['TestNew1'].parts['pin']
        session.viewports['Viewport: 1'].setValues(displayedObject=p1)
        session.viewports['Viewport: 1'].view.setValues(nearPlane=39.2662,
                                                        farPlane=50.1766, width=35.9645, height=14.2748,
                                                        viewOffsetX=2.99374,
                                                        viewOffsetY=0.252552)
        p = mdb.models['TestNew1'].parts['pin']
        v2, e, d1, n = p.vertices, p.edges, p.datums, p.nodes
        p.ReferencePoint(point=p.InterestingPoint(edge=e.findAt(coordinates=(-7.545532,
                                                                             -6.562388, 0.0)), rule=CENTER))
        p1 = mdb.models['TestNew1'].parts['pin-bottom']
        session.viewports['Viewport: 1'].setValues(displayedObject=p1)
        p = mdb.models['TestNew1'].parts['pin-bottom']
        v1, e1, d2, n1 = p.vertices, p.edges, p.datums, p.nodes
        p.ReferencePoint(point=p.InterestingPoint(edge=e1.findAt(coordinates=(-5.0,
                                                                              0.0, 0.0)), rule=MIDDLE))
        a = mdb.models['TestNew1'].rootAssembly
        a.regenerate()
        session.viewports['Viewport: 1'].setValues(displayedObject=a)
        a = mdb.models['TestNew1'].rootAssembly
        r1 = a.instances['pin-1'].referencePoints
        refPoints1 = (r1[2],)
        region = regionToolset.Region(referencePoints=refPoints1)
        mdb.models['TestNew1'].DisplacementBC(name='BC-1', createStepName='Step-1',
                                              region=region, u1=0.0, u2=-5.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                              distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['TestNew1'].rootAssembly
        r1 = a.instances['pin-bottom-1'].referencePoints
        refPoints1 = (r1[2],)
        r2 = a.instances['pin-bottom-1-lin-2-1'].referencePoints
        refPoints2 = (r2[2],)
        region = regionToolset.Region(referencePoints=(refPoints1, refPoints2,))
        mdb.models['TestNew1'].DisplacementBC(name='BC-2', createStepName='Step-1',
                                              region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                              distributionType=UNIFORM, fieldName='', localCsys=None)
        session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=OFF, bcs=OFF,
                                                                   predefinedFields=OFF, interactions=ON,
                                                                   constraints=ON,
                                                                   engineeringFeatures=ON)
        session.viewports['Viewport: 1'].assemblyDisplay.setValues(interactions=OFF,
                                                                   constraints=OFF, connectors=OFF,
                                                                   engineeringFeatures=OFF,
                                                                   adaptiveMeshConstraints=ON)

if __name__ == "__main__":
    Fibre_insert(modelName,partName,variable,uel_mode,pattern,diameter,thick,interact,strength)