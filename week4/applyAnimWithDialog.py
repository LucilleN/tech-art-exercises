import pymel.core
import os

##################
# HELPER METHODS #
##################

def createNewScene():
    """
    Creates a new scene.
    """
    pymel.core.newFile(force=True)

def getFileNamespace(filePath):
    """
    Given a file path, returns the file name without the 
    extension, which we will use as the namespace
    """
    if not os.path.exists(filePath):
        pymel.core.error("File does not exist: {0}".format(filePath))
        return
    fileDirectory, fileFullName = os.path.split(filePath)
    fileName, fileExt = os.path.splitext(fileFullName)
    return "{0}".format(fileName)

def createReference(filePath, ns):
    """
    Given a file path and a namespace, creates a reference to
    that file.
    """
    if not os.path.exists(filePath):
        pymel.core.error("File does not exist: {0}".format(filePath))
        return
    pymel.core.createReference(filePath, namespace=ns)
    refNode = pymel.core.FileReference(namespace=ns)
    return refNode

def getJointsFromNamespace(ns):
    """
    Given a namespace, returns a list of all joints
    """
    return pymel.core.ls("{0}:*".format(ns), type="joint")

def applyParentConstraint(driver, driven):
    """
    Given a driver object (parent, aka the animation) and a driven 
    object (child, aka the rig to accept the animation), applies a 
    parent constraint.
    """
    pymel.core.parentConstraint(driver, driven, mo=True)

def connectAnimAndRigJoints(animJoints, rigJoints):
    """
    Given a list of animation joints and a list of rig joints,
    connects each pair of joints with translate, rotate, and
    scale. Note: animJoints and rigJoints should follow the 
    exact same hierarchy.
    """
    for animJoint in animJoints:
        animJointName = animJoint.split(":")[1]
        for rigJoint in rigJoints:
            rigJointName = rigJoint.split(":")[1]
            if animJointName == rigJointName:
                applyParentConstraint(animJoint, rigJoint)
                break

def saveFile(tempFilePath, newFilePath):
    """
    Given a new file path, renames the current file and saves.
    """
    pymel.core.saveAs(newFilePath)

    # Again, this was an attempt to stop the student license popup, and it successfully
    # removes the student license line from the .ma file, but it doesn't stop the 
    # popup from appearing lol damnit

    # pymel.core.saveAs(tempFilePath)
    # removeStudentLicenseLine(tempFilePath, newFilePath)

def removeReference(refNode):
    """
    Removes the reference represented by the given refNode.
    """
    refNode.remove()

def removeStudentLicenseLine(tempFilePath, finalFilePath):
    """
    Removes the Student License line from the given Maya ASCII file (Note: only works 
    for .ma files, not .mb). This doesn't do anything to help with the popups that come up in this script, but if we were to open up the files we produce, the student
    license popup should be suppressed. 
    """
    with open(tempFilePath, "r") as input:
        with open(finalFilePath, "w") as output: 
            for line in input:
                if line.strip("\n") != r'fileInfo "license" "student";':
                    output.write(line)
    os.remove(tempFilePath)

def applyAnimationForOneFile(animPath, destinationFolder, rigPath):
    """
    Given the path of an animation file, a rig file, and a destination folder, 
    applies the animation to the rig using references and parent constraints
    and saves the resulting file to the destination folder using the name
    rig_with_{animation file name}.ma .
    """
    animNs = getFileNamespace(animPath)
    rigNs = getFileNamespace(rigPath)

    createNewScene()

    animRefNode = createReference(animPath, animNs)
    rigRefNode = createReference(rigPath, rigNs)
    
    pymel.core.select(cl=True)
    animJoints = getJointsFromNamespace(animNs)
    rigJoints = getJointsFromNamespace(rigNs)
    
    firstKeyframe = pymel.core.findKeyframe(animJoints[0], which="first")
    pymel.core.playbackOptions(animationStartTime=firstKeyframe, minTime=firstKeyframe)
    pymel.core.currentTime(firstKeyframe)

    connectAnimAndRigJoints(animJoints, rigJoints)

    startTime = pymel.core.playbackOptions(q=True, min=True)
    endTime = pymel.core.playbackOptions(q=True, max=True)
    
    pymel.core.select(rigJoints)

    pymel.core.bakeResults(
        simulation = True,
        time = (startTime, endTime),
        sampleBy = 1,
        oversamplingRate = 1,
        disableImplicitControl = True,
        preserveOutsideKeys = True,
        sparseAnimCurveBake = False,
        removeBakedAnimFromLayer = False,
        bakeOnOverrideLayer = False,
        minimizeRotation = True,
        controlPoints = False,
        shape = True
    )

    removeReference(animRefNode)

    # this was an attempt to get rid of the student license popup, and it successfully
    # removes the license line, but it doesn't stop the popup lol
    tempFilePath = "{0}/temp.ma".format(destinationFolder) 
    finalFilePath = "{0}/rig_with_{1}.ma".format(destinationFolder, animNs)
    saveFile(tempFilePath, finalFilePath)

def applyAnimationForAllFilesInFolder(animFolder, destFolder, rigPath):
    """
    Given the path of a folder of animation files and the path of a rig file, 
    applies each animation to the given rig one by one and saves each one to the 
    destination folder.
    """
    if not os.path.exists(destFolder):
        os.mkdir(destFolder)
    animationFiles = [animFolder + fileName for fileName in os.listdir(animFolder)]
    for animationFile in animationFiles:
        applyAnimationForOneFile(animationFile, destFolder, rigPath)
        # break # uncomment to run only one loop interation for easier testing

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

