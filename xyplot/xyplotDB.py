# -*- coding: utf-8 -*-
# Do not delete the following import lines
from abaqusConstants import *
from abaqusGui import *
from kernelAccess import mdb, session
import os

thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)


###########################################################################
# Class definition
###########################################################################

class XyplotDB(AFXDataDialog):
    ID_Mybutton = AFXDataDialog.ID_LAST
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form):

        # Construct the base class.
        #
        #创建标题  
        AFXDataDialog.__init__(self, form, 'Easy_plot',
            self.OK|self.APPLY|self.CANCEL, DIALOG_ACTIONS_SEPARATOR) 
          

        okBtn = self.getActionButton(self.ID_CLICKED_OK)
        okBtn.setText('OK') #ok按钮
            

        applyBtn = self.getActionButton(self.ID_CLICKED_APPLY)
        applyBtn.setText('Apply') #Apply按钮
            
        GroupBox_2 = FXGroupBox(p=self, text='DataGroup', opts=FRAME_GROOVE|LAYOUT_FILL_X)
        #新增控件组
        frame = FXHorizontalFrame(GroupBox_2, 0, 0,0,0,0, 0,0,0,0)
        self.PICK=FXCheckButton(p=frame,        
            text='PICK ENTITY', tgt=form.PICKw, sel=0)

        pickHf = FXHorizontalFrame(p=frame, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)
        # Note: Set the selector to indicate that this widget should not be
        #       colored differently from its parent when the 'Color layout managers'
        #       button is checked in the RSG Dialog Builder dialog.
        pickHf.setSelector(99)
        label = FXLabel(p=pickHf, text='Pick elements or nodes from the viewport' + ' (None)', ic=None, opts=LAYOUT_CENTER_Y|JUSTIFY_LEFT)
        pickHandler = XyplotDBPickHandler(form, form.keyword05Kw, 'Pick an element or nodes', NODES|ELEMENTS, ONE, label)
        icon = afxGetIcon('select', AFX_ICON_SMALL ) #箭头小标签
        self.button2=FXButton(p=pickHf, text='\tPick Items in Viewport', ic=icon, tgt=pickHandler, sel=AFXMode.ID_ACTIVATE,
            opts=BUTTON_NORMAL|LAYOUT_CENTER_Y, x=0, y=0, w=0, h=0, pl=2, pr=2, pt=1, pb=1)
        #鼠标选择按钮
        frame = FXHorizontalFrame(GroupBox_2, 0, 0,0,0,0, 0,0,0,0) #框架
        
        self.NODESETS=FXCheckButton(p=frame, 
            text='NODE SETS', tgt=form.NODESETSKw, sel=0)
        # ODB combo
        #
        self.RootComboBox_1 = AFXComboBox(p=frame, ncols=0, nvis=1, text='ODB:', tgt=form.ODBNameKw, sel=0)
        self.RootComboBox_1.setMaxVisible(10)
        msgCount = 325
        form.ODBNameKw.setTarget(self)
        form.ODBNameKw.setSelector(AFXDataDialog.ID_LAST+msgCount)
        msgHandler = str(self.__class__).split('.')[-1] + '.onNodesetsChanged'
        exec('FXMAPFUNC(self, SEL_COMMAND, AFXDataDialog.ID_LAST+%d, %s)' % (msgCount, msgHandler) )

        # Nodesets combo
        #
        self.ComboBox_1 = AFXComboBox(p=frame, ncols=0, nvis=1, text='Node set:', tgt=form.nodeSetNameKw, sel=0)
        self.ComboBox_1.setMaxVisible(10)

        self.form = form
        #框架大小
        frame = FXHorizontalFrame(GroupBox_2, 0, 0,0,0,0, 0,0,0,0) 
        
        # ODB combo
        #
        self.ELEMENTSETS=FXCheckButton(p=frame, 
            text='ELEMENT SETS', tgt=form.ELEMENTSETSKw, sel=0)
        self.RootComboBox_3 = AFXComboBox(p=frame, ncols=0, nvis=1, text='ODB:',tgt=form.odbNameKw, sel=0)
        self.RootComboBox_3.setMaxVisible(10)
        msgCount = 326
        form.odbNameKw.setTarget(self)
        form.odbNameKw.setSelector(AFXDataDialog.ID_LAST+msgCount)
        msgHandler = str(self.__class__).split('.')[-1] + '.onElementsetsChanged'
        exec('FXMAPFUNC(self, SEL_COMMAND, AFXDataDialog.ID_LAST+%d, %s)' % (msgCount, msgHandler) )

        # Elementsets combo
        #
        self.ComboBox_3 = AFXComboBox(p=frame, ncols=0, nvis=1, text='Element set:',tgt=form.elementSetNameKw, sel=0)
        self.ComboBox_3.setMaxVisible(10)



        


        self.form = form ##单选按钮组件
        GroupBox_1 = FXGroupBox(p=self, text='DATA_CAT', opts=FRAME_GROOVE|LAYOUT_FILL_X)
        FXRadioButton(p=GroupBox_1, text='RF', tgt=form.GroupBox1Kw1, sel=397)
        FXRadioButton(p=GroupBox_1, text='Mises', tgt=form.GroupBox1Kw1, sel=398)
        
        GroupBox_3 = FXGroupBox(p=self, text='Notice', opts=FRAME_GROOVE|LAYOUT_FILL_X)
        l = FXLabel(p=GroupBox_3, text='Extrach data from current datafield', opts=JUSTIFY_LEFT)
        l.setFont( getAFXFont(FONT_BOLD) ) 
        #标签组件
        l = FXLabel(p=GroupBox_3, text='[About me]:QQ943452349', opts=JUSTIFY_LEFT)

    
        # self.enable1=FXRadioButton(p=GroupBox_4, 
        #     text='Test enable', tgt=form.testenableKw, sel=402)

        # self.button1=FXButton(p=self, text='测试', ic=None, tgt=self, 
        #     sel=self.ID_Mybutton,
        #     opts=BUTTON_NORMAL,
        #     x=0, y=0, w=0, h=0, pl=0)              #自定义push button
        self.form=form

    def processUpdates(self):
    
        if self.form.NODESETSKw.getValue() == False:
    
               self.RootComboBox_1.disable()
               self.ComboBox_1.disable()
        else:
               self.RootComboBox_1.enable()
               self.ComboBox_1.enable()     

        if self.form.ELEMENTSETSKw.getValue() == False:
    
               self.RootComboBox_3.disable()
               self.ComboBox_3.disable()
        else:
               self.RootComboBox_3.enable()
               self.ComboBox_3.enable()
                 
        if self.form.PICKw.getValue() == False:
    
               self.button2.disable()
        else:
               self.button2.enable()
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

        self.form.ODBNameKw.setValue(self.currentOdbName)

        session.odbs.registerQuery(self.updateRootComboBox_1Odbs)

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

        session.odbs.registerQuery(self.updateRootComboBox_3Odbs)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def hide(self):

        AFXDataDialog.hide(self)

        session.odbs.unregisterQuery(self.updateRootComboBox_1Odbs)

        session.odbs.unregisterQuery(self.updateRootComboBox_3Odbs)

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
            if not self.form.ODBNameKw.getValue() in names:
                self.form.ODBNameKw.setValue( names[0] )
        else:
            self.form.ODBNameKw.setValue('')

        self.onNodesetsChanged(None, None, None)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onNodesetsChanged(self, sender, sel, ptr):

        odbName = self.form.ODBNameKw.getValue()

        # Update the names in the Nodesets combo
        #
        self.ComboBox_1.clearItems()
        if odbName:
            names = session.odbs[odbName].rootAssembly.nodeSets.keys()
            names.sort()
            for name in names:
                self.ComboBox_1.appendItem(name)

            if names:
                if not self.form.nodeSetNameKw.getValue() in names:
                    self.form.nodeSetNameKw.setValue( names[0] )
            else:
                self.form.nodeSetNameKw.setValue('')

        else:
            self.form.nodeSetNameKw.setValue('')

        self.resize( self.getDefaultWidth(), self.getDefaultHeight() )

        return 1

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateRootComboBox_3Odbs(self):

        # Update the names in the ODB combo
        #
        self.RootComboBox_3.clearItems()
        names = session.odbs.keys()
        names.sort()
        for name in names:
            self.RootComboBox_3.appendItem(name)

        if names:
            if not self.form.odbNameKw.getValue() in names:
                self.form.odbNameKw.setValue( names[0] )
        else:
            self.form.odbNameKw.setValue('')

        self.onElementsetsChanged(None, None, None)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onElementsetsChanged(self, sender, sel, ptr):

        odbName = self.form.odbNameKw.getValue()

        # Update the names in the Elementsets combo
        #
        self.ComboBox_3.clearItems()
        if odbName:
            names = session.odbs[odbName].rootAssembly.elementSets.keys()
            names.sort()
            for name in names:
                self.ComboBox_3.appendItem(name)

            if names:
                if not self.form.elementSetNameKw.getValue() in names:
                    self.form.elementSetNameKw.setValue( names[0] )
            else:
                self.form.elementSetNameKw.setValue('')

        else:
            self.form.elementSetNameKw.setValue('')

        self.resize( self.getDefaultWidth(), self.getDefaultHeight() )

        return 1



