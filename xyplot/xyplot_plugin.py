# -* - coding:UTF-8 -*-
# Do not delete the following import lines
from abaqusGui import *
from abaqusConstants import ALL
import osutils, os


###########################################################################
# Class definition
###########################################################################

class Xyplot_plugin(AFXForm):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, owner):
        
        # Construct the base class.
        #
        AFXForm.__init__(self, owner)
        self.radioButtonGroups = {}

        self.cmd = AFXGuiCommand(mode=self, method='SSExtrac',
            objectName='xyplot', registerQuery=False)
        pickedDefault = ''
        self.keyword05Kw = AFXObjectKeyword(self.cmd, 'keyword05', TRUE, pickedDefault)

        self.ODBNameKw = AFXStringKeyword(self.cmd, 'ODBName', True)
        self.nodeSetNameKw = AFXStringKeyword(self.cmd, 'nodeSetName', True)

        self.odbNameKw = AFXStringKeyword(self.cmd, 'odbName', True)
        self.elementSetNameKw = AFXStringKeyword(self.cmd, 'elementSetName', True)

        if not self.radioButtonGroups.has_key('GroupBox1'):
            self.GroupBox1Kw1 = AFXIntKeyword(None, 'GroupBox1Dummy', True)
            self.GroupBox1Kw2 = AFXStringKeyword(self.cmd, 'GroupBox1', True)
            self.radioButtonGroups['GroupBox1'] = (self.GroupBox1Kw1, self.GroupBox1Kw2, {})
        self.radioButtonGroups['GroupBox1'][2][397] = 'RF' 
        # 按钮关键字RF
        if not self.radioButtonGroups.has_key('GroupBox1'):
            self.GroupBox1Kw1 = AFXIntKeyword(None, 'GroupBox1Dummy', True)
            self.GroupBox1Kw2 = AFXStringKeyword(self.cmd, 'GroupBox1', True)
            self.radioButtonGroups['GroupBox1'] = (self.GroupBox1Kw1, self.GroupBox1Kw2, {})
        self.radioButtonGroups['GroupBox1'][2][398] = 'Mises' 
        # 按钮关键字Mises




        ##测试用的

        self.PICKw = AFXBoolKeyword(self.cmd, 'PICK', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.NODESETSKw = AFXBoolKeyword(self.cmd, 'NODESETS', AFXBoolKeyword.TRUE_FALSE, True, True)
        self.ELEMENTSETSKw = AFXBoolKeyword(self.cmd, 'ELEMENTSETS', AFXBoolKeyword.TRUE_FALSE, True, False)
    
        #self.radiusKw = AFXFloatKeyword(self.cmd, 'radius', True)
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getFirstDialog(self):

        import xyplotDB
        return xyplotDB.XyplotDB(self)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def doCustomChecks(self):

        # Try to set the appropriate radio button on. If the user did
        # not specify any buttons to be on, do nothing.
        #
        for kw1,kw2,d in self.radioButtonGroups.values():
            try:
                value = d[ kw1.getValue() ]
                kw2.setValue(value)
            except:
                pass
        if self.GroupBox1Kw1.getValue()!=397 and self.GroupBox1Kw1.getValue()!=398:
            showAFXErrorDialog(getAFXApp().getAFXMainWindow(),'The radio buttton should be selected.')
        else:
            return True
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def okToCancel(self):

        # No need to close the dialog when a file operation (such
        # as New or Open) or model change is executed.
        #
        return False

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Register the plug-in
#
thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)

toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
toolset.registerGuiMenuButton(
    buttonText='xyplot', 
    object=Xyplot_plugin(toolset),
    messageId=AFXMode.ID_ACTIVATE,
    icon=None,
    kernelInitString='import xyplot',
    applicableModules=ALL,
    version='N/A',
    author='N/A',
    description='N/A',
    helpUrl='N/A'
)
