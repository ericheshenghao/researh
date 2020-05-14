from abaqusConstants import *
from abaqusGui import *
from kernelAccess import mdb, session
import os

thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)


###########################################################################
# Class definition
###########################################################################

class j_integral_allDB(AFXDataDialog):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form):

        # Construct the base class.
        # Construct a Dialog box. mode=form. title='J_Integeral'. three bottons here, OK, Apply and Cancel
        AFXDataDialog.__init__(self, form, 'J_integeral',
            self.OK|self.APPLY|self.CANCEL, DIALOG_ACTIONS_SEPARATOR)
            

        okBtn = self.getActionButton(self.ID_CLICKED_OK)
        okBtn.setText('OK')
            
        applyBtn = self.getActionButton(self.ID_CLICKED_APPLY)
        applyBtn.setText('Apply')



        # ======================================================"J Interal Parameters" Frame====================================
        GroupBox_1 = FXGroupBox(p=self, text='J Integral Parameters', opts=FRAME_GROOVE|LAYOUT_FILL_X)

        # ==============Control Bottom for Entering or Picking==============
        FXCheckButton(p=GroupBox_1, text='Enter parameter', tgt=form.enterKw, sel=0)
        HFrame_Int = FXHorizontalFrame(p=GroupBox_1, opts=0, x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0)
        VFrame_Int = FXHorizontalFrame(p=GroupBox_1, opts=0, x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0)



        # ==================When Entering is activated=======================
        # ===============Crack Tip Coordinates Enter Box=====================
        GroupBox_2 = FXGroupBox(p=HFrame_Int, text='Crack Tip Coordinates', opts=FRAME_GROOVE)
        VAligner_2 = AFXVerticalAligner(p=GroupBox_2, opts=0, x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0)
        self.xcentero = AFXTextField(p=VAligner_2, ncols=12, labelText='Crack Tip X:', tgt=form.xcenteroKw, sel=0)
        self.ycentero = AFXTextField(p=VAligner_2, ncols=12, labelText='Crack Tip Y:', tgt=form.ycenteroKw, sel=0)

        # ===============Crack Vertex Coordinates Enter Box==================
        GroupBox_3 = FXGroupBox(p=VFrame_Int, text='Crack Vertex Coordinates', opts=FRAME_GROOVE)
        VAligner_3 = AFXVerticalAligner(p=GroupBox_3, opts=0, x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0)
        self.xvertexo = AFXTextField(p=VAligner_3, ncols=12, labelText='Crack Vertex X:', tgt=form.xvertexoKw, sel=0)
        self.yvertexo = AFXTextField(p=VAligner_3, ncols=12, labelText='Crack Vertex Y:', tgt=form.yvertexoKw, sel=0)



        # ==================When Picking is activated========================
        # =============Crack Tip Coordinates Pick Botton=====================
        # Note: Set the selector to indicate that this widget should not be
        #       colored differently from its parent when the 'Color layout managers'
        #       button is checked in the RSG Dialog Builder dialog.
        GroupBox_4 = FXGroupBox(p=HFrame_Int, text='Integral Center Node', opts=FRAME_GROOVE|LAYOUT_FILL_Y)
        pickHf = FXHorizontalFrame(p=GroupBox_4, opts=0, x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0, hs=0, vs=0)
        pickHf.setSelector(99)
        label = FXLabel(p=pickHf, text='Select the Crack Tip Node' + ' (None)', ic=None, opts=LAYOUT_CENTER_Y|JUSTIFY_LEFT)
        pickHandler = j_integral_allDBPickHandler(form, form.centernodeKw, 'Pick a node', NODES, ONE, label)
        icon = afxGetIcon('select', AFX_ICON_SMALL )
        self.sel = FXButton(p=pickHf, text='\tPick Items in Viewport', ic=icon, tgt=pickHandler, sel=AFXMode.ID_ACTIVATE,
            opts=BUTTON_NORMAL|LAYOUT_CENTER_Y, x=0, y=0, w=0, h=0, pl=2, pr=2, pt=1, pb=1)

        # ===========Crack Vertex Coordinates Pick Botton====================
        GroupBox_5 = FXGroupBox(p=VFrame_Int, text='Crack Vertex Node', opts=FRAME_GROOVE|LAYOUT_FILL_Y)
        pickHf2 = FXHorizontalFrame(p=GroupBox_5, opts=0, x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0, hs=0, vs=0)
        pickHf2.setSelector(98)
        label2 = FXLabel(p=pickHf2, text='Select the Crack Vertex Node' + ' (None)', ic=None, opts=LAYOUT_CENTER_Y|JUSTIFY_LEFT)
        pickHandler2 = j_integral_allDBPickHandler(form, form.vertexnodeKw, 'Pick a node', NODES, ONE, label2)
        icon2 = afxGetIcon('select', AFX_ICON_SMALL )
        self.sel2 = FXButton(p=pickHf2, text='\tPick Items in Viewport', ic=icon2, tgt=pickHandler2, sel=AFXMode.ID_ACTIVATE,
            opts=BUTTON_NORMAL|LAYOUT_CENTER_Y, x=0, y=0, w=0, h=0, pl=2, pr=2, pt=1, pb=1)



        # ======================================================"Other Parameters" Frame========================================
        HFrame_Other = FXHorizontalFrame(p=self, opts=0, x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0)
        GroupBox_6 = FXGroupBox(p=HFrame_Other, text='Other Parameters', opts=FRAME_GROOVE|LAYOUT_FILL_Y)

        # ===========Problem Types: Plane stress or Plane strain=============
        VAligner_2 = AFXVerticalAligner(p=GroupBox_6, opts=0, x=0, y=0, w=0, h=0, pl=0, pr=0, pt=5, pb=0)
        ComboBox_1 = AFXComboBox(p=VAligner_2, ncols=0, nvis=1, text='type:', tgt=form.problemtypeKw, sel=0)
        ComboBox_1.setMaxVisible(10)
        ComboBox_1.appendItem(text='Plane stress')
        ComboBox_1.appendItem(text='Plane strain')

        # ===================== Integral Radius R_J =========================
        AFXTextField(p=VAligner_2, ncols=12, labelText='Integral Radius:', tgt=form.JrKw, sel=0)

        # ======================OBD File Selector============================
        fileHandler = j_integral_allDBFileHandler(form, 'fileName', '*.odb')
        fileTextHf = FXHorizontalFrame(p=VAligner_2, opts=0, x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)

        # Note: Set the selector to indicate that this widget should not be
        #       colored differently from its parent when the 'Color layout managers'
        #       button is checked in the RSG Dialog Builder dialog.
        # ===========File Selector Options==============
        fileTextHf.setSelector(99)
        AFXTextField(p=fileTextHf, ncols=12, labelText='.OBD File:', tgt=form.fileNameKw, sel=0, opts=AFXTEXTFIELD_STRING|LAYOUT_CENTER_Y)
        icon3 = afxGetIcon('fileOpen', AFX_ICON_SMALL )
        FXButton(p=fileTextHf, text='	Select File From Dialog', ic=icon3, tgt=fileHandler, sel=AFXMode.ID_ACTIVATE, opts=BUTTON_NORMAL|LAYOUT_CENTER_Y, x=0, y=0, w=0, h=0, pl=1, pr=1, pt=1, pb=1)

        # ==========================Step Index=============================
        VAligner_2 = AFXVerticalAligner(p=GroupBox_6, opts=0, x=0, y=0, w=0, h=0, pl=0, pr=0, pt=5, pb=0)
        AFXTextField(p=VAligner_2, ncols=12, labelText='Step Index:', tgt=form.StepIndexKw, sel=0)

        # ==========================Total Frames=============================
        VAligner_2 = AFXVerticalAligner(p=GroupBox_6, opts=0, x=0, y=0, w=0, h=0, pl=0, pr=0, pt=5, pb=0)
        AFXTextField(p=VAligner_2, ncols=12, labelText='Total Frames:', tgt=form.TotalFramesKw, sel=0)



        # ================================================Sketch Picture Frame==================================================
        HFrame_Picture = FXHorizontalFrame(p=HFrame_Other, opts=0, x=0, y=0, w=0, h=0, pl=3, pr=0, pt=0, pb=0)
        fileName = os.path.join(thisDir, 'J_integral.png')
        icon4 = afxCreatePNGIcon(fileName)
        FXLabel(p=HFrame_Picture, text='', ic=icon4)

        self.form = form
        # =============================================================
        self.addTransition(form.enterKw,AFXTransition.EQ,
            True,self.xcentero,
            MKUINT(FXWindow.ID_ENABLE,SEL_COMMAND),None)
        self.addTransition(form.enterKw,AFXTransition.EQ,
            False,self.xcentero,
            MKUINT(FXWindow.ID_DISABLE,SEL_COMMAND),None)

        self.addTransition(form.enterKw,AFXTransition.EQ,
            True,self.ycentero,
            MKUINT(FXWindow.ID_ENABLE,SEL_COMMAND),None)
        self.addTransition(form.enterKw,AFXTransition.EQ,
            False,self.ycentero,
            MKUINT(FXWindow.ID_DISABLE,SEL_COMMAND),None) 

        # =============================================================
        self.addTransition(form.enterKw,AFXTransition.EQ,
            True,self.xvertexo,
            MKUINT(FXWindow.ID_ENABLE,SEL_COMMAND),None)
        self.addTransition(form.enterKw,AFXTransition.EQ,
            False,self.xvertexo,
            MKUINT(FXWindow.ID_DISABLE,SEL_COMMAND),None)

        self.addTransition(form.enterKw,AFXTransition.EQ,
            True,self.yvertexo,
            MKUINT(FXWindow.ID_ENABLE,SEL_COMMAND),None)
        self.addTransition(form.enterKw,AFXTransition.EQ,
            False,self.yvertexo,
            MKUINT(FXWindow.ID_DISABLE,SEL_COMMAND),None) 

        # =============================================================
        self.addTransition(form.enterKw,AFXTransition.EQ,
            True,self.sel,
            MKUINT(FXWindow.ID_DISABLE,SEL_COMMAND),None) 
        self.addTransition(form.enterKw,AFXTransition.EQ,
            False,self.sel,
            MKUINT(FXWindow.ID_ENABLE,SEL_COMMAND),None) 

        # =============================================================
        self.addTransition(form.enterKw,AFXTransition.EQ,
            True,self.sel2,
            MKUINT(FXWindow.ID_DISABLE,SEL_COMMAND),None) 
        self.addTransition(form.enterKw,AFXTransition.EQ,
            False,self.sel2,
            MKUINT(FXWindow.ID_ENABLE,SEL_COMMAND),None) 

