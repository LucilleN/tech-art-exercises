import maya.cmds
import os

##################
# HELPER METHODS #
##################

def createNewScene():
    """
    Creates a new scene.
    """
    maya.cmds.file(new=True, force=True)

def getFileNamespace(filePath):
    """
    Given a file path, returns the file name without the 
    extension, which we will use as the namespace
    """
    if not os.path.exists(filePath):
        maya.cmds.error("File does not exist: {0}".format(filePath))
        return
    fileDirectory, fileFullName = os.path.split(filePath)
    fileName, fileExt = os.path.splitext(fileFullName)
    return "ns_{0}".format(fileName)

def createReference(filePath, ns):
    """
    Given a file path and a namespace, creates a reference to
    that file.
    """
    if not os.path.exists(filePath):
        maya.cmds.error("File does not exist: {0}".format(filePath))
        return
    maya.cmds.file(filePath, r=True, ns=ns)

def getJointsFromNamespace(ns):
    """
    Given a namespace, returns a list of all joints
    """
    return maya.cmds.ls("{0}:*".format(ns), type="joint")

def connectSingleAttribute(src, dest, attr):
    """
    Given a source object, a destination object, and an 
    attribute, connects the attribute of the src and dest.
    """
    srcString = "{0}.{1}".format(src, attr)
    destString = "{0}.{1}".format(dest, attr)
    maya.cmds.connectAttr(srcString, destString, f=True)

def connectTranslateRotateScale(src, dest):
    """
    Given a source object and destination object, connects 
    all translation, rotation, and scale attributes.
    """
    attributes = [
        "translateX", 
        "translateY",
        "translateZ",
        "rotateX",
        "rotateY",
        "rotateZ",
        "scaleX",
        "scaleY",
        "scaleZ"
    ]
    for attribute in attributes:
        connectSingleAttribute(src, dest, attribute)

def applyParentConstraint(driver, driven):
    """
    Given a driver object (parent, aka the animation) and a driven 
    object (child, aka the rig to accept the animation), applies a 
    parent constraint.
    """
    maya.cmds.parentConstraint(driver, driven, mo=True)

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
                # connectTranslateRotateScale(animJoint, rigJoint)
                applyParentConstraint(animJoint, rigJoint)
                break

def saveFile(newFilePath):
    """
    Given a new file path, renames the current file and saves.
    """
    maya.cmds.file(rename=newFilePath)
    maya.cmds.file(save=True, f=True)

def removeReference(filePathToRemove):
    """
    Removes the reference to the given file path.
    """
    maya.cmds.file(filePathToRemove, rr=True)

##########
# SCRIPT #
##########

def main():
    animPath = r'C:\Users\GoodbyeWorld Dev\Documents\Lucille\Tech for Anim\tech-art-exercises\week2\animations\maya\01_01.ma'.replace("\\", "/")
    rigPath = r'C:\Users\GoodbyeWorld Dev\Documents\Lucille\Tech for Anim\tech-art-exercises\week2\character.mb'.replace("\\", "/")
    animNs = getFileNamespace(animPath)
    rigNs = getFileNamespace(rigPath)
    
    # maya.cmds.file(animPath, o=True, f=True)
    # firstKeyframe = maya.cmds.findKeyframe(which="first")
    
    # print("???")
    createNewScene()
    # print("FUCK ME")
    # print(firstKeyframe)

    createReference(animPath, animNs)
    createReference(rigPath, rigNs)
    
    maya.cmds.select(cl=True)
    animJoints = getJointsFromNamespace(animNs)
    # maya.cmds.select(animJoints)
    rigJoints = getJointsFromNamespace(rigNs)
    
    firstKeyframe = maya.cmds.findKeyframe(animJoints[0], which="first")
    maya.cmds.playbackOptions(animationStartTime=firstKeyframe, minTime=firstKeyframe)
    maya.cmds.currentTime(firstKeyframe)

    connectAnimAndRigJoints(animJoints, rigJoints)

    startTime = maya.cmds.playbackOptions(q=True, min=True)
    endTime = maya.cmds.playbackOptions(q=True, max=True)
    
    maya.cmds.select(rigJoints)

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

    newFilePath = r'C:\Users\GoodbyeWorld Dev\Documents\Lucille\Tech for Anim\tech-art-exercises\week2\assignment.mb'.replace("\\", "/")
    saveFile(newFilePath)

if __name__ == "__main__":
    main()