###########################################################################
# Class definition
###########################################################################

class XyplotDBPickHandler(AFXProcedure):

        count = 0

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        def __init__(self, form, keyword, prompt, entitiesToPick, numberToPick, label):

                self.form = form
                self.keyword = keyword
                self.prompt = prompt
                self.entitiesToPick = entitiesToPick # Enum value
                self.numberToPick = numberToPick # Enum value
                self.label = label
                self.labelText = label.getText()

                AFXProcedure.__init__(self, form.getOwner())

                XyplotDBPickHandler.count += 1
                self.setModeName('XyplotDBPickHandler%d' % (XyplotDBPickHandler.count) )
#pickHandler = XyplotDBPickHandler(form, form.keyword05Kw, 'Pick an element or nodes', NODES|ELEMENTS, ONE, label)
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        def getFirstStep(self):

                return  AFXPickStep(self, self.keyword, self.prompt, 
                    self.entitiesToPick, self.numberToPick, sequenceStyle=TUPLE)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        def getNextStep(self, previousStep):

                self.label.setText( self.labelText.replace('None', 'Picked') )
                return None

        def deactivate(self):

            AFXProcedure.deactivate(self)
            if  self.numberToPick == ONE and self.keyword.getValue() and self.keyword.getValue()[0]!='<':
                sendCommand(self.keyword.getSetupCommands() + '\nhighlight(%s)' % self.keyword.getValue() )

