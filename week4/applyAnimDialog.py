from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtUiTools
from shiboken2 import wrapInstance
import maya.OpenMayaUI
from applyAnimWithDialog import * 

############
# UI CLASS #
############

class ApplyAndSaveAnimDialog(QtWidgets.QDialog):

    def __init__(self):
        mayaMain = self.get_maya_window()
        super(ApplyAndSaveAnimDialog, self).__init__(mayaMain)

        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setModal(False)

        self.setWindowTitle("Apply And Save Animations")

        self.setMinimumWidth(600)
        self.setMinimumHeight(200)

        self.createWidgets()
        self.createLayouts()
        self.createConnections()

    def get_maya_window(self):
        mainWindowPtr = maya.OpenMayaUI.MQtUtil.mainWindow()
        return wrapInstance(long(mainWindowPtr), QtWidgets.QWidget)

    def createConnections(self):
        self.animDirPathBtn.clicked.connect(self.browseAnimDirPath)
        self.rigFilePathBtn.clicked.connect(self.browseRigFilePath)
        self.destDirPathBtn.clicked.connect(self.browseDestDirPath)
        self.runBtn.clicked.connect(self.runApplyAnimScript)

    def createLayouts(self):

        mainLayout = QtWidgets.QVBoxLayout(self)
        animDirLayout = QtWidgets.QHBoxLayout(self)
        rigFileLayout = QtWidgets.QHBoxLayout(self)
        destDirLayout = QtWidgets.QHBoxLayout(self)

        animDirLayout.addWidget(self.animDirPathText)
        animDirLayout.addWidget(self.animDirPathLineEdit)
        animDirLayout.addWidget(self.animDirPathBtn)
        
        rigFileLayout.addWidget(self.rigFilePathText)
        rigFileLayout.addWidget(self.rigFilePathLineEdit)
        rigFileLayout.addWidget(self.rigFilePathBtn)
        
        destDirLayout.addWidget(self.destDirPathText)
        destDirLayout.addWidget(self.destDirPathLineEdit)
        destDirLayout.addWidget(self.destDirPathBtn)

        mainLayout.addWidget(self.titleText)
        mainLayout.addLayout(animDirLayout)
        mainLayout.addLayout(rigFileLayout)
        mainLayout.addLayout(destDirLayout)
        mainLayout.addWidget(self.runBtn)

    def createWidgets(self):

        self.titleText = QtWidgets.QLabel()
        self.titleText.setAlignment(QtCore.Qt.AlignHCenter)
        self.titleText.setText("Apply and Save Out Animations on Selected Rig")

        self.animDirPathText = QtWidgets.QLabel()
        self.animDirPathText.setText("Animation Folder Path")
        self.animDirPathLineEdit = QtWidgets.QLineEdit()
        self.animDirPathBtn = QtWidgets.QPushButton()
        self.animDirPathBtn.setIcon(QtGui.QIcon(":fileOpen.png"))

        self.rigFilePathText = QtWidgets.QLabel()
        self.rigFilePathText.setText("Rig File Path")
        self.rigFilePathLineEdit = QtWidgets.QLineEdit()
        self.rigFilePathBtn = QtWidgets.QPushButton()
        self.rigFilePathBtn.setIcon(QtGui.QIcon(":fileOpen.png"))

        self.destDirPathText = QtWidgets.QLabel()
        self.destDirPathText.setText("Destination Folder Path")
        self.destDirPathLineEdit = QtWidgets.QLineEdit()
        self.destDirPathBtn = QtWidgets.QPushButton()
        self.destDirPathBtn.setIcon(QtGui.QIcon(":fileOpen.png"))

        self.runBtn = QtWidgets.QPushButton("Run")

    def browseAnimDirPath(self):
        selectedPath = QtWidgets.QFileDialog.getExistingDirectory(self)
        if selectedPath:
            self.animDirPathLineEdit.setText(selectedPath)

    def browseRigFilePath(self):
        selectedPath = QtWidgets.QFileDialog.getOpenFileName(self)[0]
        if selectedPath:
            self.rigFilePathLineEdit.setText(selectedPath)

    def browseDestDirPath(self):
        selectedPath = QtWidgets.QFileDialog.getExistingDirectory(self)
        if selectedPath:
            self.destDirPathLineEdit.setText(selectedPath)

    def runApplyAnimScript(self):
        animDirPath = self.animDirPathLineEdit.text().replace("\\", "/") + "/"
        rigFilePath = self.rigFilePathLineEdit.text().replace("\\", "/")
        destDirPath = self.destDirPathLineEdit.text().replace("\\", "/") + "/"

        if not animDirPath or not rigFilePath or not destDirPath:
            pymel.core.error("Invalid file path")
            return

        applyAnimationForAllFilesInFolder(animDirPath, destDirPath, rigFilePath)
        self.close()

##########
# SCRIPT #
##########

def main():
    try:
        anim_dialog.delete()
    except:
        pass

    animDialog = ApplyAndSaveAnimDialog()
    animDialog.show()

if __name__ == "__main__":
    main()

