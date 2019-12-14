from abaqusGui import *
from abaqusConstants import ALL
import osutils, os


###########################################################################
# Class definition
###########################################################################

class _rsgTmp322_Form(AFXForm):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, owner):
        
        # Construct the base class.
        #
        AFXForm.__init__(self, owner)
        self.radioButtonGroups = {}

        self.cmd = AFXGuiCommand(mode=self, method='Fibre_insert',
            objectName='Fibre_insert', registerQuery=False)
        pickedDefault = ''
        self.uel_modeKw = AFXBoolKeyword(self.cmd, 'uel_mode', AFXBoolKeyword.TRUE_FALSE, True, False)
        self.modelNameKw = AFXStringKeyword(self.cmd, 'modelName', True)
        self.partNameKw = AFXStringKeyword(self.cmd, 'partName', True)
        self.variableKw = AFXObjectKeyword(self.cmd, 'variable', TRUE, pickedDefault)
        self.concreteKw = AFXStringKeyword(self.cmd, 'concrete', True, 'C25')
        self.thicknessKw = AFXFloatKeyword(self.cmd, 'thickness', True, 50)
        self.diameterKw = AFXStringKeyword(self.cmd, 'diameter', True, '0.2')

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getFirstDialog(self):

        import _rsgTmp322_DB
        return _rsgTmp322_DB._rsgTmp322_DB(self)

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
    def deactivate(self):
    
        try:
            osutils.remove(os.path.join('c:\\Users\\Hasee\\abaqus_plugins\\Fibre_insert', '_rsgTmp322_DB.py'), force=True )
            osutils.remove(os.path.join('c:\\Users\\Hasee\\abaqus_plugins\\Fibre_insert', '_rsgTmp322_DB.pyc'), force=True )
        except:
            pass
        try:
            osutils.remove(os.path.join('c:\\Users\\Hasee\\abaqus_plugins\\Fibre_insert', '_rsgTmp322_Form.py'), force=True )
            osutils.remove(os.path.join('c:\\Users\\Hasee\\abaqus_plugins\\Fibre_insert', '_rsgTmp322_Form.pyc'), force=True )
        except:
            pass
        AFXForm.deactivate(self)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getCommandString(self):

        cmds = 'import Fibre_insert\n'
        cmds += AFXForm.getCommandString(self)
        return cmds

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def okToCancel(self):

        # No need to close the dialog when a file operation (such
        # as New or Open) or model change is executed.
        #
        return False
