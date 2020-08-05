import maya.cmds
import pymel.core
import os

##################
# HELPER METHODS #
##################

def createNewScene():
    """
    Creates a new scene.
    """
    # maya.cmds.file(new=True, force=True)
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
    # maya.cmds.file(filePath, r=True, ns=ns)
    pymel.core.createReference(filePath, namespace=ns)

def getJointsFromNamespace(ns):
    """
    Given a namespace, returns a list of all joints
    """
    return maya.cmds.ls("{0}:*".format(ns), type="joint")
    # return pymel.core.ls("{0}:*".format(ns), type="joint")

def applyParentConstraint(driver, driven):
    """
    Given a driver object (parent, aka the animation) and a driven 
    object (child, aka the rig to accept the animation), applies a 
    parent constraint.
    """
    # maya.cmds.parentConstraint(driver, driven, mo=True)
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

def saveFile(newFilePath):
    """
    Given a new file path, renames the current file and saves.
    """
    # maya.cmds.file(rename=newFilePath)
    # maya.cmds.file(save=True, f=True)
    pymel.core.saveAs(newFilePath)

def removeReference(filePathToRemove):
    """
    Removes the reference to the given file path.
    """
    maya.cmds.file(filePathToRemove, rr=True)

def applyAnimationForOneFile(animPath, destinationFolder):
    # animPath = "C:/Users/GoodbyeWorld Dev/Documents/Lucille/Tech for Anim/tech-art-exercises/week3/animations/AAA_0010_tk01.ma"
    rigPath = "C:/Users/GoodbyeWorld Dev/Documents/Lucille/Tech for Anim/tech-art-exercises/week3/character.mb"
    animNs = getFileNamespace(animPath)
    rigNs = getFileNamespace(rigPath)

    createNewScene()

    createReference(animPath, animNs)
    createReference(rigPath, rigNs)
    
    maya.cmds.select(cl=True)
    animJoints = getJointsFromNamespace(animNs)
    rigJoints = getJointsFromNamespace(rigNs)
    
    firstKeyframe = maya.cmds.findKeyframe(animJoints[0], which="first")
    maya.cmds.playbackOptions(animationStartTime=firstKeyframe, minTime=firstKeyframe)
    maya.cmds.currentTime(firstKeyframe)

    connectAnimAndRigJoints(animJoints, rigJoints)

    startTime = maya.cmds.playbackOptions(q=True, min=True)
    endTime = maya.cmds.playbackOptions(q=True, max=True)
    
    #maya.cmds.select(rigJoints)
    pymel.core.select(rigJoints)

    maya.cmds.bakeResults(
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

    removeReference(animPath)

    newFilePath = "{0}/rig_with_{1}.mb".format(destinationFolder, animNs)
    saveFile(newFilePath)

def applyAnimationForAllFilesInFolder(folder):
    destinationFolder = "C:/Users/GoodbyeWorld Dev/Documents/Lucille/Tech for Anim/tech-art-exercises/week2/finished-files/"
    if not os.path.exists(destinationFolder):
        os.mkdir(destinationFolder)
    animationFiles = [folder + fileName for fileName in os.listdir(folder)]
    for animationFile in animationFiles:
        applyAnimationForOneFile(animationFile, destinationFolder)

##########
# SCRIPT #
##########

def main():
    animationFolder = "C:/Users/GoodbyeWorld Dev/Documents/Lucille/Tech for Anim/tech-art-exercises/week3/animations/"
    applyAnimationForAllFilesInFolder(animationFolder)

if __name__ == "__main__":
    main()

