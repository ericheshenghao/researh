# -*- coding: utf-8 -*-
# coding=gbk
### dummy单元用的是CEP4
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
 
def uel(uel_mode,modelName,partName,fileName,En,Es,tn,ts,Gf1,Gf2,ini_thick,out_thick,constitutive,cpus,interactive):
    ##得到当前路径
    cur_dir = os.getcwd()
    cur_d = cur_dir.split("\\")
    cur = ""
    for i in range(len(cur_d)):
        cur = cur+cur_d[i]+'/'
    uelname = fileName.split("/")[-1] 
    Model = modelName
    if cur+Model+".odb" in session.odbs.keys():
        session.odbs[cur+Model+".odb"].close()
    name_list=[".sim",".sta",".dat",".msg",".prt",".com",".odb",".inp", ".lck"]
    try:
        for i in range(len(name_list)):
            if os.path.exists(Model+name_list[i]):
                os.remove(Model+name_list[i])
    except:
        print("请关闭结果文件")
        os.remove(Model+name_list[i])
    ##用于可视化的用户材料

    
    ##########
    if uel_mode:
        mdb.models[Model].Material(name='Dummymat')
        mdb.models[Model].materials['Dummymat'].UserMaterial(
            mechanicalConstants=(1e-11, 0.3))
        mdb.models[Model].materials['Dummymat'].Depvar(n=7)
        ###分析步也可以作为参数
        try:
            mdb.models[Model].FieldOutputRequest(name='F-Output-10', 
                createStepName='Step-1', variables=('SDV', ))
        except:
            print("请先创建分析步")
         ###指派dummt界面
        mdb.models[Model].CohesiveSection(name='DUMMY', material='Dummymat', 
            response=TRACTION_SEPARATION, outOfPlaneThickness=None)
        p = mdb.models[Model].parts[partName]
        # if 'DUMMY' in p.sets:
        #     print("已有COH截面不再重复生成")
        # else:
        region = p.sets['DUMMY']
        p.SectionAssignment(region=region, sectionName='DUMMY', offset=0.0, 
                offsetType=MIDDLE_SURFACE, offsetField='', 
                thicknessAssignment=FROM_SECTION)
        ####COH单元的数量
        coh_num=len(p.sets['DUMMY'].elements)
        ####起始COH单元的表号，可以修改uel了
        ini_num=p.sets['DUMMY'].elements[0].label-coh_num
        mdb.Job(name=Model, model=Model, description='', type=ANALYSIS, 
            atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
            memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
            explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
            modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine="", 
            scratch='', resultsFormat=ODB, parallelizationMethodExplicit=DOMAIN, 
            numDomains=1, activateLoadBalancing=False, multiprocessingMode=DEFAULT, 
            numCpus=1, numGPUs=0)
        mdb.jobs[Model].writeInput(consistencyChecking=OFF)
    ##写入inp文件
    jobname=Model
    ##修改inp文件的参数
    change_Para(cur_dir,modelName,fileName,En,Es,tn,ts,Gf1,Gf2,ini_thick,out_thick,constitutive,ini_num,coh_num)
    #将inp文件和uel提交
    job_submit(cur_dir,fileName,uelname,jobname,cpus,interactive)

def change_Para(cur_dir,modelName,fileName,En,Es,tn,ts,Gf1,Gf2,ini_thick,out_thick,constitutive,ini_num,coh_num):
    inp_file = cur_dir + "\\" + modelName + ".inp"
    file_path = inp_file.split("\\")[0:-1]
    dir_name = ""
    line1 = "*USER ELEMENT,TYPE=u1,NODES=4,PROPERTIES=9,COORDINATES=2,VARIABLES=14,i properties=2\n"
    line2 = "1,2\n"
    line3 = "*Element, type=u1\n"
    line4 = "*UEL PROPERTY, ELSET=CO_SET\n"
    line5 = "%f, %f, %f, %f,%f,%f,%d,%d,\n"%(En,Es,tn,ts,Gf1,Gf2,ini_thick,out_thick)
    line7 =  "*Element, type=COH2D4, ELSET=dummy\n"
    con_dic = {'Linear':1,'Petersson':2,'CEB':3,'Roesler':4,'exponent':5,'customize':6}
    con_num = con_dic[constitutive]
    line6 = "%d,2,2\n"%(con_num)
    for i in range(len(file_path)):
        dir_name += file_path[i]+"\\"
    os.chdir(dir_name)
    ##可读可写用r+
    key_word="=COH2D4"
    flag,index=find_key(inp_file,key_word)
    with open(inp_file,'r+') as fp:
        lines = []
        for line in fp:                 
            lines.append(line)
    if flag:
        lines.insert(index, line1) #在第 LINE-1 行插入
        lines.insert(index+1, line2)
        lines.insert(index+2, line4) #在第 LINE-1 行插入
        lines.insert(index+3, line5)
        lines.insert(index+4, line6)
        lines.insert(index+5, line3)
        del lines[index+6]
    s = ''.join(lines)
    with open(inp_file, 'w') as fp:
        fp.write(s)
    
    ################这部分删掉一些数据

    key_word="** ELEMENT CONTROLS"
    flag,index=find_key(inp_file,key_word)
    with open(inp_file,'r+') as fp:
        lines = []
        for line in fp:                  #内置的迭代器, 效率很高
            lines.append(line)
    if flag:
        del lines[index+1]
        del lines[index+1]
        del lines[index+1]
    s = ''.join(lines)
    with open(inp_file, 'w') as fp:
        fp.write(s)

    ################这部分修改dummy单元的关键字,先给一个绝对用不到的单元名字
    key_word="=CPE4P"
    flag,index=find_key(inp_file,key_word)
    with open(inp_file,'r+') as fp:
        lines = []
        for line in fp:                 
            lines.append(line)
    if flag:
        lines.insert(index, line7)
        del lines[index+1]
    s = ''.join(lines)
    with open(inp_file, 'w') as fp:
        fp.write(s)
    
    ################这部分修改uel中的数据
    new_lines=[]
    with open(fileName, 'r+') as f:
        for  line in f.readlines():
            line=re.sub(r"NELEMENT=\d{1,10}", "NELEMENT=%d"%(coh_num), line, count=0)
            line=re.sub(r"ELEMOFFSET=\d{1,10}", "ELEMOFFSET=%d" % (ini_num), line, count=2, flags=0)
            new_lines.append(line)
    s = ''.join(new_lines)
    with open(fileName, 'w') as fp:
        fp.write(s)
    
##inp和for文件要放在一起
def job_submit(cur_dir,fileName,uelname,jobname,cpus,interactive):
    uel_file=fileName
    # uel_path=uel_file.split("/")[0:-1]
    new_path = cur_dir+"\\"+"%s.for"%(uelname.split(".")[0])
    ##如果不存在就复制文件，存在就提示一下以存在同名字子程序，不覆盖。
    # if os.path.exists(uelname.split(".")[0]+".for"):
    #     print("在当前目录下存在同名文件不执行复制操作")
    # else:
    shutil.copyfile(uel_file, new_path)
    if interactive:
        os.system('call abq2018 job=%s user=%s cpus=%d %s'%(jobname,uelname.split(".")[0],cpus,'interactive'))
    else:
        os.system('call abq2018 job=%s user=%s cpus=%d '%(jobname,uelname.split(".")[0],cpus))
##寻找关键字的函数
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
if __name__ == "__main__":
    uel(uel_mode,modelName,partname,fileName,En,Es,tn,ts,Gf1,Gf2,ini_thick,out_thick,constitutive)
