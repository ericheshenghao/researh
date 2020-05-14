from abaqusGui import *
from abaqusConstants import ALL
import osutils, os


###########################################################################
# Class definition
###########################################################################

class j_integral_all_plugin(AFXForm):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, owner):
        
        # Construct the base class.
        #
        AFXForm.__init__(self, owner)
        self.radioButtonGroups = {}

        self.cmd = AFXGuiCommand(mode=self, method='main_Jintegral',
            objectName='J_K_3', registerQuery=False)
        pickedDefault = ''
        self.enterKw = AFXBoolKeyword(self.cmd, 'enter', AFXBoolKeyword.TRUE_FALSE, True, True)
        self.xcenteroKw = AFXFloatKeyword(self.cmd, 'xcentero', True, 20)
        self.ycenteroKw = AFXFloatKeyword(self.cmd, 'ycentero', True, 0)

        self.xvertexoKw = AFXFloatKeyword(self.cmd, 'xvertexo', True, 0)
        self.yvertexoKw = AFXFloatKeyword(self.cmd, 'yvertexo', True, 0)

        self.centernodeKw = AFXObjectKeyword(self.cmd, 'centernode', TRUE, pickedDefault)

        self.vertexnodeKw = AFXObjectKeyword(self.cmd, 'vertexnode', TRUE, pickedDefault)

        self.problemtypeKw = AFXStringKeyword(self.cmd, 'problemtype', True, 'Plane stress')
        self.JrKw = AFXFloatKeyword(self.cmd, 'Jr', True, 5)
        self.fileNameKw = AFXStringKeyword(self.cmd, 'fileName', True, 'Job-1.odb')
        self.StepIndexKw = AFXFloatKeyword(self.cmd, 'StepIndex', True, 0)
        self.TotalFramesKw = AFXFloatKeyword(self.cmd, 'TotalFrames', True, -1)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getFirstDialog(self):

        import j_integral_allDB
        return j_integral_allDB.j_integral_allDB(self)

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
    buttonText='j_integral_all', 
    object=j_integral_all_plugin(toolset),
    messageId=AFXMode.ID_ACTIVATE,
    icon=None,
    kernelInitString='import J_K_3',
    applicableModules=ALL,
    version='2.0',
    author='Canate',
    description='This is a plug-in to calculate the Stress Intensity Factors (K, KI and KII) based on J-Integral and Interaction Integral of 2-D crack\n\
    Limitation: 2-D \
                Quadrilateral element',
    helpUrl='NONE'
)
