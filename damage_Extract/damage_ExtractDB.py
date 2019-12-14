# -*- coding: mbcs -*-
# -*- coding: utf-8 -*-
# coding=gbk
from abaqusConstants import *
from abaqusGui import *
from kernelAccess import mdb, session
import os

thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)


###########################################################################
# Class definition
###########################################################################

class Damage_ExtractDB(AFXDataDialog):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form):

        # Construct the base class.
        #

        AFXDataDialog.__init__(self, form, '\xcb\xf0\xc9\xcb\xc3\xe6\xbb\xfd\xbc\xc6\xcb\xe3\xb9\xa4\xbe\xdf',
            self.OK|self.APPLY|self.CANCEL, DIALOG_ACTIONS_SEPARATOR)
            

        okBtn = self.getActionButton(self.ID_CLICKED_OK)
        okBtn.setText('OK')
            

        applyBtn = self.getActionButton(self.ID_CLICKED_APPLY)
        applyBtn.setText('Apply')
            
        frame = FXHorizontalFrame(self, 0, 0,0,0,0, 0,0,0,0)

        # ODB combo
        #
        self.RootComboBox_1 = AFXComboBox(p=frame, ncols=0, nvis=1, text='ODB\xd1\xa1\xcf\xee:', tgt=form.odbNameKw, sel=0)
        self.RootComboBox_1.setMaxVisible(10)
        msgCount = 35
        form.odbNameKw.setTarget(self)
        form.odbNameKw.setSelector(AFXDataDialog.ID_LAST+msgCount)
        msgHandler = str(self.__class__).split('.')[-1] + '.onPartsChanged'
        exec('FXMAPFUNC(self, SEL_COMMAND, AFXDataDialog.ID_LAST+%d, %s)' % (msgCount, msgHandler) )

        # Parts combo
        #
        
        self.ComboBox_1 = AFXComboBox(p=frame, ncols=0, nvis=1, text='\xb2\xbf\xbc\xfe:', tgt=form.instancenameKw, sel=0)
        self.ComboBox_1.setMaxVisible(10)
        self.form=form
        self.ComboBox_2 = AFXComboBox(p=frame, ncols=0, nvis=1, text='SET:', tgt=form.elementSetsKw, sel=0)
        self.ComboBox_2.setMaxVisible(10)
        msgCount4 = 45
        form.instancenameKw.setTarget(self)
        form.instancenameKw.setSelector(AFXDataDialog.ID_LAST+msgCount4)
        msgHandler4=str(self.__class__).split('.')[-1] + '.onComboBox_2elesetChanged'
        exec('FXMAPFUNC(self, SEL_COMMAND, AFXDataDialog.ID_LAST+%d, %s)' % (msgCount4, msgHandler4) )

        AFXTextField(p=self, ncols=12, labelText='\xbc\xe4\xb8\xf4:', tgt=form.NFrasKw, sel=0)
        AFXTextField(p=self, ncols=12, labelText='Frames:', tgt=form.NFraFKw, sel=0)
        AFXTextField(p=self, ncols=12, labelText='\xb2\xce\xca\xfd\xc3\xfb\xb3\xc6:', tgt=form.variableKw, sel=0)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def show(self):

        AFXDataDialog.show(self)

        # Select the current ODB, if there is one
        #
        names = session.odbs.keys()
        names.sort()
        objectType = getCurrentContext()['objectType']
        if objectType == 'ODB':
            self.currentOdbName = getCurrentContext()['objectPath']
        elif names:
            self.currentOdbName = names[0]
        else:
            self.currentOdbName = ''

        self.form.odbNameKw.setValue(self.currentOdbName)

        session.odbs.registerQuery(self.updateRootComboBox_1Odbs)
        #session.odbs.models[self.currentOdbName].parts.registerQuery(self.updateRootComboBox_2eleset)
        session.odbs.registerQuery(self.updateComboBox_2eleset)
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def hide(self):

        AFXDataDialog.hide(self)

        session.odbs.unregisterQuery(self.updateRootComboBox_1Odbs)
        #session.odbs.models[self.currentOdbName].parts.registerQuery(self.updateRootComboBox_2eleset)
        session.odbs.unregisterQuery(self.updateComboBox_2eleset)
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateRootComboBox_1Odbs(self):

        # Update the names in the ODB combo
        #
        self.RootComboBox_1.clearItems()
        names = session.odbs.keys()
        names.sort()
        for name in names:
            self.RootComboBox_1.appendItem(name)

        if names:
            if not self.form.odbNameKw.getValue() in names:
                self.form.odbNameKw.setValue( names[0] )
        else:
            self.form.odbNameKw.setValue('')

        self.onPartsChanged(None, None, None)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onPartsChanged(self, sender, sel, ptr):

        odbName = self.form.odbNameKw.getValue()

        # Update the names in the Parts combo
        #
        self.ComboBox_1.clearItems()
        if odbName:
            names = session.odbs[odbName].parts.keys()
            names.sort()
            for name in names:
                self.ComboBox_1.appendItem(name)

            if names:
                if not self.form.instancenameKw.getValue() in names:
                    self.form.instancenameKw.setValue( names[0] )
            else:
                self.form.instancenameKw.setValue('')

        else:
            self.form.instancenameKw.setValue('')

        self.resize( self.getDefaultWidth(), self.getDefaultHeight() )

        return 1


## 
    def onComboBox_2elesetChanged(self, sender, sel, ptr):    #自定义下拉框函数

        self.updateComboBox_2eleset()
        return 1
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateComboBox_2eleset(self):

        odbName = self.form.odbNameKw.getValue()
        instanceName = self.form.instancenameKw.getValue()
        # Update the names in the Elementsets combo
        #
        self.ComboBox_2.clearItems()
        if odbName:
            names = session.odbs[odbName].rootAssembly.instances['%s-1'%instanceName].elementSets.keys()
            names.sort()
            for name in names:
                self.ComboBox_2.appendItem(name)

            if names:
                if not self.form.elementSetsKw.getValue() in names:
                    self.form.elementSetsKw.setValue( names[0] )
            else:
                self.form.elementSetsKw.setValue('')

        else:
            self.form.elementSetsKw.setValue('')

        self.resize( self.getDefaultWidth(), self.getDefaultHeight() )