###########################################################################
# Class definition
###########################################################################

class j_integral_allDBPickHandler(AFXProcedure):

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

                j_integral_allDBPickHandler.count += 1
                self.setModeName('j_integral_allDBPickHandler%d' % (j_integral_allDBPickHandler.count) )

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        def getFirstStep(self):

                return  AFXPickStep(self, self.keyword, self.prompt, 
                    self.entitiesToPick, self.numberToPick, sequenceStyle=TUPLE)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        def getNextStep(self, previousStep):

                self.label.setText( self.labelText.replace('None', 'Picked') )
                return None
                self.label2.setText( self.labelText.replace('None', 'Picked') )
                return None


###########################################################################
# Class definition
###########################################################################

class j_integral_allDBFileHandler(FXObject):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form, keyword, patterns='*'):

        self.form = form
        self.patterns = patterns
        self.patternTgt = AFXIntTarget(0)
        exec('self.fileNameKw = form.%sKw' % keyword)
        self.readOnlyKw = AFXBoolKeyword(None, 'readOnly', AFXBoolKeyword.TRUE_FALSE)
        FXObject.__init__(self)
        FXMAPFUNC(self, SEL_COMMAND, AFXMode.ID_ACTIVATE, j_integral_allDBFileHandler.activate)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def activate(self, sender, sel, ptr):

       fileDb = AFXFileSelectorDialog(getAFXApp().getAFXMainWindow(), 'Select a File',
           self.fileNameKw, self.readOnlyKw,
           AFXSELECTFILE_ANY, self.patterns, self.patternTgt)
       fileDb.setReadOnlyPatterns('*.odb')
       fileDb.create()
       fileDb.showModal()
