'''
Usage - run this code

import exportAnimation

try:

    # If there is, delete it
    anim_dialog.delete()

except:

    pass

# Create a new progress bar GUI
anim_dialog = exportAnimation.ExportAnimDialog()

anim_dialog.show()


Select a root bone node, select a file path, and hit run. This will export fbx animation Z up file for Unreal
'''

import pymel.core
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtUiTools
from shiboken2 import wrapInstance
import maya.OpenMayaUI

def export_anim(root, export_file_path):

    # select the root node and all the children
    # hi -> select all children in hierarchy
    # add -> add to list of selected items without removing what's already selected
    pymel.core.select(root, hi = True, add = True)

    # get start frame and end frame
    start = int(pymel.core.playbackOptions(q = True, min = True))
    end = int(pymel.core.playbackOptions(q = True, max = True))

    # load a plugin to export an fbx maybe?
    pymel.core.loadPlugin('fbxmaya.mll', quiet = True)
    # a shit ton of export settings probably
    pymel.core.mel.FBXResetExport()
    pymel.core.mel.FBXExportInAscii(v = True)
    pymel.core.mel.FBXExportUpAxis("z")
    pymel.core.mel.FBXExportAnimationOnly(v = False)
    pymel.core.mel.FBXExportBakeComplexAnimation(v = True)
    pymel.core.mel.FBXExportBakeComplexStart(v = start)
    pymel.core.mel.FBXExportBakeComplexEnd(v = end)
    pymel.core.mel.FBXExportBakeResampleAnimation(v = True)
    pymel.core.mel.FBXExport(s = True, f = export_file_path)

# returns maya window so that we can make a dialog inside of it
def get_maya_window():

    mainWindowPtr = maya.OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(long(mainWindowPtr), QtWidgets.QWidget)

class ExportAnimDialog(QtWidgets.QDialog):
    
    # constructor
    def __init__(self):

        maya_main = get_maya_window()

        # call superclass constructor (QtWidgets.QDialog)
        super(ExportAnimDialog, self).__init__(maya_main)

        # ?????
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        # it's not a Modal, no idea what that means
        self.setModal(False)

        # title at top of dialog
        self.setWindowTitle("Export Animation")

        # width height 
        self.setMinimumWidth(400)
        self.setMinimumHeight(100)

        # make all the widgets
        self.createWidgets()
        # put widgets into layouts
        self.createLayouts()
        # connect shit
        self.createConnections()

    def createConnections(self):

        # the function to call when we click nodeBtn is the getSelected method
        self.nodeBtn.clicked.connect(self.getSelected)
        # etc.
        self.fileBtn.clicked.connect(self.browseFile)
        # etc.
        self.runBtn.clicked.connect(self.runExport)

    def createLayouts(self):

        mainLayout = QtWidgets.QVBoxLayout(self)
        # each row in the thing is a Horizontal box
        nodeLayout = QtWidgets.QHBoxLayout(self)
        # horizontal box again
        fileNameLayout = QtWidgets.QHBoxLayout(self)
        # this last one is a Form layout because I guess you can 
        formLayout = QtWidgets.QFormLayout(self)

        # add all the shit to the sub-layouts
        nodeLayout.addWidget(self.nodeText)
        nodeLayout.addWidget(self.nodeLineEdit)
        nodeLayout.addWidget(self.nodeBtn)

        fileNameLayout.addWidget(self.fileText)
        fileNameLayout.addWidget(self.fileLineEdit)
        fileNameLayout.addWidget(self.fileBtn)

        # add all the shit to main layout
        mainLayout.addWidget(self.titleText)
        mainLayout.addLayout(nodeLayout)
        mainLayout.addLayout(fileNameLayout)
        mainLayout.addWidget(self.runBtn)

    def createWidgets(self):

        self.titleText = QtWidgets.QLabel()
        self.titleText.setAlignment(QtCore.Qt.AlignHCenter)
        self.titleText.setText("Export Animation of Selected Rig")

        self.nodeText = QtWidgets.QLabel()
        self.nodeText.setText("Root Node")
        self.nodeLineEdit = QtWidgets.QLineEdit()
        self.nodeBtn = QtWidgets.QPushButton("<<")

        self.fileText = QtWidgets.QLabel()
        self.fileText.setText("File Path")
        self.fileLineEdit = QtWidgets.QLineEdit()
        self.fileBtn = QtWidgets.QPushButton()
        self.fileBtn.setIcon(QtGui.QIcon(":fileOpen.png"))

        self.runBtn = QtWidgets.QPushButton("Run")

    def browseFile(self):

        fbxFile = QtWidgets.QFileDialog.getSaveFileName(self, "Save FBX File", None, "FBX Files (*.fbx)")

        if fbxFile[0]:

            self.fileLineEdit.setText(fbxFile[0])

    def getSelected(self):

        if not pymel.core.selected():

            self.nodeLineEdit.setText("")

            return

        item = pymel.core.selected()[0]

        self.nodeLineEdit.setText(item.name())

    def runExport(self):

        nodeName = self.nodeLineEdit.text()

        file_path = self.fileLineEdit.text().replace("\\", "/")

        if not file_path:

            pymel.core.error("Unacceptable file path")

            return

        if not nodeName:

            pymel.core.error("No Node submitted")

            return

        try:

            node = pymel.core.PyNode(nodeName)

        except:

            pymel.core.error("Node does not exist")

            return

        export_anim(node, file_path)
        self.close()